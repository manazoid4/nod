#include "buddy_face.h"

#include <math.h>

#include "theme.h"

namespace maz {
namespace buddy_face {

using alert_policy::Mood;
using namespace theme;

namespace {
constexpr float kTau = 6.2831853f;
float wave(uint32_t ms, uint32_t periodMs) { return sinf(kTau * static_cast<float>(ms % periodMs) / static_cast<float>(periodMs)); }
}  // namespace

void draw(M5Canvas& g, int cx, int cy, int r, Mood mood, uint32_t ms) {
    int dx = 0, dy = 0;
    switch (mood) {
        case Mood::Idle:           dy = static_cast<int>(wave(ms, 2400) * 1.5f); break;
        case Mood::Working:        dy = static_cast<int>(wave(ms, 900) * 1.0f); break;
        case Mood::Celebrating:    dy = -static_cast<int>(fabsf(wave(ms, 700)) * r * 0.35f); break;
        case Mood::Sleeping:       dy = static_cast<int>(wave(ms, 4000) * 2.0f); break;
        case Mood::NeedsAttention: dx = static_cast<int>(wave(ms, 260) * 2.0f); break;
    }
    const int x = cx + dx, y = cy + dy;
    const int eyeDx = r * 38 / 100, eyeY = y - r / 6, eyeR = r / 6 > 2 ? r / 6 : 2;

    g.fillEllipse(cx, cy + r + 2, r * 3 / 4, 3, LINE);  // ground shadow
    g.fillCircle(x, y, r, ACCENT);
    g.drawCircle(x, y, r, TEXT);

    switch (mood) {
        case Mood::Idle: {
            const bool blink = (ms % 3200) < 140;
            for (int s = -1; s <= 1; s += 2) {
                if (blink) g.drawFastHLine(x + s * eyeDx - eyeR, eyeY, eyeR * 2, BG);
                else g.fillCircle(x + s * eyeDx, eyeY, eyeR, BG);
            }
            g.fillArc(x, y + r / 6, r / 3 - 1, r / 3 + 1, 25, 155, BG);  // smile
            break;
        }
        case Mood::Working: {
            const int look = wave(ms, 1800) > 0 ? 2 : -2;
            for (int s = -1; s <= 1; s += 2) {
                g.fillCircle(x + s * eyeDx, eyeY, eyeR + 1, TEXT);
                g.fillCircle(x + s * eyeDx + look, eyeY, eyeR - 1 > 1 ? eyeR - 1 : 1, BG);
            }
            g.drawFastHLine(x - r / 4, y + r / 3, r / 2, BG);  // flat mouth
            const int dots = 1 + static_cast<int>((ms / 350) % 3);  // "..." thinking
            for (int i = 0; i < dots; ++i) g.fillCircle(x + r / 2 + 3 + i * 5, y - r - 2, 1, TEXT);
            break;
        }
        case Mood::Celebrating: {
            for (int s = -1; s <= 1; s += 2) g.fillArc(x + s * eyeDx, eyeY + eyeR, eyeR + 2, eyeR + 4, 190, 350, BG);  // ^ ^
            g.fillArc(x, y + r / 6, r / 3, r / 3 + 2, 10, 170, BG);
            g.fillCircle(x, y + r / 6 + 2, r / 5, BG);  // open mouth
            const uint16_t conf[3] = {OK, LIVE, TEXT};
            for (int i = 0; i < 6; ++i) {
                const int px = cx - r - 6 + ((i * 37 + static_cast<int>(ms / 60)) % (2 * r + 12));
                const int py = cy - r - 4 + ((i * 23 + static_cast<int>(ms / 40)) % (2 * r + 8));
                g.fillRect(px, py, 2, 2, conf[i % 3]);
            }
            break;
        }
        case Mood::Sleeping: {
            for (int s = -1; s <= 1; s += 2) g.fillArc(x + s * eyeDx, eyeY - 2, eyeR + 1, eyeR + 2, 20, 160, BG);  // closed
            g.fillCircle(x, y + r / 3, 2, BG);
            g.setFont(&fonts::Font0);
            g.setTextDatum(top_left);
            g.setTextColor(TEXT, BG);
            const int zy = static_cast<int>((ms / 250) % 4);
            g.drawString("z", x + r - 2, y - r + 6 - zy);
            g.drawString("Z", x + r + 6, y - r - 2 - zy);
            break;
        }
        case Mood::NeedsAttention: {
            for (int s = -1; s <= 1; s += 2) {
                g.fillCircle(x + s * eyeDx, eyeY, eyeR + 2, TEXT);
                g.fillCircle(x + s * eyeDx, eyeY, eyeR - 1 > 1 ? eyeR - 1 : 1, BG);
            }
            g.drawCircle(x, y + r / 3, 3, BG);  // small "o" mouth
            const bool on = (ms % 600) < 400;   // blinking "!" badge
            g.fillCircle(x + r - 2, y - r + 2, 7, on ? ERR : LINE);
            g.setFont(&fonts::Font2);
            g.setTextDatum(middle_center);
            g.setTextColor(TEXT, on ? ERR : LINE);
            g.drawString("!", x + r - 2, y - r + 3);
            g.setTextDatum(top_left);
            break;
        }
    }
}

}  // namespace buddy_face
}  // namespace maz
