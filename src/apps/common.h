// Piblo — small shared pieces every app screen needs.
#pragma once
#include <string>
#include <vector>

#include <phone_text.h>

#include "../audio/dictate.h"
#include "../core/keys.h"
#include "../storage/store.h"
#include "../ui/ui.h"

namespace maz {
namespace apps {

// A one-line text field driven by the physical keyboard. Deliberately not a
// text editor: on a 240px panel, a field that scrolls horizontally and takes
// ENTER as "done" is the interaction that actually works.
//
// One component, four input methods with a visible switch (draw() shows
// KEYS, CAPS, PHONE or the dictation meter):
//   * physical keys, with cursor (LEFT/RIGHT), Delete and Backspace;
//     Shift and symbols already arrive as shifted chars from the keyboard
//     decoder, and double Shift (two presses, nothing between) toggles CAPS.
//   * Ctrl+SPACE dictation, as before.
//   * phone keyboard text (POST /buddy/text), a literal insert via
//     phone_text::applyPhoneText — never a key, never an approve.
//   * quick phrases: Ctrl+P inserts the next saved shortcut (Snippets),
//     Ctrl+H inserts the next recent submission (remember()); both are
//     capped at `limit` and never partially inserted.
//
// The visible field registers itself as the phone target on every draw();
// the phone router only inserts into that field and goes stale after
// kPhoneTargetMs, so a hidden field (list mode, popped screen) correctly
// answers "no field". Word suggestions are deliberately skipped: the flash
// budget for them is not there (see docs/EASY-MODE-HANDOVER.md).
struct TextField {
    std::string text;
    size_t      limit = 120;
    size_t      cursor = 0;
    bool        caps = false;

    static constexpr uint32_t kPhoneTargetMs = 2000;

    ~TextField() {
        if (phoneTargetSlot() == this) phoneTargetSlot() = nullptr;
    }

    static TextField*& phoneTargetSlot() { static TextField* t = nullptr; return t; }
    static uint32_t&   phoneTargetAtSlot() { static uint32_t t = 0; return t; }
    static TextField*  phoneTarget() { return phoneTargetSlot(); }
    static bool        phoneTargetFresh(uint32_t now) {
        return phoneTargetSlot() && (now - phoneTargetAtSlot()) <= kPhoneTargetMs;
    }

    // Copy of submitted text for Ctrl+H recall. Screens call this when they
    // save; passwords and tokens never call it.
    void remember() {
        if (text.empty()) return;
        auto& h = historySlot();
        if (!h.empty() && h.back() == text) return;
        h.push_back(text);
        while (h.size() > 5) h.erase(h.begin());
    }

    // Literal phone insert at the cursor (focused field assumed; the router
    // checks freshness first). Never submits: "send" inserts only.
    phone_text::Status applyPhone(const std::string& phone, phone_text::Mode mode) {
        syncCursor();
        phone_text::Status s = phone_text::applyPhoneText(text, limit, cursor, mode, phone, true);
        if (s == phone_text::Status::Inserted) {
            seenSize = text.size();
            lastPhoneAt = millis();
            flash(mode == phone_text::Mode::Replace ? "replaced" : "phone text in");
        } else if (s == phone_text::Status::TooLong) {
            flash("too long");
        } else if (s == phone_text::Status::Unsupported) {
            flash("unsupported chars");
        }
        return s;
    }

    // Hold Ctrl+SPACE and talk. SPACE alone cannot be the trigger here — in a
    // text field that is a space — and Ctrl+SPACE is otherwise unbound.
    static bool isDictateKey(const KeyEvent& e) {
        return e.code == KEY_SPACE && (e.mods & MOD_CTRL);
    }

    // Returns true if the key was consumed.
    bool onKey(const KeyEvent& e) {
        if (isDictateKey(e)) {
            if (e.down) {
                if (!dictate::active(this)) dictate::start(this);
            } else if (dictate::state() == dictate::State::Listening) {
                dictate::stop();
            }
            return true;
        }
        // Double Shift toggles CAPS. Any character resets the window, so
        // alternating-case typing can never false-trigger it.
        if (e.isMod && e.code == KEY_LEFTSHIFT && e.down) {
            const uint32_t now = millis();
            if (lastShiftAt && now - lastShiftAt < 500) caps = !caps;
            lastShiftAt = now;
            return true;
        }
        if (!e.down) return false;
        // ESC while the mic is open abandons the dictation instead of leaving
        // the screen out from under a recording.
        if (dictate::active(this) && e.code == KEY_ESC) {
            dictate::cancel();
            return true;
        }
        syncCursor();
        if ((e.mods & MOD_CTRL) && e.code == KEY_P) {
            insertNext(store::loadSnippets(), snipAt);
            return true;
        }
        if ((e.mods & MOD_CTRL) && e.code == KEY_H) {
            auto& h = historySlot();
            ++histAt;
            const std::string phrase = h.empty() ? "" : h[histAt % h.size()];
            insertAtCursor(phrase);
            return true;
        }
        if (e.code == KEY_LEFT) {
            if (cursor > 0) cursor = cursor > 1 ? cursor - 1 : 0;
            return true;
        }
        if (e.code == KEY_RIGHT) {
            if (cursor < text.size()) ++cursor;
            return true;
        }
        if (e.code == KEY_DELETE) {
            if (cursor < text.size()) text.erase(cursor, 1);
            afterEdit();
            return true;
        }
        if (e.code == KEY_BACKSPACE) {
            if (cursor > 0) {
                text.erase(cursor - 1, 1);
                --cursor;
            }
            afterEdit();
            return true;
        }
        if (e.ch >= 32 && e.ch < 127) {
            // Switch bounce guard: the TCA8418 reports transitions only (a
            // held key sends one down + one up), so a duplicate down of the
            // same key inside 30 ms is a bounce, never real typing.
            const uint32_t now = millis();
            if (e.code == lastCode && now - lastAt < 30) return true;
            lastCode = e.code;
            lastAt = now;
            lastShiftAt = 0;
            char c = e.ch;
            if (caps && c >= 'a' && c <= 'z') c = static_cast<char>(c - 'a' + 'A');
            if (text.size() < limit) {
                text.insert(cursor, 1, c);
                ++cursor;
            }
            afterEdit();
            return true;
        }
        return false;
    }

    // Called from draw(), so a screen receives its transcript without needing
    // an update() hook of its own.
    void collect() {
        std::string spoken;
        if (!dictate::take(this, spoken)) return;
        if (!text.empty() && text.back() != ' ') text.push_back(' ');
        for (char c : spoken) {
            if (text.size() >= limit) break;
            text.push_back(c);
        }
        seenSize = text.size();
        cursor = text.size();
    }

    void draw(M5Canvas& g, int x, int y, int w, const char* placeholder = "") {
        phoneTargetSlot() = this;
        phoneTargetAtSlot() = millis();
        collect();
        syncCursor();
        ui::panel(g, x, y, w, 18);
        g.setFont(&fonts::Font2);
        g.setTextDatum(top_left);

        if (dictate::active(this)) {
            const bool listening =
                dictate::state() == dictate::State::Listening;
            // A live meter rather than a spinner: you need to know the mic is
            // hearing you, not merely that something is happening.
            if (listening) {
                const int bar = static_cast<int>((w - 8) * dictate::level());
                g.fillRect(x + 4, y + 14, bar < 2 ? 2 : bar, 2, theme::ACCENT2);
            }
            g.setTextColor(listening ? theme::ACCENT2 : theme::WARN,
                           theme::PANEL);
            g.drawString(listening ? "listening..." : "transcribing...", x + 4,
                         y + 1);
            return;
        }

        const bool empty = text.empty();
        g.setTextColor(empty ? theme::DIM : theme::TEXT, theme::PANEL);

        // Show the cursor and its neighbourhood; with the cursor at the end
        // this is exactly the old tail view.
        size_t maxChars = (w - 10) / 8;
        std::string chip;
        if (!msg.empty() && millis() - msgAt < 2000) chip = msg;
        else if (millis() - lastPhoneAt < 2000) chip = "PHONE";
        else if (caps) chip = "CAPS";
        if (!chip.empty()) maxChars = maxChars > 7 ? maxChars - 7 : 8;
        std::string shown;
        size_t start = 0;
        if (empty) {
            shown = placeholder;
        } else {
            if (text.size() > maxChars)
                start = cursor <= maxChars ? 0 : cursor - maxChars;
            shown = text.substr(start, maxChars);
            if ((millis() / 500) % 2) shown.insert(cursor - start, "_");
        }
        g.setTextColor(empty ? theme::DIM : theme::TEXT, theme::PANEL);
        g.drawString(shown.c_str(), x + 4, y + 1);
        if (!chip.empty()) {
            g.setTextDatum(top_right);
            g.setTextColor(theme::DIM, theme::PANEL);
            g.drawString(chip.c_str(), x + w - 4, y + 1);
        }
    }

private:
    void syncCursor() {
        // A screen that assigns `text` directly (note reload) lands the
        // cursor at the end, which is what an editor's next type expects.
        if (text.size() != seenSize) {
            cursor = text.size();
            seenSize = text.size();
        }
        if (cursor > text.size()) cursor = text.size();
    }
    void afterEdit() { seenSize = text.size(); }
    void flash(const char* m) { msg = m; msgAt = millis(); }
    static std::vector<std::string>& historySlot() {
        static std::vector<std::string> h;
        return h;
    }
    void insertAtCursor(const std::string& phrase) {
        syncCursor();
        if (!phrase.empty() && text.size() + phrase.size() <= limit) {
            text.insert(cursor, phrase);
            cursor += phrase.size();
        } else if (!phrase.empty()) {
            flash("too long");
        }
        seenSize = text.size();
    }
    void insertNext(const std::vector<std::pair<std::string, std::string>>& items, size_t& at) {
        if (items.empty()) {
            flash("no shortcuts");
            return;
        }
        const std::string& value = items[at % items.size()].second;
        ++at;
        insertAtCursor(value);
    }

    size_t seenSize = 0;
    size_t snipAt = 0, histAt = 0;
    uint8_t lastCode = KEY_NONE;
    uint32_t lastAt = 0, lastShiftAt = 0, lastPhoneAt = 0, msgAt = 0;
    std::string msg;
};

// Shared list cursor: keeps selection and scroll window in step so every list
// screen in Piblo behaves identically.
struct ListCursor {
    int sel   = 0;
    int first = 0;

    void clamp(int count) {
        if (count <= 0) {
            sel = first = 0;
            return;
        }
        if (sel >= count) sel = count - 1;
        if (sel < 0) sel = 0;
        if (sel < first) first = sel;
        // The header takes the first body row, so lists show LIST_ROWS items, not ROWS_VISIBLE.
        if (sel >= first + theme::LIST_ROWS)
            first = sel - theme::LIST_ROWS + 1;
        if (first < 0) first = 0;
    }
    bool onKey(const KeyEvent& e, int count) {
        if (!e.down) return false;
        if (e.code == KEY_UP) {
            sel--;
            clamp(count);
            return true;
        }
        if (e.code == KEY_DOWN) {
            sel++;
            clamp(count);
            return true;
        }
        return false;
    }
};

}  // namespace apps
}  // namespace maz
