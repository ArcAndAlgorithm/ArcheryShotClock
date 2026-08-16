# Controller firmware

This folder is the first firmware target for the master controller. The design follows the
requirements document: a single controller owns the match session, drives the web UI, and
broadcasts state to the paired displays and buzzers over the shared transport layer.

## Purpose

- Own the timing state machine
- Accept local/web controls
- Broadcast state updates
- Maintain pairing / connectivity state
- Expose a state API and monitoring UI

## Current scaffold

The controller runtime is modeled by the shared python runtime layer in
`firmware/common/controller_runtime.py`, and the transport flow is modeled in
`firmware/common/broadcast.py` and `firmware/common/firmware_runtime.py`.

This folder is intentionally left as a PlatformIO/ESP-IDF-ready target scaffold for the next
firmware implementation step.
