// Piblo's character (the green hooded one), drawn from a generated RGB565 sprite.
#pragma once
#include <M5Unified.h>

#include <talk_home.h>

namespace maz {
namespace ui {

constexpr int CHAR_W = 29, CHAR_H = 44;  // matches src/ui/chars/green.h

// Top-left at x,y. Bobs to show the Talk state; listening follows the mic level.
void character(M5Canvas& g, int x, int y, nod::TalkState s, float micLevel, uint32_t ms);

}  // namespace ui
}  // namespace maz
