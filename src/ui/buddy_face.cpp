#include "buddy_face.h"

#include "theme.h"

namespace maz {
namespace buddy_face {

using alert_policy::Mood;
using namespace theme;

// Integer-only on purpose (firmware size gate): bob/shake/blink come from ms phases.
void draw(M5Canvas& g, int cx, int cy, int r, Mood mood, uint32_t ms) {
    const bool alarm = mood == Mood::NeedsAttention, party = mood == Mood::Celebrating;
    const bool flip = (ms / (alarm ? 130 : party ? 300 : 700)) & 1;
    const int x = cx + (alarm ? (flip ? 2 : -2) : 0);
    const int y = cy + (party ? (flip ? -r / 3 : 0) : (flip ? 1 : 0));
    const int ex = r * 38 / 100, ey = y - r / 6, er = r / 6;

    g.drawFastHLine(cx - r / 2, cy + r + 2, r, LINE);  // ground shadow
    g.fillCircle(x, y, r, ACCENT);
    g.drawCircle(x, y, r, TEXT);

    const bool shut = mood == Mood::Sleeping || (mood == Mood::Idle && ms % 3200 < 140);
    for (int s = -1; s <= 1; s += 2) {
        const int px = x + s * ex;
        if (shut) g.drawFastHLine(px - er, ey, er * 2, BG);
        else { g.fillCircle(px, ey, er + alarm * 2, alarm ? TEXT : BG); if (alarm) g.fillCircle(px, ey, er - 1, BG); }
    }
    if (mood == Mood::Idle || party) g.fillArc(x, y + r / 6, r / 3, r / 3 + 2, 25, 155, BG);  // smile
    else g.drawFastHLine(x - r / 4, y + r / 3, r / 2, BG);  // flat mouth (working / sleeping / alarm)

    if (alarm && flip) {  // blinking "!" badge
        g.fillCircle(x + r - 2, y - r + 2, 7, ERR);
        g.fillRect(x + r - 3, y - r - 2, 2, 7, TEXT);
    }
}

}  // namespace buddy_face
}  // namespace maz
