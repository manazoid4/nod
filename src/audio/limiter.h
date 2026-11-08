// Soft limiter: linear below 60% of full scale, then a smooth knee that never
// exceeds ~90%. Hard clipping at high speaker volume was a main crackle source.
#pragma once
#include <stddef.h>
#include <stdint.h>

namespace maz {
namespace audio {

inline void softLimit(int16_t* s, size_t n) {
    constexpr float kKnee = 0.6f * 32768.f, kRoom = 0.3f * 32768.f;
    for (size_t i = 0; i < n; ++i) {
        const float a = s[i] < 0 ? -(float)s[i] : (float)s[i];
        if (a <= kKnee) continue;
        const float t = (a - kKnee) / kRoom;
        const float y = kKnee + kRoom * (t / (1.f + t));  // asymptote 0.9
        s[i] = (int16_t)(s[i] < 0 ? -y : y);
    }
}

}  // namespace audio
}  // namespace maz
