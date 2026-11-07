// Crash-safe saves for the device store. Works over any FS with
// exists/remove/rename(const char*) (fs::FS on the device, a fake in tests).
#pragma once
#include <string>

namespace nod {

template <class Fs>
void removeIfThere(Fs& fs, const std::string& p) {
    if (fs.exists(p.c_str())) fs.remove(p.c_str());
}

// A plain truncate-then-write leaves an empty or half file if the device
// restarts mid-save; records.tsv and tasks.tsv hold everything, so that lost
// everything. Write a temp file first, then swap it in.
template <class Fs, class Write>
bool replaceFile(Fs& fs, const std::string& path, Write write) {
    const std::string tmp = path + ".tmp", bak = path + ".bak";
    removeIfThere(fs, tmp);
    if (!write(tmp)) { removeIfThere(fs, tmp); return false; }
    removeIfThere(fs, bak);
    if (fs.exists(path.c_str()) && !fs.rename(path.c_str(), bak.c_str())) {
        removeIfThere(fs, tmp);
        return false;
    }
    if (!fs.rename(tmp.c_str(), path.c_str())) {
        fs.rename(bak.c_str(), path.c_str());
        return false;
    }
    removeIfThere(fs, bak);
    return true;
}

// A restart between the two renames leaves only the .bak: put it back.
template <class Fs>
void recoverFile(Fs& fs, const std::string& path) {
    const std::string bak = path + ".bak";
    if (!fs.exists(path.c_str()) && fs.exists(bak.c_str()))
        fs.rename(bak.c_str(), path.c_str());
}

// Before the clock syncs, every boot starts at 1970-01-01 00:00:00, so a
// timestamp name repeats after a restart and would overwrite an older note.
template <class Exists>
std::string uniquePath(const std::string& stem, const std::string& ext, Exists exists) {
    std::string p = stem + "." + ext;
    for (int n = 1; exists(p) && n < 1000; ++n) p = stem + "-" + std::to_string(n) + "." + ext;
    return p;
}

}  // namespace nod
