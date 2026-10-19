const slug = 'tftp-last-block';

function renderProgress(state) {
  const objectFound = Boolean(state.object_found);
  const keyFound = Boolean(state.key_found);
  const solved = Boolean(state.solved);

  document.querySelector('#object-status').textContent = objectFound
    ? 'Payload identified.'
    : 'Find the exported file that contains the protected payload.';
  document.querySelector('#key-status').textContent = keyFound
    ? 'Key recovered.'
    : objectFound ? 'Payload identified. Recover the key from the note.' : 'Locked until you identify the payload.';
  document.querySelector('#flag-status').textContent = solved
    ? 'Challenge complete.'
    : keyFound ? 'Key recovered. Decrypt the payload and submit its flag.' : 'Locked until you recover the key.';

  document.querySelector('#key-fields').disabled = !objectFound || keyFound || solved;
  document.querySelector('#flag-fields').disabled = !keyFound || solved;
  document.querySelector('#object-stage').classList.toggle('complete', objectFound);
  document.querySelector('#key-stage').classList.toggle('complete', keyFound);
  document.querySelector('#flag-stage').classList.toggle('complete', solved);
  document.querySelector('#key-stage').classList.toggle('locked', !objectFound);
  document.querySelector('#flag-stage').classList.toggle('locked', !keyFound);
}

ChallengeAPI.init(slug, renderProgress);

async function submitStep(event, stage, inputSelector) {
  event.preventDefault();
  const input = document.querySelector(inputSelector);
  const response = await ChallengeAPI.submit(slug, { stage, answer: input.value });
  if (response && response.challenge) renderProgress(response.challenge);
  if (response && response.result && response.result.correct) input.value = '';
}

document.querySelector('#object-form').addEventListener('submit', event => submitStep(event, 'object', '#object-answer'));
document.querySelector('#key-form').addEventListener('submit', event => submitStep(event, 'key', '#key-answer'));
document.querySelector('#flag-form').addEventListener('submit', event => submitStep(event, 'flag', '#flag-answer'));
