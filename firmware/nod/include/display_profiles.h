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
    // Size 1 - the built-in Cardputer ADV panel. Ships first.
    {"standard", "Standard 1.14in (Cardputer ADV built-in)", "ST7789V2", 240, 135, 40, 52, true, false,
     "Offsets from M5GFX Cardputer config; confirm on device"},
    // Size 2 - larger pop-in panel, roughly half a Kindle (~3.5in). Exact module not chosen:
    // 480x320 SPI ST7796/ILI9488 class. Template until a sample is bought and tested.
    {"large", "Large 3.5in 480x320 (sample pending)", "ST7796", 480, 320, 0, 0, false, false,
     "Template - driver, wiring and offsets to be set from the sample"},
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
