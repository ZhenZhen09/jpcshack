const slug = 'base64-cascade';
ChallengeAPI.init(slug, challenge => {
  document.querySelector('#artifact').textContent = challenge.artifact;
});
document.querySelector('#answer').addEventListener('submit', event => {
  event.preventDefault();
  ChallengeAPI.submit(slug, { answer: document.querySelector('#flag').value });
});