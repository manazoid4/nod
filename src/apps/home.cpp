#include <array>
#include <cstring>
#include <string>
#include <vector>

#include "../audio/sfx.h"
#include "../core/field.h"
#include "../core/settings.h"
#include "../core/shell.h"
#include "../core/sys.h"
#include "../input/keyboard.h"
#include "../net/mazhost.h"
#include "../net/net.h"
#include <nod_theme.h>
#include <talk_home.h>

#include "../audio/voice.h"
#include "../net/host_worker.h"
#include "../ui/lvgl_ui.h"
#include "../ui/talk_orb.h"
#include "apps.h"
#include "common.h"

namespace maz {
namespace apps {

using namespace theme;

namespace {

class HomeApp : public App {
public:
    const char* id() const override { return "home"; }
    const char* title() const override { return "Piblo"; }
    const char* hints() const override { return _hints; }

    void onEnter() override {
        buildPrimary();
        _spaceArmed = false;
        lvui::setActive(true);
        rebuildHints();
        invalidate();
    }

    void onExit() override { lvui::setActive(false); }

    bool onKey(const KeyEvent& e) override {
        if (!e.down) {
            if (e.code == KEY_SPACE) _spaceArmed = false;
            return false;
        }

        // ESC: More (grid) goes back to the Talk circle; otherwise stop any reply that is playing.
        if (e.code == KEY_ESC) {
            if (_grid) { _grid = false; sfx::select(); invalidate(); return true; }
            if (voice::isPlaying()) { voice::stopPlayback(); invalidate(); return true; }
            return false;
        }

        if (e.code >= KEY_1 && e.code <= KEY_4) {
            const int slot = static_cast<int>(e.code - KEY_1) + 1;
            if (e.mods & MOD_FN) field::cycleQuick(slot);
            else field::runQuick(slot);
            rebuildHints();
            invalidate();
            return true;
        }

        if (e.code == KEY_U && host::updateReady()) { shell::confirmFwUpdate(); return true; }
        if (e.code == KEY_SPACE) { _spaceArmed = true; return true; }
        if (!_grid) {  // Talk circle Home
            if (e.code == KEY_ENTER) { activate(_focus); return true; }
            const char dir = e.code == KEY_RIGHT ? 'R' : e.code == KEY_LEFT ? 'L' : e.code == KEY_DOWN ? 'D' : e.code == KEY_UP ? 'U' : 0;
            if (dir) { _focus = nod::moveTalkFocus(_focus, dir); sfx::select(); invalidate(); return true; }
        } else {
            if (e.code == KEY_ENTER) { open(_sel); return true; }
            if (e.code == KEY_RIGHT) { move(+1); return true; }
            if (e.code == KEY_LEFT)  { move(-1); return true; }
            if (e.code == KEY_DOWN)  { move(+TABLE_COLS); return true; }
            if (e.code == KEY_UP)    { move(-TABLE_COLS); return true; }
        }

        size_t n = 0;
        const Descriptor* t = apps::table(n);
        for (size_t i = 0; i < n; ++i) {
            if (t[i].shortcut && t[i].shortcut == e.code) {
                sfx::confirm();
                shell::pushById(t[i].id);
                return true;
            }
        }
        return false;
    }

    void update() override {
        if (_spaceArmed && KB.heldFor(KEY_SPACE) > 250) {
            _spaceArmed = false;
            shell::pushById("braindump");  // keeps recording while SPACE is held
            return;
        }
        rebuildHints();
        // The shell repaints every 250 ms; the Talk circle asks for ~8 fps so the
        // breathing ring and the thinking arc look smooth. Nothing else redraws.
        if (!_grid && millis() - _lastAnim > 120) { _lastAnim = millis(); invalidate(); }
    }

    std::string contextSnapshot() const override {
        if (!_grid) return std::string("Home: Talk circle; NOW: ") + field::nowText();
        if (_primary.empty() || _sel < 0 || _sel >= static_cast<int>(_primary.size()))
            return field::nowText();
        return std::string("Home selected ") + _primary[_sel]->cellTitle() + "; NOW: " + field::nowText();
    }

    void render(M5Canvas& g) override {
        if (!_grid) { renderTalk(g); return; }
        std::array<lvui::Cell, TABLE_PAGE> cells{};
        for (size_t i = 0; i < _primary.size() && i < cells.size(); ++i) {
            cells[i].title = _primary[i]->cellTitle();
            cells[i].badge = _primary[i]->shortcut ? static_cast<char>('A' + (_primary[i]->shortcut - KEY_A)) : ' ';
        }
        lvui::Status st;
        st.version = "v" NOD_FW_VERSION;
        statusFor(st);
        lvui::renderHome(g, cells.data(), _primary.size(), _sel, st);
    }

private:
    void activate(nod::TalkFocus f) {
        sfx::confirm();
        switch (f) {
            case nod::FOCUS_TALK:  shell::pushById("live"); break;  // T still opens push-to-talk Call
            case nod::FOCUS_SAVE:  shell::pushById("braindump"); break;
            case nod::FOCUS_TODAY: shell::pushById("today"); break;
            default:               _grid = true; invalidate(); break;  // More: the full six-surface grid
        }
    }

    // One short line (about 20 chars fit beside the circle): trouble first, then field status.
    std::string shortLine() const {
        static std::string now;
        if (linkSentence(true)) {
            if (!Sys.wifiConnected) return "No Wi-Fi: press W";
            if (!host::configured()) return "Not paired: Control";
            return "Core is off (PC)";
        }
        if (host::updateReady()) return "Update: press U";
        if (Sys.agentQuestion) return "Agent asked: press N";
        now = field::nowText();
        return now != "READY" ? ui::ellipsis(now, 20) : std::string("1-4 quick actions");
    }

    void renderTalk(M5Canvas& g) {
        namespace nt = nod::theme;
        const nod::TalkHomeLayout L = nod::computeTalkHome({0, BODY_Y, SCREEN_W, BODY_H});
        g.fillRect(0, BODY_Y, SCREEN_W, BODY_H, nt::BG);

        const nod::TalkState st = nod::talkFromSources(
            voice::state() == voice::State::Listening, voice::isPlaying(),
            host_worker::busy() && host_worker::jobKind() == host_worker::JobKind::TalkAudio);
        static const char* const sub[] = {"ENTER", "", "", ""};
        static const char* const word[] = {"Talk", "Listening", "Thinking", "Speaking"};
        ui::talkOrb(g, L.cx, L.cy, L.r, st, voice::level(), _focus == nod::FOCUS_TALK,
                    word[st], st == nod::TALK_IDLE ? sub[st] : nullptr);

        static const char* const hint[3] = {"hold SPACE", "", "all apps"};
        g.setTextDatum(middle_left);
        for (int i = 0; i < 3; ++i) {
            const nod::Rect& b = L.btn[i];
            const bool on = _focus == nod::FOCUS_SAVE + i;
            g.fillRoundRect(b.x, b.y, b.w, b.h, 6, nt::BUTTON);
            g.drawRoundRect(b.x, b.y, b.w, b.h, 6, on ? nt::TEXT : nt::DIM);
            if (on) g.drawRoundRect(b.x + 1, b.y + 1, b.w - 2, b.h - 2, 5, nt::TEXT);
            g.setFont(&fonts::Font2);
            g.setTextColor(nt::TEXT, nt::BUTTON);
            g.drawString(nod::kTalkButton[i], b.x + 10, b.y + b.h / 2);
            if (hint[i][0]) {
                g.setFont(&fonts::Font0);
                g.setTextColor(nt::DIM, nt::BUTTON);
                g.setTextDatum(middle_right);
                g.drawString(hint[i], b.x + b.w - 8, b.y + b.h / 2);
                g.setTextDatum(middle_left);
            }
        }
        g.setFont(&fonts::Font0);
        g.setTextColor(linkSentence(true) ? nt::TEXT : nt::DIM, nt::BG);
        g.drawString(shortLine().c_str(), L.sentence.x, L.sentence.y + L.sentence.h / 2);
        g.setTextDatum(top_left);
    }

    // Link trouble beats everything else, then a ready update, then what the
    // field layer reports. Same words and colours as Call (ui::statusWord).
    void statusFor(lvui::Status& st) {
        static std::string now;
        const char* link = linkSentence(true);
        ui::Phase ph = ui::Phase::Ready;
        st.sentence = "Hold SPACE: brain dump  T: talk  S: type";
        if (link) {
            ph = ui::Phase::Offline;
            st.sentence = link;
        } else if (host::updateReady()) {
            ph = ui::Phase::Update;
            st.sentence = "Press U, then Y";
        } else if (Sys.agentQuestion) {
            ph = ui::Phase::NeedsYou;
            st.sentence = "An agent asked. Press N.";
        }
        const ui::StatusWord w = ui::statusWord(ph);
        st.phase = ph;
        st.line = w.text;
        st.colour = w.colour;
        if (ph == ui::Phase::Ready) {
            now = field::nowText();
            if (now != "READY") st.line = now.c_str();  // outbox, shift, reminder...
        }
    }

    void buildPrimary() {
        _primary.clear();
        size_t n = 0;
        const Descriptor* t = apps::table(n);
        for (size_t i = 0; i < n; ++i)
            if (t[i].onHome && strcmp(t[i].id, "home") && _primary.size() < TABLE_PAGE) _primary.push_back(&t[i]);
        if (_sel >= static_cast<int>(_primary.size())) _sel = 0;
    }

    void rebuildHints() {
        // W opens Wi-Fi from Home (registry shortcut), so say so when Wi-Fi is down.
        if (!_grid) {
            _hints = (linkSentence(true) && !Sys.wifiConnected) ? "ENTER live  SPACE save  W wifi"
                   : host::updateReady()                        ? "ENTER live  SPACE save  U update"
                                                                : "ENTER live  hold SPACE save";
            return;
        }
        _hints = (linkSentence(true) && !Sys.wifiConnected) ? "SPACE dump  ENTER open  W wifi"
               : host::updateReady()                        ? "SPACE dump  ENTER open  U update"
                                                            : "SPACE dump  ENTER open  1-4 quick";
    }

    void move(int delta) {
        if (_primary.empty()) return;
        _sel = (_sel + delta + static_cast<int>(_primary.size())) % static_cast<int>(_primary.size());
        sfx::select(); invalidate();
    }

    void open(int slot) {
        if (slot < 0 || slot >= static_cast<int>(_primary.size())) return;
        sfx::confirm(); shell::pushById(_primary[slot]->id);
    }

    std::vector<const Descriptor*> _primary;
    int _sel = 0;
    bool _spaceArmed = false;
    bool _grid = false;  // false = Talk circle, true = More (the six-surface grid)
    nod::TalkFocus _focus = nod::FOCUS_TALK;
    uint32_t _lastAnim = 0;
    const char* _hints = "";
};

}  // namespace

const char* linkSentence(bool quiet) {
    if (quiet && (millis() - Sys.bootMillis <= 12000 || Cfg.fieldMode)) return nullptr;
    if (!Sys.wifiConnected) return "No Wi-Fi. Press W to connect.";
    if (!host::configured()) return "Not paired. Control > Pair.";
    if (!Sys.hostOnline) return "Core is off. Start it on PC.";
    return nullptr;
}

App* makeHome() { return new HomeApp(); }

}  // namespace apps
}  // namespace maz
