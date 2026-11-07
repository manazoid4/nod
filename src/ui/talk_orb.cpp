#include "talk_orb.h"

#include <nod_theme.h>

namespace maz {
namespace ui {

namespace nt = nod::theme;

void talkOrb(M5Canvas& g, int cx, int cy, int r, nod::TalkState s, float micLevel,
             bool focused, const char* label, const char* sub) {
    using namespace nod;
    const uint32_t ms = millis();
    int level = (int)(micLevel * 1000.f);
    // No playback level is exposed, so speaking uses a gentle fixed pulse.
    if (s == TALK_SPEAKING) level = 350 + triangle(ms, 480, 400);

    const bool live = s == TALK_LISTENING || s == TALK_SPEAKING;
    const uint16_t fill = live ? nt::LIVE : s == TALK_THINKING ? nt::rgb565(nt::mix(nt::TALK_RGB, nt::BG_RGB, 110)) : nt::TALK;
    const uint16_t ring = live ? nt::LIVE : nt::TALK;

    g.fillCircle(cx, cy, r, fill);
    if (s == TALK_THINKING) {
        const int a = arcStartDeg(ms);
        g.fillArc(cx, cy, r + 3, r + 6, (float)a, (float)(a + 90), nt::THINK);
    } else {
        const int rr = live ? levelRingRadius(r, level) : idleRingRadius(r, ms);
        g.drawCircle(cx, cy, rr, ring);
        if (r >= 30) g.drawCircle(cx, cy, rr + 1, ring);
    }
    if (focused) g.drawCircle(cx, cy, r - 3, nt::BG);

    if (r >= 30 && label) {
        g.setTextDatum(middle_center);
        g.setTextColor(s == TALK_THINKING ? nt::TEXT : nt::BG, fill);
        g.setFont(sub ? &fonts::Font4 : &fonts::Font2);
        g.drawString(label, cx, sub ? cy - 8 : cy);
        if (sub) {
            g.setFont(&fonts::Font2);
            g.drawString(sub, cx, cy + 14);
        }
        g.setTextDatum(top_left);
    }
}

}  // namespace ui
}  // namespace maz
