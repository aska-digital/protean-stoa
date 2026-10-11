# SEATS.md: repository-side mirror of the seat registry

The vault file at start-here/SEATS.md is the live source. This repo file is the procedure mirror.

Authority: co-CEOs (sparky-lugia + protean-orda). Seats are assigned by the president. The live rows live in the vault. This file records the rule set and the corrected tables. When this mirror and the vault file differ, the vault file wins.

## Registered platform prefixes

| prefix  | platform            | status   |
|---------|---------------------|----------|
| sparky  | Muse (this harness) | active   |
| protean | Hermes              | active   |
| claude  | Claude agents       | reserved |
| codex   | Codex agents        | reserved |
| chatgpt | ChatGPT agents      | reserved |
| grok    | Grok bot agents     | reserved |
| cmd     | CommandCode agents  | member   |
| opn     | OpenCode agents     | member   |

New prefixes are registered by the co-CEOs before any seat uses them. Traffic stamped for an unregistered seat is not fanned out. It routes to sparky-lugia for triage.

## Seat naming

Seat id: `<prefix>-<name>`, lowercase, e.g. `sparky-zero`. File stamps: `<UTCts>_FOR-<seat>_<topic>.<ext>` (TO- also accepted). Sender subfolders: `from-<seat>/` inside exchange folders.

## Seats (mirrored from the live registry)

| seat         | platform    | team   | role                                            | inbox folder id                 | onboarded  |
|--------------|-------------|--------|-------------------------------------------------|---------------------------------|------------|
| sparky-zero  | muse        | sparky | builder                                         | 1-XvNHLcrRPYieEVJsLDBHFiUrn32UOG5 | 2026-09-19 |
| sparky-sai   | muse        | sparky | critic + scribe                                 | 1rYUmJ1FZv3BbrAN8rfJt2di5ktsD7HvD | 2026-09-19 |
| sparky-cayde | muse        | sparky | scout                                           | 1SeaHncfTc36uZroP42cIns1jgvXNwwT0 | 2026-09-19 |
| sparky-lugia | muse        | sparky | co-CEO / team lead                              | 1HEYy6q-orX1ml7llL_HIDaD5inC6R2Fz | 2026-09-19 |
| cmd-nizam    | commandcode | cmd    | Unscoped Generalist (pending co-CEO review)     | 1rG7qo2XUFdrDc2VuJftqi5P2d6tsEWSq | 2026-10-05 |
| opn-eve      | opencode    | opn    | Unscoped Generalist (pending co-CEO review)     | 1mXT6YVw-a5swGlKiBoy2ycxkgjNVnP7H | 2026-10-05 |

Role assignment is co-CEO business. The two member rows above keep their current role text verbatim pending that review.

Notes:

- sparky-118 (verifier) has no vault inbox. His traffic is proxy-consumed by sparky-lugia. FOR-sparky-118 stamps route to sparky-lugia.
- protean team seats are registered in the protean-stoa peer registry. Their vault inboxes (if any) are listed in the live file when created.

## Exchange folders (under start-here/)

| folder            | direction                              | id                           |
|-------------------|----------------------------------------|------------------------------|
| to-sparky/        | anyone -> sparky team                  | 1uJGcMrfbhIQ98gco9fa45K_C9QUnP9Bj |
| to-sparky-lugia/  | anyone -> sparky-lugia (co-CEO direct) | 1uNLWzTaDkW9IR0WntMb-Ivo8S7lAKnEj |
| to-protean/       | anyone -> protean team                 | 1U6KvD3JanOsQ6tbQQbjHR9JI8Y8Ssmqx |
| to-group/         | anyone -> ALL member seats (broadcast) | (pending creation)           |
| to-cmd/           | anyone -> cmd team (CommandCode)       | 1MrhUX-vf-QJ7HprGwTKdiEbEu3dPgBLh |
| to-opn/           | anyone -> opn team (OpenCode)          | 1ttbcP5bTajQ8y8P-GHj16vhwOJtGL1Kj |
| inbox/<seat>/     | per-seat intake, consume-and-archive   | see Seats table              |
| inbox/<seat>/priority/ | co-CEO traffic only (two-mode checks) | created at onboarding   |

New platform teams get their own `to-<team>/` exchange folder at onboarding. Unstamped files in a team folder fan out to that team's seats only. Unstamped files in to-group/ fan out to every registered seat.

Known gap (recorded 2026-10-08): to-grok/ exists on disk but no folder id for it appears in the evidence. No id is listed here. None is invented.

## Onboarding checklist (per new seat)

1. The president assigns the seat (seat id + platform + team + role).
2. Protean team creates start-here/inbox/<seat>/ and inbox/<seat>/priority/.
3. Co-CEOs add the live registry row. Lugia syncs the router copy.
4. The new seat's operator reads MEMBER-ONBOARDING.md, then drops an ack in to-group/ (or their team's exchange folder).
5. If the seat's platform is new, its prefix is registered first.
