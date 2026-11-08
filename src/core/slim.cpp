// Flash diet: stubs for prebuilt-library code nothing here needs, wired up with
// -Wl,--wrap=... in platformio.ini so the linker drops the real implementations.
//  - mbedtls_strerror: only used to format TLS error text for log_e(); CORE_DEBUG_LEVEL=0
//    already discards those logs. Dropping it frees libmbedcrypto error.c (~15 KB).
//  - esp_core_dump_*: panic core dumps to flash are never decoded on this product; a panic
//    still prints its backtrace and reboots.
#include <stddef.h>

extern "C" {

void __wrap_mbedtls_strerror(int, char* buf, size_t len) {
    if (buf && len) buf[0] = 0;
}

// Piblo is only ever a TLS client; refusing server handshakes drops mbedtls ssl_srv.c (~7 KB).
int __wrap_mbedtls_ssl_handshake_server_step(void*) { return -0x7100; /* BAD_INPUT_DATA */ }


void __wrap_esp_core_dump_init(void) {}

void __wrap_esp_core_dump_write(void*) {}

}  // extern "C"
