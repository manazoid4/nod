// Emits preview/layouts.js from the REAL firmware headers so the HTML preview cannot drift from them.
#include <cstdio>
#include "../include/home_layout.h"
using namespace nod;
int main() {
    printf("window.NOD_PROFILES=[");
    for (int p = 0; p < kProfileCount; p++) {
        const DisplayProfile& d = kProfiles[p]; HomeLayout L = computeHome(d.w, d.h);
        printf("%s{id:\"%s\",name:\"%s\",w:%d,h:%d,verified:%s,bar:[%d,%d,%d,%d],foot:[%d,%d,%d,%d],cards:[",
               p ? "," : "", d.id, d.name, d.w, d.h, d.verified ? "true" : "false",
               L.statusBar.x, L.statusBar.y, L.statusBar.w, L.statusBar.h, L.footer.x, L.footer.y, L.footer.w, L.footer.h);
        for (int i = 0; i < CARD_COUNT; i++)
            printf("%s{l:\"%s\",s:\"%s\",r:[%d,%d,%d,%d]}", i ? "," : "", kCardLabel[i], kCardHint[i],
                   L.cards[i].x, L.cards[i].y, L.cards[i].w, L.cards[i].h);
        printf("]}");
    }
    printf("];\n");
}
