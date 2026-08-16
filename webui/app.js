async function fetchState() {
  const response = await fetch('/api/state');
  if (!response.ok) {
    throw new Error('State request failed');
  }
  return response.json();
}

async function triggerAction(action) {
  const response = await fetch(`/api/${action}`, { method: 'POST' });
  if (!response.ok) {
    throw new Error(`${action} request failed`);
  }
  return response.json();
}

function formatTimer(milliseconds) {
  return `${(milliseconds / 1000).toFixed(1)}s`;
}

function renderState(state) {
  const statusEl = document.getElementById('status');
  const timerEl = document.getElementById('timer');
  const lightEl = document.getElementById('light');
  const phaseEl = document.getElementById('phase');
  const activeList = document.getElementById('active-list');

  statusEl.textContent = state.active ? 'RUNNING' : 'READY';
  timerEl.textContent = formatTimer(state.time_remaining_ms || 0);
  lightEl.textContent = `Light state: ${state.light_state}`;
  phaseEl.textContent = `Phase: ${state.phase}`;

  if (state.active) {
    activeList.textContent = 'Session active';
  } else {
    activeList.textContent = 'Awaiting start';
  }
}

async function refresh() {
  try {
    const state = await fetchState();
    renderState(state);
  } catch (error) {
    console.error(error);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-action]').forEach((button) => {
    button.addEventListener('click', async () => {
      const action = button.dataset.action;
      try {
        await triggerAction(action);
        await refresh();
      } catch (error) {
        console.error(error);
      }
    });
  });

  refresh();
  setInterval(refresh, 500);
});
