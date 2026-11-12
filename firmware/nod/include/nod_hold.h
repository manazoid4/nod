// Piblo - The Nod: hold-to-approve timing. Pure (no hardware) so
// firmware/nod/tests can check it on a PC. A big action needs Y/Enter HELD, never tapped.
#pragma once
#include <stdint.h>

namespace maz {
namespace nod {

constexpr uint32_t HOLD_MS = 800;   // how long Y/Enter must stay down to approve a nod

inline bool holdDone(uint32_t heldMs) { return heldMs >= HOLD_MS; }

// 0..100 for the filling bar; clamps at 100.
inline uint8_t holdPercent(uint32_t heldMs) {
    return heldMs >= HOLD_MS ? 100 : static_cast<uint8_t>(heldMs * 100u / HOLD_MS);
}

}  // namespace nod
}  // namespace maz
