# Display firmware

This folder is the display target for the field units. Display nodes are intended to be
receive-only listeners on the controller's broadcast state updates.

## Design

- Receive `STATE_UPDATE` packets from the controller
- Render the countdown and light state
- Show score information only when flagged as a scoring display
- Degrade gracefully into a no-signal mode when heartbeats stop

## Current scaffold

The shared display state model lives in `firmware/common/display_state.py`. This target is a
placeholder for the actual ESP32 dot-matrix rendering firmware that will be implemented in the
next phase.
