// Nod consumer Home: four big cards a normal person understands at a glance.
//   SUBTITLES  captions for a video on your laptop/TV (coming: needs Nod Core)
//   ROUTINES   your four one-key actions (the existing quick slots)
//   SAVE THIS  speak an idea, it becomes a note (Brain Dump)
//   MORE       every other app: the full six-surface grid, unchanged
// Hold SPACE anywhere on Home = CALL (talk to Nod). Keys 1-4 still run quick actions.
#include <home_layout.h>

#include <cstring>
#include <string>

#include "../audio/sfx.h"
#include "../core/field.h"
#include "../core/shell.h"
#include "../input/keyboard.h"
#include "apps.h"
#include "common.h"

namespace maz {
namespace apps {

using namespace theme;

namespace {

const char* const kTarget[nod::CARD_COUNT] = {"subtitles", "routines", "braindump", "more"};

class NodHomeApp final : public App {
public:
    const char* id() const override { return "home"; }
    const char* title() const override { return "Nod"; }
    const char* hints() const override { return "hold SPACE talk   ENTER open"; }

    void onEnter() override { _spaceArmed = false; invalidate(); }

    bool onKey(const KeyEvent& e) override {
        if (!e.down) {
            if (e.code == KEY_SPACE && _spaceArmed) { _spaceArmed = false; shell::pushById("talk"); return true; }
            return false;
        }
        if (e.code == KEY_SPACE) { _spaceArmed = true; return true; }
        if (e.code >= KEY_1 && e.code <= KEY_4) {
            const int slot = static_cast<int>(e.code - KEY_1) + 1;
            if (e.mods & MOD_FN) field::cycleQuick(slot); else field::runQuick(slot);
            invalidate();
            return true;
        }
        char dir = 0;
        if (e.code == KEY_LEFT) dir = 'L';
        if (e.code == KEY_RIGHT) dir = 'R';
        if (e.code == KEY_UP) dir = 'U';
        if (e.code == KEY_DOWN) dir = 'D';
        if (dir) {
            const nod::Card next = nod::moveSelection(_sel, dir);
            if (next != _sel) { _sel = next; sfx::select(); invalidate(); }
            return true;
        }
        if (e.code == KEY_ENTER) { sfx::confirm(); shell::pushById(kTarget[_sel]); return true; }
        return false;
    }

    void update() override {
        if (_spaceArmed && KB.heldFor(KEY_SPACE) > 250) { _spaceArmed = false; shell::pushById("talk"); }
    }

    std::string contextSnapshot() const override {
        return std::string("Nod Home, selected ") + nod::kCardLabel[_sel];
    }

    void render(M5Canvas& g) override {
        g.fillScreen(BG);
        nod::Rect r[nod::CARD_COUNT];
        nod::computeGrid({0, (int16_t)BODY_Y, (int16_t)SCREEN_W, (int16_t)BODY_H}, r);
        for (int i = 0; i < nod::CARD_COUNT; i++) {
            const bool sel = i == _sel;
            g.fillRoundRect(r[i].x, r[i].y, r[i].w, r[i].h, 6, sel ? ACCENT : PANEL);
            if (!sel) g.drawRoundRect(r[i].x, r[i].y, r[i].w, r[i].h, 6, LINE);
            g.setTextDatum(top_left);
            g.setFont(&fonts::FreeSansBold9pt7b);
            if (g.textWidth(nod::kCardLabel[i]) > r[i].w - 12) g.setFont(&fonts::Font2);
            g.setTextColor(sel ? BG : TEXT);
            g.drawString(nod::kCardLabel[i], r[i].x + 6, r[i].y + 6);
            g.setFont(&fonts::Font0);
            g.setTextColor(sel ? BG : DIM);
            g.drawString(nod::kCardHint[i], r[i].x + 6, r[i].y + r[i].h - 12);
        }
    }

private:
    nod::Card _sel = nod::CARD_SUBTITLES;
    bool _spaceArmed = false;
};

// ROUTINES: the four existing one-key quick actions, shown as a list.
class RoutinesApp final : public App {
public:
    const char* id() const override { return "routines"; }
    const char* title() const override { return "Routines"; }
    const char* hints() const override { return "ENTER run   TAB change   ESC back"; }

    bool onKey(const KeyEvent& e) override {
        if (!e.down) return false;
        if (e.code == KEY_UP && _sel > 0) { _sel--; sfx::select(); invalidate(); return true; }
        if (e.code == KEY_DOWN && _sel < 3) { _sel++; sfx::select(); invalidate(); return true; }
        if (e.code == KEY_TAB) { field::cycleQuick(_sel + 1); invalidate(); return true; }
        if (e.code == KEY_ENTER) { sfx::confirm(); field::runQuick(_sel + 1); invalidate(); return true; }
        return false;
    }

    void render(M5Canvas& g) override {
        g.fillScreen(BG);
        ui::header(g, "ROUTINES", "one key, one job");
        for (int i = 0; i < 4; i++) {
            char key[4];
            snprintf(key, sizeof(key), "%d", i + 1);
            ui::listRow(g, i + 1, i == _sel, field::quickLabel(i + 1), key);
        }
    }

private:
    int _sel = 0;
};

// SUBTITLES: honest placeholder until Nod Core ships the captions job.
class SubtitlesApp final : public App {
public:
    const char* id() const override { return "subtitles"; }
    const char* title() const override { return "Subtitles"; }
    const char* hints() const override { return "ESC back"; }
    void render(M5Canvas& g) override {
        g.fillScreen(BG);
        ui::header(g, "SUBTITLES", "COMING SOON");
        ui::emptyState(g, "Captions for a video on your laptop", "Needs a Nod Core update. Not ready yet.");
    }
};

}  // namespace

App* makeHome() { return new NodHomeApp(); }
App* makeRoutines() { return new RoutinesApp(); }
App* makeSubtitles() { return new SubtitlesApp(); }

}  // namespace apps
}  // namespace maz
