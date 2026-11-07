# Nod: launch gates

Rule: do not launch the campaign or accept any pledge until every gate is MET with the evidence listed. "Met" means the evidence exists in the repo or a linked file, not that someone believes it works. Statuses are as of 6 Nov 2026, from the repo documents. Update as evidence arrives.

| # | Gate | Status | Evidence required |
|---|---|---|---|
| 1 | Three workflows demonstrated on video on the real Cardputer ADV | IN PROGRESS | Uncut video per workflow (suggested: CALL with spoken reply, voice capture, agent approval) showing the device and PC together; firmware and Nod Core versions visible; test notes with date and pass/fail. Repo docs say nothing is yet independently verified on hardware; owner reports v1.0.2 boots. |
| 2 | 100 approval trials, at least 95% complete, zero unauthorised executions | NOT MET | Log of 100 runs with timestamps, firmware and Core versions and categorised failures; proof that timeout, disconnect, duplicate and stale requests all deny; a short threat-model note (pairing, local network, rogue device, token theft). Zero unapproved executions is a hard requirement; one failure resets the count after the fix. |
| 3 | Five outsider novice setup tests | NOT MET | Five people who did not build Nod set it up from the written guide on their own Windows PC. Record time, where they got stuck and whether they finished; fix and re-test. Get consent for any recordings. |
| 4 | Feasible product format and two real written supplier quotes | NOT MET | Format decision (software-only plus own board, or printed-case kit); two written quotes with minimum order quantities and lead times (for example boards, print service or filament and printer capacity, packaging); one finished printed case that fits the real device and keeps USB-C, speaker, microphone and keyboard accessible. |
| 5 | UK compliance assessment | NOT MET | Written assessment covering: radio and EMC (the Cardputer is a certified module, but the finished product still needs assessment; keep the module's certification documents); battery transport (UN38.3 test summary from the supplier, carrier acceptance); WEEE producer duties; GPSR and UK consumer law (labelling, instructions, safety information, returns). Take professional advice where unsure and add the costs to `ECONOMICS.csv`. |
| 6 | Complete unit economics | NOT MET | `ECONOMICS.csv` filled from real quotes for every volume; bad-case run; funding goal justified by it; VAT position confirmed with an accountant. |
| 7 | Uncut demo and real opt-in interest | NOT MET | One uncut video of the core workflow with no CGI or invented functions; real double opt-in signups (the current site uses a mailto link, not a true signup); verified signup count reported as it is. Threshold for "enough interest": [owner to decide]. |

Also required before launch:
- Kickstarter's current rules and hardware/prototype guidance read; no renders presented as real product photos.
- A privacy statement covering voice audio and AI providers.
- No claims about streaming-service subtitles, offline AI, free cloud AI or ship dates without evidence.
- No precise owner location published.
- The owner personally approves the final page. Nothing goes live automatically.
