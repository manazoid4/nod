// Nod consumer Home: four big plain-language cards. Layout is computed from the
// screen size so every display profile gets a usable, non-overlapping UI.
#pragma once
#include <stdint.h>
#include "display_profiles.h"

namespace nod {

struct Rect { int16_t x, y, w, h; };
enum Card : uint8_t { CARD_SUBTITLES, CARD_ROUTINES, CARD_SAVE, CARD_MORE, CARD_COUNT };
static const char* const kCardLabel[CARD_COUNT] = {"SUBTITLES", "ROUTINES", "SAVE THIS", "MORE"};
static const char* const kCardHint[CARD_COUNT] = {
    "Captions for your video", "One key, one job", "Voice idea to note", "All other apps"};

struct HomeLayout {
    Rect statusBar;
    Rect cards[CARD_COUNT];
    Rect footer;
};

inline HomeLayout computeHome(uint16_t w, uint16_t h) {
    HomeLayout L;
    const int16_t pad = 6, gap = 6;
    const int16_t bar = h >= 160 ? 22 : 16;
    const int16_t foot = h >= 160 ? 18 : 12;
    L.statusBar = {0, 0, (int16_t)w, bar};
    L.footer = {0, (int16_t)(h - foot), (int16_t)w, foot};
    const int16_t top = bar + pad, bottom = h - foot - pad;
    const int16_t cw = (w - 2 * pad - gap) / 2, ch = (bottom - top - gap) / 2;
    for (int i = 0; i < CARD_COUNT; i++) {
        L.cards[i] = {(int16_t)(pad + (i % 2) * (cw + gap)), (int16_t)(top + (i / 2) * (ch + gap)), cw, ch};
    }
    return L;
}

// Arrow keys move on the 2x2 grid; number keys 1-4 jump. Wraps never; stays put at edges.
inline Card moveSelection(Card c, char dir /* 'L','R','U','D' */) {
    int col = c % 2, row = c / 2;
    if (dir == 'L' && col > 0) col--;
    if (dir == 'R' && col < 1) col++;
    if (dir == 'U' && row > 0) row--;
    if (dir == 'D' && row < 1) row++;
    return (Card)(row * 2 + col);
}

}  // namespace nod
