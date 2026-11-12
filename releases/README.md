# Piblo betas

These are early test releases. See [manifest.json](manifest.json) for exact artifacts, SHA-256 hashes and test limits.

## Windows

1. Download `Piblo-Setup-0.2.0-beta.1.exe` and `SHA256SUMS.txt` from the [Windows beta](https://github.com/manazoid4/piblo/releases/tag/app-v0.2.0-beta.1).
2. Compare `Get-FileHash .\Piblo-Setup-0.2.0-beta.1.exe -Algorithm SHA256` with the checksum file.
3. Run the installer on Windows 10/11 x64. **Unsigned beta: Windows SmartScreen will warn; click More info, Run anyway**.
4. Follow setup in Piblo. Core needs Python 3.10+ with pip, internet access for its initial dependencies, and the device on the same Wi-Fi for pairing.

The beta uses the existing `app-latest` update feed and its `beta.yml` channel. Installer execution, real device pairing and installing an automatic update still need physical testing.

## Android

1. Download `Piblo-Android-0.1.1-beta.apk` and `SHA256SUMS.txt` from the [Android beta](https://github.com/manazoid4/piblo/releases/tag/android-v0.1.1-beta).
2. Check the APK's SHA-256 against the checksum file, then open it on Android 8.0+ (API 26+).
3. Allow **Install unknown apps** for the browser or file manager used to open it. Install Piblo, then turn that permission off again.
4. Connect to Core on the same network and enable notification access only if you want notification forwarding.

The APK is signed with a dedicated, locally held Piblo beta key. It is not on Google Play and has not been tested on a physical phone. A debug build uses a different signing key: replacing it requires uninstalling it, which removes its local data. Back up anything needed first.

## Rollback

Quit Piblo before uninstalling. Keep your previous installer/APK and back up local settings before changing versions. Reinstall the previous version from [Windows release history](https://github.com/manazoid4/piblo/releases?q=app-v) or [Android release history](https://github.com/manazoid4/piblo/releases?q=android-v). These are the first published Windows/Android betas, so no earlier release of either component is available yet. Android downgrades or signing-key changes can require uninstalling, deleting local data. Hardware firmware is unchanged by these installers.
