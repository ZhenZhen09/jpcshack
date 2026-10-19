const slug = 'sekur-julius';
ChallengeAPI.init(slug, challenge => {
  document.querySelector('#artifact').textContent = challenge.artifact;
  document.querySelector('#note').textContent = challenge.note;
});
document.querySelector('#answer').addEventListener('submit', event => {
  event.preventDefault();
  ChallengeAPI.submit(slug, { answer: document.querySelector('#flag').value });
});