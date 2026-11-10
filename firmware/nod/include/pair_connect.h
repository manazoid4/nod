// Piblo - "Connect to computer" pairing logic (docs/protocol/DEVICE-PAIRING.md).
// Pure (no Arduino) so the PC test build covers it: discovery-reply parsing, code formatting,
// device id from the MAC, and the poll state machine.
#pragma once
#include <stddef.h>
#include <stdint.h>
#include <string>

namespace nod {
namespace pair {

// ---- tiny JSON field readers (flat one-line objects only) ----
// Returns the index just after `"key":` (skipping spaces), or npos.
inline size_t keyValueAt(const std::string& j, const char* key) {
    const std::string pat = std::string("\"") + key + "\"";
    size_t p = j.find(pat);
    if (p == std::string::npos) return std::string::npos;
    p += pat.size();
    while (p < j.size() && (j[p] == ' ' || j[p] == '\t')) ++p;
    if (p >= j.size() || j[p] != ':') return std::string::npos;
    ++p;
    while (p < j.size() && (j[p] == ' ' || j[p] == '\t')) ++p;
    return p < j.size() ? p : std::string::npos;
}

inline bool jsonInt(const std::string& j, const char* key, long& out) {
    size_t p = keyValueAt(j, key);
    if (p == std::string::npos) return false;
    long v = 0;
    size_t digits = 0;
    while (p < j.size() && j[p] >= '0' && j[p] <= '9' && digits < 9) {
        v = v * 10 + (j[p] - '0');
        ++p;
        ++digits;
    }
    if (!digits) return false;
    out = v;
    return true;
}

// String value; handles \" and \\ only, stops at the closing quote.
inline bool jsonString(const std::string& j, const char* key, std::string& out) {
    size_t p = keyValueAt(j, key);
    if (p == std::string::npos || j[p] != '"') return false;
    ++p;
    std::string s;
    while (p < j.size() && j[p] != '"') {
        if (j[p] == '\\' && p + 1 < j.size()) ++p;
        s += j[p++];
    }
    if (p >= j.size()) return false;
    out = s;
    return true;
}

// ---- discovery reply: {"piblo":1,"port":8787,"name":"MAZPC","version":"x"} ----
struct Discovery {
    uint16_t port = 0;
    std::string name;
};

inline std::string printableName(const std::string& in, size_t maxLen) {
    std::string out;
    for (size_t i = 0; i < in.size() && out.size() < maxLen; ++i) {
        const unsigned char c = static_cast<unsigned char>(in[i]);
        if (c >= 0x20 && c < 0x7F) out += static_cast<char>(c);
    }
    return out;
}

inline bool parseDiscovery(const std::string& json, Discovery& out) {
    long ver = 0, port = 0;
    if (!jsonInt(json, "piblo", ver) || ver != 1) return false;
    if (!jsonInt(json, "port", port) || port < 1 || port > 65535) return false;
    std::string name;
    jsonString(json, "name", name);
    out.port = static_cast<uint16_t>(port);
    out.name = printableName(name, 32);
    return true;
}

// ---- code: "482913" -> "482 913" (empty if not exactly 6 digits) ----
inline std::string formatCode(const std::string& code) {
    if (code.size() != 6) return std::string();
    for (size_t i = 0; i < 6; ++i)
        if (code[i] < '0' || code[i] > '9') return std::string();
    return code.substr(0, 3) + " " + code.substr(3);
}

// ---- device id: "piblo-" + last 6 hex digits of the MAC ----
inline std::string deviceIdFromMac(const uint8_t mac[6]) {
    static const char H[] = "0123456789abcdef";
    std::string id = "piblo-";
    for (int i = 3; i < 6; ++i) {
        id += H[(mac[i] >> 4) & 0xF];
        id += H[mac[i] & 0xF];
    }
    return id;
}

// ---- the request body ----
inline std::string requestBody(const std::string& deviceId, const char* name) {
    return std::string("{\"device_id\":\"") + deviceId + "\",\"name\":\"" + name + "\"}";
}

// ---- poll state machine ----
enum class Phase : uint8_t {
    Discovering,  // "Looking for your computer..."
    NoComputer,   // no discovery reply
    Requesting,   // asked, waiting for a code
    Waiting,      // code shown, "Click Allow on your computer"
    Approved,     // token received
    Denied,       // "Not allowed"
    TimedOut,     // expired, 404, request failed or 120 s passed
};

constexpr uint32_t kPollEveryMs = 2000;
constexpr uint32_t kGiveUpMs = 120000;

inline bool terminal(Phase p) {
    return p == Phase::NoComputer || p == Phase::Approved || p == Phase::Denied || p == Phase::TimedOut;
}

// Folds one poll answer into the phase. `http` <= 0 is a transport error and keeps waiting: one
// dropped packet must not end pairing. 404 is terminal per the contract.
inline Phase nextPhase(Phase cur, int http, const std::string& status) {
    if (terminal(cur)) return cur;
    if (http == 404) return Phase::TimedOut;
    if (http != 200) return cur;
    if (status == "approved") return Phase::Approved;
    if (status == "denied") return Phase::Denied;
    if (status == "expired") return Phase::TimedOut;
    return cur;  // "pending" or anything unknown
}

inline Phase afterElapsed(Phase cur, uint32_t elapsedMs) {
    return (!terminal(cur) && elapsedMs >= kGiveUpMs) ? Phase::TimedOut : cur;
}

}  // namespace pair
}  // namespace nod
