// Piblo — phone keyboard mode router.
//
// The Core forwards phone text as /buddy/events ring entries of kind
// "text_input" (see docs/protocol/PHONE-KEYBOARD.md). This glue receives one
// event at a time and routes it to exactly one place: the currently drawn
// TextField (apps/common.h), as a literal insert. If no field is focused, a
// short hint shows and the Core is acked "no_field". An ack is always filed
// (inserted / no_field / too_long) so the phone's GET has an answer.
//
// Safety: this path never synthesises a key event and never touches the
// approval queue. While an approval or alert overlay is up, phone text is
// answered "no_field" and dropped (see invariants, integration brief).
#pragma once

#include <stdint.h>

#include "../net/mazhost.h"

namespace maz {
namespace phone {

void onTextInput(const host::AgentEvent& ev);
void update();  // pump queued acks; called from the shell loop

}  // namespace phone
}  // namespace maz
