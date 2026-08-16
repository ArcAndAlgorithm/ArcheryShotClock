# Archery Timer

A wireless, ESP32-based shot clock and match timing system for target archery, built to
comply with [World Archery Book 3 — Target Archery](docs/requirements.md) rules. Designed
for indoor and outdoor use, covering both qualification rounds and match play, across
Individual, Team, and Mixed Team events.

One **Controller** unit (buttons, keypad, and a built-in web UI) drives any number of
**Display** units (RGB dot-matrix panels) and **Buzzer** units (audio signals) over
low-latency ESP-NOW, so a single director of shooting can run a shot clock across a large
field with several displays in sync.

## Features

- **All World Archery timing modes** — individual and team, alternating and
  non-alternating, qualification and match play, shoot-offs, and practice sessions, per
  Article 11.2/11.3.
- **Multiple synchronised displays** — pair as many RGB dot-matrix panels as a field
  needs; all show the same clock and light state (red/green/yellow) in sync.
- **Optional match logic** — end/arrow tracking, set-play and cumulative scoring, togglable
  independently of the core timing engine.
- **Web UI** — setup, live monitoring, and remote control, hosted directly on the
  Controller (no extra hardware required).
- **Dedicated audio signalling** — separate buzzer units generate the exact sound-signal
  patterns required by Article 11.3, plus an optional PA line-out.
- **Suspension/resume handling** — correctly recalculates remaining time per Article
  11.2.4 for both individual and team events.
- **Emergency stop** — a dedicated physical control that works independently of Wi-Fi/UI
  state.

## Project status

🚧 **In development.** Full requirements, architecture, and design decisions are documented
in [`docs/requirements.md`](docs/requirements.md). See that document for the complete
functional specification, timing state machines, and rulebook article references.

## Repository structure

```
archery-timer/
├── firmware/
│   ├── common/       # Shared code: ESP-NOW message schema, signal codes, timing logic
│   ├── controller/   # Buttons, keypad, Wi-Fi AP, web server, ESP-NOW broadcast master
│   ├── display/       # RGB dot-matrix rendering, ESP-NOW receive-only client
│   └── buzzer/        # Audio signal generation, ESP-NOW receive-only client
├── webui/             # Web UI source, built into the controller's firmware image
├── docs/              # Requirements, protocol spec, rulebook-to-code mapping
├── tools/             # Python scripts (node emulator, load testing, etc.)
├── tests/             # Unit tests
└── platformio.ini     # Multi-target build configuration
```

## Tech stack

- **Firmware:** C++ on ESP-IDF, built with [PlatformIO](https://platformio.org/)
- **Web UI:** HTML/CSS/vanilla JavaScript, served from the Controller over WebSocket + HTTP
- **Tooling:** Python (test/simulation scripts, CI helpers)

See [`docs/requirements.md`](docs/requirements.md) §12 for the full rationale.

## Getting started

> Build instructions will be added once the firmware scaffolding is in place.

## Hardware

- ESP32 modules (Controller, Display ×N, Buzzer ×N)
- RGB dot-matrix LED panels (Display units)
- Speaker/buzzer (Buzzer units), optional PA line-out
- IP-rated enclosures for outdoor use

Exact hardware models and part numbers are still being finalised and will be added here.

## Rulebook compliance

This project is built against **World Archery Book 3 — Target Archery, Version
2026-08-15**. Every timing mode and match-logic behaviour in the requirements document is
traced back to the specific article it implements — see
[`docs/requirements.md`](docs/requirements.md) and
[`docs/rulebook-mapping.md`](docs/rulebook-mapping.md) (once available) for full
traceability. This is an independent, unofficial implementation and is not affiliated with
or endorsed by World Archery.

## License

> Add a license (e.g., MIT, Apache 2.0, or GPLv3) before making the repository public.  address).
- All paired displays for a session receive **identical state** (same clock, same lights);
  this is what allows 2–4 units to cover a large field for one match.
- One or more displays may be flagged in the web UI as **"scoring display"** so that in
  alternating individual matches they also render running score/set-points instead of (or
  alongside) the countdown, per the use case described.

---

## 3. Controller — Physical Inputs

| Control | Function |
|---|---|
| **Start** | Begins the shooting period for the current mode (per Article 11.2/11.3 sequencing — see §5). |
| **Stop** | Immediately halts the clock and triggers the "shooting time finished" signal sequence (Article 11.3.1, RED / two sound signals), even if arrows remain. |
| **Next End** | Advances to the next end/set once scoring for the current end is complete; resets arrow/end counters as appropriate for the active mode. |
| **Reset Current End** | Resets the clock and arrow count for the *current* end without advancing (e.g., false start, misfire before first arrow) — does not touch scores already recorded for prior ends. |
| **Pause / Resume** | Implements Article 11.2.4 suspension logic (see §5.6): freezes the clock and lights, and on resume recalculates remaining time per the applicable rule. |
| **Emergency Stop** | Dedicated physical button, independent of Wi-Fi/web UI responsiveness, that immediately triggers the ≥5-signal emergency sequence (Art. 11.3.3) on every paired buzzer/display and halts all clocks. Must work even if the web UI is unresponsive or the companion device is disconnected — it should trigger directly from the button's interrupt handler, not depend on the same code path as the web UI's emergency control. |
| **Keypad** | Numeric entry for arrow values (0/M, 1–10, X) when match-logic scoring is enabled, and for mode/parameter selection as a fallback to the web UI. |

All of the above must also be triggerable from the web UI, so the director can operate
from a tablet if preferred — physical buttons are not the *only* path, per your note that
this may be easier to manage as a web interface long-term. However, **Start/Stop must have
guaranteed low-latency delivery** regardless of whether triggered locally (button) or
remotely (web UI over Wi-Fi) — this should be tested since Wi-Fi-triggered Start/Stop adds
a network hop the buttons don't have. Emergency Stop specifically should always be a
physical button (see table above) — it is the one control that must not depend on Wi-Fi
being up.

---

## 4. Web UI — Functional Requirements (Controller-hosted)

1. **Session setup**
   - Select event type: Individual / Team / Mixed Team
   - Select round type: Qualification / Match Play (non-alternating) / Match Play
     (alternating) / Finals (alternating) / Shoot-off
   - Select division: Recurve / Compound / Barebow (relevant for set-play vs cumulative
     default, and end/set sizing)
   - Select distance category: Long distance / Short distance (relevant to some tie/shoot-
     off rules, may be informational only in v1 if not driving timing)
   - Select event class: WRE/other-international (Article 11.2.1.1 timing) vs. all other
     events (Article 11.2.1.2 timing, with the 40s→30s reduction option)
   - Arrows per end (3 or 6, per Article 10.1) — default by mode, overridable
   - Enable/disable Match Logic module
   - If Match Logic enabled: select Set-play or Cumulative scoring
2. **Device management** — pair/unpair displays and buzzer units; assign a display as
   "scoring display"; live connectivity status per unit (last-seen heartbeat).
3. **Live monitoring** — mirror of what's on the displays (clock, lights, end/arrow count,
   scores) for the director's own reference.
4. **Score entry** (if Match Logic enabled) — per-arrow entry, editable before "Next End"
   is confirmed, matching the human workflow in Article 12.1.3 (call out, record, verify).
5. **Manual time-limit extension** — per Article 11.2.2 ("time limit may be extended in
   exceptional circumstances"), the director can add time to the current period.
6. **Audit/event log** — timestamped log of all Start/Stop/Pause/Reset/score-entry events
   for post-match reference and dispute resolution (supports Chapter 15 — Questions and
   Disputes, and Chapter 17 — Appeals, even though the system doesn't adjudicate).

---

## 5. Timing Engine — Modes & State Machines

All modes must be selectable at setup (per your requirement that all modes be supported).
Below, each state machine references the governing article(s).

### 5.1 Common signal vocabulary (Article 11.3.1, 11.3.3)

| Signal | Meaning | Trigger |
|---|---|---|
| RED (steady), 2 sound signals | Athletes occupy shooting line | Start of a shooting-line-occupation phase |
| GREEN, 1 sound signal | Shooting begins | 10s after RED |
| YELLOW | 30s warning before time expires | Automatic, 30s before period end (not used in alternating Finals shooting) |
| RED, 2 sound signals | Shooting time finished — stop | Clock reaches 0, or Stop pressed |
| RED (post-completion), 3 sound signals | Scoring may begin | All required arrows shot, or time expired and line is clear |
| ≥5 sound signals | Emergency — all shooting must cease | Manual "Emergency Stop" control (must be reachable in 1 action from web UI and ideally a dedicated hold-to-trigger physical action) |
| 1 sound signal | Resume after suspension | Resume pressed after a suspension |

Both light state and digital clock must stay synchronised; per Article 11.3.1, **the
digital clock is authoritative** if there's ever a discrepancy — so the Display firmware
should treat the numeric countdown as ground truth and derive light colour from it, not
maintain light colour as independently-timed state.

### 5.2 Individual, non-alternating (Qualification / Match Play without alternate shooting)

- Per-arrow time: **30s** (WRE) or **40s**, reducible to 30s (other events) — Art. 11.2.1.1/.2
- Sequence: 10s occupy-line signal → GREEN/start → countdown for (arrows × per-arrow time)
  → YELLOW at 30s remaining → RED/stop at 0 or when all arrows shot and line clear → 3
  signals for scoring.
- End size: 3 or 6 arrows (config).

### 5.3 Individual, alternating shooting (Match Play Finals — Article 11.2.3.2, 11.1.4.1)

- Per-arrow time: **20s**, one arrow at a time, athletes alternate.
- Sequence:
  1. 10s signal — both athletes to the line.
  2. 1 signal — 20s clock starts for **Athlete A** (the athlete who shoots first, per
     11.1.4.1 seeding rule — director selects who goes first via UI at match start).
  3. On A's first arrow release **or** timeout, the director presses **Start** again —
     this both stops A's clock (if still running) and immediately starts B's 20s clock in
     one action (Decision OQ-1: Start is reused as the handoff trigger, not a separate
     button). Internally the state machine treats this as `HANDOFF`, distinct from the
     very first `START` of the match (which only begins A's clock and has no "stop the
     previous side" action to perform).
  4. Repeat until each athlete has shot their arrows for the set (3, per 11.1.4.1) or a
     "sure loss" early stop is invoked by the director (athlete may vacate — director
     marks this state manually, no auto-detection; a long-press or double-tap on Stop can
     be used to distinguish "match conceded" from a normal end-of-set Stop, to avoid
     accidental triggering — flag for firmware design).
  5. Time-out on either side (clock reaching 0 without a Start press) auto-advances to the
     opponent's clock and triggers the appropriate sound signal (per 11.2.3.2), without
     waiting for the director — this keeps the alternating rhythm moving even if the
     handoff button press is missed.
  - Scoring display flag (§2.3) is most relevant here — shows running set score to
    spectators between exchanges.
  - **Design note:** because Start is overloaded (first-press = begin match, subsequent
    presses = handoff), the firmware should track an explicit `current_shooter` state so
    the same physical action always does the right thing without the director needing to
    think about which press number they're on.

### 5.4 Team / Mixed Team, simultaneous shooting (Article 11.1.4.2)

- Per-arrow time: **20s** per arrow, whole-team clock.
- Team shoots 2 arrows per athlete, one athlete at a time crosses the 1m line; system does
  not need to track *which* athlete is shooting (no individual identification), only:
  - Total arrows for the end (6 for team, 4 for mixed team).
  - Elapsed/remaining time against the full end (20s × total arrows), not per-athlete.
- Yellow-card support (Article 13.6): director can flag a violation (early 1m-line cross,
  early arrow-from-quiver, release-aid hooked early) via a UI/keypad shortcut — this is a
  **judge decision the system records**, not something it auto-detects. When flagged, UI
  shows "yellow card active — athlete must restart behind 1m line" as a reminder; if the
  team proceeds anyway, the director marks "violation not corrected," which the Match
  Logic module (if enabled) uses to auto-forfeit the highest-scoring arrow of that end (per
  13.6.2) when scores are entered.

### 5.5 Team / Mixed Team, alternating shooting — Finals (Article 11.1.4.3)

- Per-arrow time: **20s**, team-level clock, alternating between the two teams.
- Sequence:
  1. Both teams behind 1m line.
  2. Higher-seeded team (per Qualification) shoots first — director selects at match
     start.
  3. Clock runs while Team A's members shoot one arrow each in rotation; when the *last*
     athlete of that phase returns behind the 1m line, the director presses **Start**
     (same handoff mechanism as §5.3, OQ-1) — this stops Team A's clock, displays their
     remaining time, and immediately starts Team B's fresh 20s-per-arrow clock in one
     action.
  4. Team B's clock runs until their last athlete of that phase returns and Start is
     pressed again, handing back to Team A.
  5. Repeat until both teams have shot 6 arrows (4 for Mixed Team) or time expires.
  6. Shoot-off: team that shot first in the match shoots first in the shoot-off;
     alternation after every single shot.

### 5.6 Suspension / Resume (Article 11.2.4) — available in both Qualification and Match

- On **Pause**: freeze the countdown, freeze light state, log timestamp and remaining
  time/arrows.
- On **Resume**:
  - **Individual (qualification/match, non-alternating):** remaining unshot arrows get the
    full per-arrow allocation again (30/40s, or 20s if alternating) — i.e., recalculated
    from arrows-not-shot, not a simple unpause (Art. 11.2.4.1).
  - **Team/Mixed Team:** compare the clock's remaining time at pause against
    (20s × remaining-unshot-team-arrows). If remaining time on the clock **exceeds** that
    value, resume from the actual remaining time. Otherwise, reset to
    20s × remaining-unshot-arrows (Art. 11.2.4.2).
  - In all cases, resumption always restarts from the shooting line (10s occupy-line
    signal replayed) — configurable per Art. 11.2.4's "including the 10-second signal"
    wording, i.e., the 10s signal is part of the resume sequence, not skipped.
- The engine needs a concept of **"arrows shot so far in this end"** even in pure-timing
  mode (Match Logic off), purely to support this recalculation — this should be a manual
  counter the director increments (e.g., a "+1 arrow" button), independent of full
  score entry.

### 5.7 AB/CD detail rotation (Article 11.1.1, 11.2.3.1)

- When configured for AB/CD rotation: 10s changeover signal between designated pairs
  occupying the line, repeating until all athletes on the target have shot.
- This is a **display/timing config flag** (rotation on/off) rather than a separate mode —
  it modifies the occupy-line phase of §5.2's sequence to repeat per pair rather than run
  once.

### 5.8 Shoot-offs

- Individual/team shoot-offs reuse the relevant mode's timing (single-arrow or set number
  of arrows) but as a **one-off end** outside the normal end/set counter — Match Logic
  should treat a shoot-off as a distinct, separately logged mini-round, not part of the
  normal cumulative/set tally, since ties are broken by closest-to-centre rules (Article
  12.5.2) which are outside this system's scope (manual judge call, but the system should
  provide a simple UI to record the outcome for the log).

### 5.9 Practice (Chapter 14)

- Simple Start/Stop signalling, no scoring, no per-arrow subdivision — "practice session"
  is effectively its own lightweight mode: start signal, running clock (director-set
  duration or open-ended), stop signal. No YELLOW warning required (not specified in
  Chapter 14).

---

## 6. Match Logic Module (togglable)

When enabled, layered on top of §5's timing engine:

### 6.1 Structure tracking
- End size: 3 or 6 arrows per Article 10.1 (or 2/4 for mixed team per relevant articles).
- End/set counter appropriate to the mode (e.g., sets to 6 points win for individual
  set-play per 12.1.4.1, 5 points for team per 12.1.4.2; 5 ends cumulative individual per
  12.1.4.3, 4 ends cumulative team per 12.1.4.4).

### 6.2 Scoring types
- **Set-play** (default for Recurve/Barebow, Art. 12.1.4.1/.2): each end, higher score gets
  2 set points, tie gets 1 each; first to 6 (individual) / 5 (team) wins. System should
  auto-declare a winner and lock further entry once the threshold is reached.
- **Cumulative** (default for Compound, Art. 12.1.4.3/.4): running total per end; winner is
  highest total after 5 ends (individual) / 4 ends (team).
- Manual override should be available (division defaults can be overridden per event
  format).

### 6.3 Arrow entry
- Numeric keypad or web UI, values 0/M, 1–10, X (inner ten), entered in descending order
  as called out (mirrors Art. 12.1.3 workflow) — the system doesn't need to enforce
  descending order, just accept and total the entered set.
- Support the "unshot arrow = miss" rule for team match play (Art. 12.2.2.3) — if the
  director marks an end complete with fewer than the expected arrow count, offer to
  auto-fill remaining as "M" per that article, rather than silently leaving them blank.

### 6.4 Rule-breaking consequences (Chapter 13) — system support, not automatic enforcement
The system cannot detect rule violations itself (no sensors on the shooting line), but it
should give the director/judge **fast tools to apply the consequence once they've made the
call**, specifically:
- **"Forfeit highest arrow" button** — applies Art. 13.3/13.6.2 (arrow shot out of
  sequence/time, or yellow-card non-compliance): marks the highest-value arrow of the
  current end as a miss before totalling.
- **Warning tracker** (Art. 13.4) — simple per-athlete/team warning counter the director
  can increment; purely informational, does not block anything, but shows up in the log.
- **Disqualification marker** (Art. 13.5) — stops the match logic for that
  athlete/team and records it in the log; does not attempt to auto-rank remaining
  competitors.

These are explicitly **judge/director-triggered**, matching Article 17.2/17.3 (judge's
on-the-spot decisions on arrow value or yellow cards are final and unappealable) — the
system is a recording/automation aid, not an adjudicator.

---

## 7. Display Requirements

- **RGB dot-matrix LED panel** (confirmed, decision OQ-4; exact panel model/pixel-pitch
  spec to be finalised once hardware is sourced).
- Must render:
  - Numeric countdown (large, primary element).
  - Light-colour state (Article 11.3.1) rendered as actual panel colour — red / green /
    yellow background or border treatment behind/around the countdown, matching the
    RED/GREEN/YELLOW semantics athletes are already trained to read on the field.
  - When flagged as a "scoring display": current score/set-points, arrow count for the
    current end, and end/set number.
- Must remain readable in direct outdoor sunlight (brightness/contrast requirement to be
  detailed once hardware is chosen).
- IP-rated enclosure (rating TBD once environment is finalised).
- Must degrade gracefully on ESP-NOW signal loss (e.g., show a clear "no signal" state
  rather than a frozen or blank display) — important for outdoor range distances.

---

## 8. Acoustic Requirements

- **Dedicated buzzer/speaker ESP32 nodes**, separate from displays, receiving ESP-NOW
  signal-trigger events (not raw audio — just event codes, e.g., `SIGNAL_OCCUPY_LINE`,
  `SIGNAL_START`, `SIGNAL_WARNING`, `SIGNAL_STOP`, `SIGNAL_SCORING`, `SIGNAL_EMERGENCY`,
  `SIGNAL_RESUME`), with the actual tone/pattern generated locally on each buzzer unit so
  audio timing isn't dependent on network audio streaming.
- **PA line-out**: a separate output path (from the controller or a dedicated buzzer unit)
  that plays a pre-recorded/synthesised audio file per signal type over a line-level
  output, so a PA operator can patch it into a venue sound system. This should use the same
  event codes as the buzzer nodes, just routed to an audio file playback + DAC/line-out
  instead of (or in addition to) a local buzzer.
- Signal patterns must match Article 11.3 counts exactly (2 signals / 1 signal / 2 signals
  / 3 signals / ≥5 signals) — these counts are load-bearing for officials on the field who
  are trained to recognise them, so pattern timing (gap between beeps, beep duration)
  should be configurable but ship with sensible WA-convention defaults.

---

## 9. Design Decisions Log

| # | Question | Decision |
|---|---|---|
| OQ-1 | Alternating-shooting handoff trigger | Reuse the **Start** button — first press begins the match, each subsequent press stops the current shooter's clock and starts the opponent's in one action (see §5.3, §5.5 for the resulting state-machine behaviour). Timeout still auto-advances if Start isn't pressed. |
| OQ-2 | Emergency Stop control | Dedicated physical button, in addition to a web UI control. Must trigger independently of Wi-Fi/UI state (see §3). |
| OQ-3 | Per-athlete ID in team modes | Not required. Team/mixed-team simultaneous shooting (§5.4) tracks only team-level arrow count and clock — no individual athlete identification on the shooting line. |
| OQ-4 | Display hardware type | **RGB dot-matrix panels.** Light-colour state (Art. 11.3.1: RED/GREEN/YELLOW) is rendered natively as panel colour, in addition to the numeric countdown — see updated §7. |
| OQ-5 | Practical unit cap | No fixed upper bound; system must comfortably support **at least 10 units** (displays + buzzers combined) in a session. This has a direct effect on the ESP-NOW transport design — see §7.1 (new) and §12. |

### 9.1 Implication of "at least 10 units" on the ESP-NOW transport

ESP-NOW's **encrypted unicast peer list is capped at 20 peers** on standard ESP32 (and as
few as 6 if AP+STA coexistence with Wi-Fi is active in some configurations), so relying on
individually-addressed encrypted peers for both directions (control-out and
status-heartbeat-in) risks hitting that ceiling once buzzers, displays, and headroom for
growth are counted together. Recommended approach:

- **Control channel (controller → units): use ESP-NOW broadcast**, not per-unit unicast.
  All paired displays/buzzers listen for the same broadcast frames and filter by a
  session/group ID in the payload. This scales to any number of receivers with no peer-list
  limit, and keeps the "near-simultaneous" latency goal intact since it's a single
  broadcast, not N sequential unicasts.
- **Status channel (unit → controller, e.g., "I'm alive," battery/connectivity): use
  low-rate unicast** (e.g., a heartbeat every 1–2s), which is where the ~20-peer ceiling
  actually matters — comfortably covers 10+ units with margin, and if you later scale well
  beyond that, the heartbeat can be moved to a round-robin/staggered schedule instead of
  every unit reporting every cycle.

---

## 10. Non-Functional Requirements

- **Latency:** Start/Stop/Pause signal delivery from controller to all paired displays and
  buzzers should be near-simultaneous (target: sub-100ms spread across units) — this is
  the "low latency is critical" requirement; ESP-NOW's broadcast/unicast performance
  should comfortably meet this at the small peer counts expected here.
- **Reliability:** Displays/buzzers must clearly indicate loss of connection rather than
  silently showing stale state.
- **Power:** TBD per unit type once hardware is chosen (flagged, not blocking spec).
- **Extensibility:** Companion-device and multi-match-independence features (both
  explicitly deferred) should not require breaking changes to the ESP-NOW protocol or web
  API — recommend versioning the message schema now even though only v1 features are
  built.

---

## 12. Technology Stack & Repository Recommendations

### 12.1 Firmware (Controller, Display, Buzzer units)

**Recommendation: C++ on ESP-IDF via PlatformIO**, not raw Arduino IDE.

- **Why C++/ESP-IDF over Arduino framework:** ESP-NOW + Wi-Fi AP concurrency, precise
  timer interrupts for the Emergency Stop button, and the low-jitter broadcast timing this
  project needs are all more directly controllable in ESP-IDF (Espressif's native
  framework) than through the Arduino abstraction layer. The Arduino framework *can* do
  ESP-NOW and Wi-Fi together, but ESP-IDF gives finer control over task priorities and
  interrupt handling — worth it here given "low latency is critical" is a hard
  requirement, not a nice-to-have.
- **Why PlatformIO as the build system:** works with ESP-IDF as a framework option, gives
  you proper dependency management, unit-testing support (`pio test`), and multi-target
  builds (Controller / Display / Buzzer are three different firmware images from one
  repo) — much easier to keep in CI than raw `idf.py` project-per-folder.
- **If you'd rather prioritise development speed over maximum control early on:** the
  Arduino framework (still via PlatformIO, so you can switch later without changing your
  toolchain) is a reasonable v1 shortcut, especially for the Display/Buzzer firmware which
  is simpler than the Controller's. The Controller (which does Wi-Fi AP + web server +
  ESP-NOW broadcast + interrupt-driven Emergency Stop simultaneously) is where ESP-IDF's
  extra control matters most.

### 12.2 Web UI (Controller-hosted)

- **HTML/CSS/vanilla JavaScript**, served from the ESP32's flash (LittleFS), communicating
  over WebSocket for live state (clock, connectivity) and plain HTTP/JSON for
  configuration actions. Avoid a heavy frontend framework (React/Vue/etc.) for the
  ESP32-hosted UI — flash space and RAM are limited, and this UI's job (buttons, a
  countdown readout, device list, score entry) doesn't need one.
- If you want a nicer development experience while keeping the shipped bundle small,
  **Preact + esbuild** (or plain Alpine.js for reactivity) compiles down to a few KB and is
  a good middle ground — optional, not required.
- **WebSocket library:** ESP-IDF's built-in `esp_http_server` component supports
  WebSocket natively, avoiding an extra dependency.

### 12.3 Companion device (future, optional)

- Not needed for v1, but since it's meant to be "just another web client" of the
  Controller's existing API, no separate backend language decision is needed now — any
  future companion app (phone/tablet/laptop) is just a browser hitting the same
  HTTP/WebSocket API the Controller already exposes. If a richer companion **backend**
  is ever needed (e.g., for stream-overlay rendering or persistent result storage beyond
  what the ESP32 can hold), Python (FastAPI) or Node.js are both reasonable choices at
  that point — defer the decision until that feature is actually scoped.

### 12.4 Scripting / tooling (repo-level, not on-device)

- **Python** for: test/simulation scripts (e.g., a script that emulates 10 ESP-NOW display
  nodes on a dev machine for load-testing the Controller's broadcast timing without
  needing 10 physical units), calibration tools, and any CI helper scripts.
- **PlatformIO's built-in unit testing** (`pio test`, using Unity under the hood) for
  on-device and native (host-machine) firmware tests.

### 12.5 GitHub Repository Structure

Recommend a **monorepo** (all firmware images + web UI + docs together), since they share
protocol definitions and version in lockstep:

```
archery-timer/
├── firmware/
│   ├── common/              # shared code: ESP-NOW message schema, signal codes,
│   │                        # timing-mode state machine logic (shared by controller
│   │                        # and, where relevant, display/buzzer for local rendering)
│   ├── controller/          # PlatformIO project: buttons, keypad, Wi-Fi AP,
│   │                        # web server, ESP-NOW broadcast master
│   ├── display/             # PlatformIO project: RGB dot-matrix rendering, ESP-NOW
│   │                        # receive-only client
│   └── buzzer/               # PlatformIO project: tone/pattern generation + optional
│                              # line-out audio playback, ESP-NOW receive-only client
├── webui/                   # HTML/CSS/JS source (built and copied into
│                              # firmware/controller's LittleFS image at build time)
├── docs/
│   ├── requirements.md      # this document
│   ├── protocol.md          # ESP-NOW message schema, signal codes, versioning
│   └── rulebook-mapping.md  # traceability: article number → requirement → code location
├── tools/                    # Python scripts: node emulator, load-test harness, etc.
├── tests/                    # native/unit tests (Unity via PlatformIO)
├── .github/
│   └── workflows/
│       └── ci.yml           # build all three PlatformIO targets + run native tests
├── platformio.ini           # multi-environment config (controller / display / buzzer)
└── README.md
```

- **Versioning:** tag releases (`v0.1.0`, etc.) and, per §11's note on extensibility,
  include a `protocol_version` field in every ESP-NOW message from day one so
  Controller/Display/Buzzer firmware mismatches fail safely (unit shows "firmware
  mismatch" rather than misbehaving) as the system evolves.
- **CI:** GitHub Actions running `pio run` for all three firmware environments plus native
  unit tests on every push — cheap to set up and catches build breakage before it reaches
  a field test.
- **Branching:** simple trunk-based development (`main` + short-lived feature branches) is
  sufficient at this project's scale — no need for a heavier Git-flow setup.

---

## 13. Suggested Build Phasing

1. Core timing engine + Controller buttons + single Display, individual non-alternating
   mode only (§5.2) — validates ESP-NOW latency and light/clock sync.
2. Add remaining timing modes (§5.3–5.9) and multi-display pairing.
3. Add buzzer units + PA line-out.
4. Add web UI (setup, monitoring, remote Start/Stop) — could be pulled earlier if you'd
   rather configure via UI than firmware from day one, per your note.
5. Add Match Logic module (end/score tracking, set-play/cumulative, Chapter 13 support
   tools).
6. Companion-device API groundwork (no actual streaming features yet).
