#include "live.h"

#include <ArduinoJson.h>
#include <M5Unified.h>
#include <WebSocketsClient.h>
#include <WiFi.h>
#include <stdio.h>
#include <string.h>

#include "../core/settings.h"
#include "../core/sys.h"
#include "limiter.h"
#include "voice.h"

namespace maz {
namespace live {

namespace {

constexpr uint32_t kRate      = voice::SAMPLE_RATE;  // 16 kHz both ways: no resampling
constexpr size_t   kFrame     = 640;                 // mic frame, 40 ms
constexpr size_t   kBlock     = 1024;                // playback block, 64 ms; two queued
constexpr size_t   kRingBytes = 16384;               // 512 ms of reply audio
constexpr size_t   kPreBytes  = 4800;                // start playing at 150 ms buffered
constexpr size_t   kFade      = 80;                  // 5 ms
constexpr uint32_t kQuietMs   = 120;                 // no frame for this long = Core paused/finished
constexpr uint8_t  kCh        = 1;                   // voice.cpp owns channel 0

struct Bufs {
    int16_t mic[2][kFrame];
    int16_t play[2][kBlock];
    int16_t ramp[kFade];
    uint8_t ring[kRingBytes];
};

enum class Mode : uint8_t { None, Mic, Spk };

WebSocketsClient gWs;
Bufs*   gB     = nullptr;
Phase   gPhase = Phase::Off;
Mode    gMode  = Mode::None;
char    gErr[64];
char    gAuth[200];
float   gLevel = 0.f;
uint32_t gConnSince = 0;  // when we last started waiting for Core
bool     gNeedMic = false;  // switch to mic pending (retried from update())
uint8_t  gMicTries = 0;
uint32_t gNextTry = 0;

// mic
uint8_t gMicIdx = 0;
bool    gMicQueued = false;

// reply ring + playback
size_t   gHead = 0, gTail = 0, gCount = 0;
uint8_t  gPlayIdx = 0;
bool     gPrebuf = true;     // wait for kPreBytes before (re)starting
bool     gFadeIn = false;
bool     gNeedRamp = false;  // speaker was fed audio that did not end at zero
bool     gPlayed = false;    // something was played since the last playback_done
bool     gWantListen = false;
int16_t  gLast = 0;
uint32_t gLastFrameMs = 0;

void ringClear() { gHead = gTail = gCount = 0; }

void ringPush(const uint8_t* d, size_t n) {
    n &= ~(size_t)1;
    if (n > kRingBytes - gCount) n = (kRingBytes - gCount) & ~(size_t)1;  // Core paces; overflow = drop
    for (size_t i = 0; i < n; ++i) {
        gB->ring[gHead] = d[i];
        gHead = (gHead + 1) % kRingBytes;
    }
    gCount += n;
}

void ringPop(uint8_t* d, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        d[i] = gB->ring[gTail];
        gTail = (gTail + 1) % kRingBytes;
    }
    gCount -= n;
}

void sendType(const char* type) {
    char b[48];
    snprintf(b, sizeof(b), "{\"type\":\"%s\"}", type);
    gWs.sendTXT(b);
}

void setErr(const char* m) { snprintf(gErr, sizeof(gErr), "%s", m); }

bool toMic() {
    gMicIdx = 0;
    gMicQueued = false;
    gWantListen = false;
    if (!voice::useMic()) {
        setErr("mic did not start");
        gMode = Mode::None;
        return false;
    }
    gMode = Mode::Mic;
    gPhase = Phase::Listening;
    gErr[0] = 0;  // a retry succeeded
    return true;
}

void wantMic() {
    gNeedMic = true;
    gMicTries = 0;
    gNextTry = 0;
    gWantListen = false;
}

void toSpeaker() {
    gMode = Mode::Spk;
    ringClear();
    gPrebuf = true;
    gFadeIn = false;
    gNeedRamp = false;
    gPlayed = false;
    gLast = 0;
    voice::useSpeaker();
}

// Back to the mic once the reply has fully played out.
void maybeListen() {
    if (!gWantListen || gMode != Mode::Spk) return;
    if (gCount > 1 || M5.Speaker.isPlaying(kCh)) return;
    if (gPlayed) {
        sendType("playback_done");
        gPlayed = false;
    }
    wantMic();
}

void onState(const char* s) {
    if (!strcmp(s, "listening")) {
        if (gMode == Mode::Mic) {
            gPhase = Phase::Listening;
        } else {
            gWantListen = true;  // finish playing first
            maybeListen();
        }
    } else if (!strcmp(s, "thinking") || !strcmp(s, "speaking")) {
        gWantListen = false;
        gPhase = s[0] == 't' ? Phase::Thinking : Phase::Speaking;
        if (gMode != Mode::Spk) toSpeaker();
    }
}

void onText(const uint8_t* p, size_t n) {
    JsonDocument doc;
    if (deserializeJson(doc, p, n)) return;
    const char* type = doc["type"] | "";
    if (!strcmp(type, "state")) {
        onState(doc["state"] | "");
    } else if (!strcmp(type, "stop")) {
        ringClear();  // queued blocks (<=128 ms) finish, then the ramp-down in pumpSpeaker
        gPrebuf = true;
    } else if (!strcmp(type, "error")) {
        setErr(doc["message"] | "Core error");
    }
}

void onEvent(WStype_t t, uint8_t* p, size_t n) {
    switch (t) {
        case WStype_CONNECTED: {
            char b[64];
            snprintf(b, sizeof(b), "{\"type\":\"hello\",\"fw\":\"%s\"}", NOD_FW_VERSION);
            gWs.sendTXT(b);
            gErr[0] = 0;
            if (gMode != Mode::Mic) wantMic();
            break;
        }
        case WStype_DISCONNECTED:
            if (gPhase != Phase::Off && gPhase != Phase::Connecting) {
                gPhase = Phase::Connecting;
                gConnSince = millis();
            }
            break;
        case WStype_TEXT:
            onText(p, n);
            break;
        case WStype_BIN:
            if (gMode == Mode::Spk) {
                ringPush(p, n);
                gLastFrameMs = millis();
            }
            break;
        default:
            break;
    }
}

void pumpMic() {
    if (gMode != Mode::Mic) return;
    // Same double-buffer pattern as voice::update: when record() returns true,
    // the other buffer is complete and ours.
    if (!M5.Mic.record(gB->mic[gMicIdx], kFrame, kRate)) return;
    gMicIdx = 1 - gMicIdx;
    if (!gMicQueued) {
        gMicQueued = true;
        return;
    }
    const int16_t* f = gB->mic[gMicIdx];
    int32_t peak = 0;
    for (size_t i = 0; i < kFrame; ++i) {
        const int32_t v = f[i] < 0 ? -f[i] : f[i];
        if (v > peak) peak = v;
    }
    const float tgt = peak / 32768.f;
    gLevel = tgt > gLevel ? tgt : gLevel * 0.85f + tgt * 0.15f;
    if (gWs.isConnected()) gWs.sendBIN(reinterpret_cast<const uint8_t*>(f), kFrame * 2);
}

void queueBlock(int16_t* b, size_t n) {
    audio::softLimit(b, n);
    if (M5.Speaker.playRaw(b, n, kRate, false, 1, kCh, false)) {
        gLast = b[n - 1];
        gNeedRamp = true;
        gPlayed = true;
        gPlayIdx = 1 - gPlayIdx;
    }
}

void pumpSpeaker() {
    if (gMode != Mode::Spk) return;
    const bool quiet = gWantListen || millis() - gLastFrameMs > kQuietMs;
    while (M5.Speaker.isPlaying(kCh) < 2) {
        const size_t avail = gCount & ~(size_t)1;
        if (gPrebuf) {
            if (avail < kPreBytes && !(quiet && avail)) break;
            gPrebuf = false;
            gFadeIn = true;
        }
        int16_t* b = gB->play[gPlayIdx];
        size_t n;
        if (avail >= kBlock * 2) {
            n = kBlock;
        } else if (quiet && avail) {
            n = avail / 2;  // end of reply (or a stall): play the tail, fade out, re-buffer
        } else {
            // Starved with the queue empty: ramp the last sample to zero instead of a click.
            if (gNeedRamp && !M5.Speaker.isPlaying(kCh)) {
                for (size_t i = 0; i < kFade; ++i) gB->ramp[i] = (int16_t)((int32_t)gLast * (kFade - 1 - i) / kFade);
                M5.Speaker.playRaw(gB->ramp, kFade, kRate, false, 1, kCh, false);
                gNeedRamp = false;
                gPrebuf = true;
            }
            break;
        }
        ringPop(reinterpret_cast<uint8_t*>(b), n * 2);
        if (gFadeIn) {
            for (size_t i = 0; i < kFade && i < n; ++i) b[i] = (int16_t)((int32_t)b[i] * (int32_t)i / (int32_t)kFade);
            gFadeIn = false;
        }
        if (n < kBlock) {
            const size_t f = n < kFade ? n : kFade;
            for (size_t i = 0; i < f; ++i) b[n - f + i] = (int16_t)((int32_t)b[n - f + i] * (int32_t)(f - 1 - i) / (int32_t)f);
            gPrebuf = true;
        }
        queueBlock(b, n);
        if (n < kBlock) gNeedRamp = false;  // tail already faded to zero
    }
    // Core stopped sending and the buffer drained: tell it the reply was heard.
    if (gPlayed && gCount < 2 && millis() - gLastFrameMs > 300 && !M5.Speaker.isPlaying(kCh)) {
        sendType("playback_done");
        gPlayed = false;
    }
    maybeListen();
}

}  // namespace

bool begin() {
    gErr[0] = 0;
    if (gPhase != Phase::Off) return true;
    if (!Sys.wifiConnected) { setErr("No Wi-Fi"); return false; }
    if (Cfg.hostToken.empty() || Cfg.hostAddr.empty()) { setErr("Not paired with Core"); return false; }
    if (voice::state() != voice::State::Idle) { setErr("Mic busy"); return false; }
    voice::stopPlayback();
    gB = static_cast<Bufs*>(malloc(sizeof(Bufs)));
    if (!gB) { setErr("Out of memory"); return false; }
    snprintf(gAuth, sizeof(gAuth), "Authorization: Bearer %s", Cfg.hostToken.c_str());
    ringClear();
    gLevel = 0.f;
    gMode = Mode::None;
    gNeedMic = false;
    gWantListen = false;
    WiFi.setSleep(false);  // power-save wakeups add jitter to the audio stream
    gWs.begin(Cfg.hostAddr.c_str(), Cfg.hostPort, "/voice/live");
    gWs.setExtraHeaders(gAuth);
    gWs.onEvent(onEvent);
    gWs.setReconnectInterval(2000);
    gWs.enableHeartbeat(15000, 3000, 2);
    gPhase = Phase::Connecting;
    gConnSince = millis();
    Sys.recording = true;  // keeps the screen awake and shows the REC lamp
    return true;
}

void end() {
    if (gPhase == Phase::Off) return;
    if (gWs.isConnected()) sendType("bye");
    gWs.disconnect();
    gPhase = Phase::Off;
    gMode = Mode::None;
    Sys.recording = false;
    voice::useSpeaker();  // leaves the codec ready for UI sounds
    WiFi.setSleep(true);
    free(gB);
    gB = nullptr;
}

void update() {
    if (gPhase == Phase::Off) return;
    gWs.loop();
    if (gPhase == Phase::Off) return;
    pumpMic();
    pumpSpeaker();
    if (gNeedMic && (int32_t)(millis() - gNextTry) >= 0) {
        if (toMic()) {
            gNeedMic = false;
        } else if (++gMicTries >= 5) {
            end();  // keeps the "mic did not start" error for the screen
            return;
        } else {
            gNextTry = millis() + 200;
        }
    }
    if (gPhase == Phase::Connecting && millis() - gConnSince > 10000) {
        setErr("Core not answering");
        end();
    }
}

void interrupt() {
    if (gPhase != Phase::Thinking && gPhase != Phase::Speaking) return;
    sendType("interrupt");
    ringClear();
    gPrebuf = true;
}

bool        micActive() { return gPhase != Phase::Off && gMode == Mode::Mic; }
Phase       phase() { return gPhase; }
float       level() { return gLevel; }
const char* error() { return gErr; }

}  // namespace live
}  // namespace maz
