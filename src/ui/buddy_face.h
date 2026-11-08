// Piblo Buddy - a small round companion drawn with M5GFX primitives (original art,
// no bitmaps). Five moods: idle, working, celebrating, sleeping, needs-attention.
#pragma once
#include <M5Unified.h>

#include <alert_policy.h>

namespace maz {
namespace buddy_face {

// cx,cy = centre, r = body radius, ms = millis() (drives blink / bob / shake).
void draw(M5Canvas& g, int cx, int cy, int r, alert_policy::Mood mood, uint32_t ms);

}  // namespace buddy_face
}  // namespace maz
