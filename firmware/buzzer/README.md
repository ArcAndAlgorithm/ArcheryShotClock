# Buzzer firmware

This folder is the buzzer target for the audio event units. Buzzer nodes are intended to
receive `SIGNAL_EVENT` packets and generate the Article 11.3 signal patterns locally.

## Design

- Receive `SIGNAL_EVENT` packets from the controller
- Map those events to local audio patterns
- Support configurable tone lengths and gaps
- Keep audio generation local rather than streaming raw audio over the network

## Current scaffold

The shared buzzer state model lives in `firmware/common/buzzer_state.py`. This target is a
placeholder for the actual speaker or DAC driver implementation that will be added in the next
phase.
