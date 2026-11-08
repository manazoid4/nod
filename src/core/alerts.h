// Piblo - generic alerts overlay (reminder / webhook / task-done ...) with Piblo Buddy.
//
// Events arrive on the existing Core /buddy/events poll (kind "alert"). The overlay shows
// Buddy + title/body, plays the priority pattern from alert_policy.h (Quiet-aware) and
// answers with A/ENT = ack, S = snooze, ESC = hide. The answer is POSTed back to Core,
// which stores the outcome. Approvals are NOT handled here: they keep using approvals.cpp
// and the existing authority path (Y/N), and always sit above this overlay.
#pragma once
#include <M5Unified.h>

#include "app.h"
#include "../net/mazhost.h"

namespace maz {
namespace alerts {

void onEvent(const host::AgentEvent& ev);  // kind == "alert" only
void update();                             // answer submit, repeat chirp
bool active();                             // overlay owns the keyboard
bool handleKey(const KeyEvent& e);
void render(M5Canvas& g);

}  // namespace alerts
}  // namespace maz
