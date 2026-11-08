// Piblo — live voice: a thin terminal for Core's /voice/live WebSocket.
// The device only streams mic PCM up and plays reply PCM down (16 kHz mono
// PCM16). Turn detection and thinking happen on Core. Half-duplex: the ES8311
// codec is shared, so the mic is off while Piblo is thinking or speaking.
#pragma once
#include <stdint.h>

namespace maz {
namespace live {

enum class Phase : uint8_t { Off, Connecting, Listening, Thinking, Speaking };

bool        begin();      // false (see error()) if Wi-Fi / Core address / memory is missing
void        end();        // sends bye, frees buffers, restores the speaker for UI sounds
void        update();     // call every loop while active
void        interrupt();  // user pressed a key while Piblo is thinking/speaking
bool        micActive();  // true while the mic owns the shared codec (UI tones must stay silent)
Phase       phase();
float       level();      // 0..1 mic peak for the orb
const char* error();      // "" when fine

}  // namespace live
}  // namespace maz
