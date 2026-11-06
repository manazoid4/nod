// Nod swappable screens. The UI is laid out from width/height, so a different
// panel = a different profile, no UI code changes. Only the stock panel is
// pre-filled; others are TEMPLATES (verified=false) until tested on hardware.
#pragma once
#include <stdint.h>
#include <string.h>

namespace nod {

struct DisplayProfile {
    const char* id;
    const char* name;
    const char* driver;
    uint16_t w, h;          // landscape size the UI sees
    int16_t  offX, offY;    // controller RAM offset (panel-specific)
    bool     invert;
    bool     verified;      // true only after a physical PASS on that panel
    const char* note;
};

static const DisplayProfile kProfiles[] = {
    {"cardputer-stock", "Cardputer ADV built-in 1.14in", "ST7789V2", 240, 135, 40, 52, true, false,
     "Values from M5GFX Cardputer config; confirm on device"},
    {"st7789-240x240", "1.3in 240x240 IPS (template)", "ST7789", 240, 240, 0, 0, true, false,
     "Template - needs wiring + offsets tested"},
    {"st7789-320x170", "1.9in 320x170 IPS (template)", "ST7789", 320, 170, 0, 35, true, false,
     "Template - needs wiring + offsets tested"},
    {"ili9341-320x240", "2.4in 320x240 (template)", "ILI9341", 320, 240, 0, 0, false, false,
     "Template - needs wiring + offsets tested"},
};
static const int kProfileCount = sizeof(kProfiles) / sizeof(kProfiles[0]);

inline const DisplayProfile* findProfile(const char* id) {
    for (int i = 0; i < kProfileCount; i++)
        if (id && strcmp(kProfiles[i].id, id) == 0) return &kProfiles[i];
    return nullptr;
}
// Unknown/corrupt saved id -> stock panel, so a bad setting can never blank the UI.
inline const DisplayProfile& profileOrDefault(const char* id) {
    const DisplayProfile* p = findProfile(id);
    return p ? *p : kProfiles[0];
}
inline bool profileUsable(const DisplayProfile& p) { return p.w >= 200 && p.h >= 120; }

}  // namespace nod
