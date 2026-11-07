// Nod brand palette in ONE place. Change a value here and the device Home, the
// preview and the tests all follow. These are placeholders until the final
// brand palette lands; nothing else in the firmware should hard-code them.
#pragma once
#include <stdint.h>

namespace nod {
namespace theme {

// 0xRRGGBB -> RGB565 (what the panel takes).
constexpr uint16_t rgb565(uint32_t c) {
    return (uint16_t)(((c >> 8) & 0xF800) | ((c >> 5) & 0x07E0) | ((c >> 3) & 0x001F));
}
// Blend a toward b by t/256 (per channel). Used for dimmed rings and glows.
constexpr uint32_t mix(uint32_t a, uint32_t b, uint32_t t) {
    return ((((a >> 16) & 255) * (256 - t) + ((b >> 16) & 255) * t) >> 8) << 16 |
           ((((a >> 8) & 255) * (256 - t) + ((b >> 8) & 255) * t) >> 8) << 8 |
           (((a & 255) * (256 - t) + (b & 255) * t) >> 8);
}

constexpr uint32_t BG_RGB      = 0x0B0D10;  // near-black
constexpr uint32_t TEXT_RGB    = 0xF3EBDD;  // warm off-white
constexpr uint32_t TALK_RGB    = 0xFF5A36;  // tomato-orange: the Talk circle
constexpr uint32_t LIVE_RGB    = 0x3DDC97;  // mint: mic is live / nod is speaking
constexpr uint32_t THINK_RGB   = 0xFFB020;  // amber arc while thinking
constexpr uint32_t BUTTON_RGB  = 0x1B2026;  // right-column button fill
constexpr uint32_t DIM_RGB     = 0x9AA4AE;

constexpr uint16_t BG     = rgb565(BG_RGB);
constexpr uint16_t TEXT   = rgb565(TEXT_RGB);
constexpr uint16_t TALK   = rgb565(TALK_RGB);
constexpr uint16_t LIVE   = rgb565(LIVE_RGB);
constexpr uint16_t THINK  = rgb565(THINK_RGB);
constexpr uint16_t BUTTON = rgb565(BUTTON_RGB);
constexpr uint16_t DIM    = rgb565(DIM_RGB);

}  // namespace theme
}  // namespace nod
