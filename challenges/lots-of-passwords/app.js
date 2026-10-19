const slug = 'lots-of-passwords';
ChallengeAPI.init(slug, challenge => {
  document.querySelector('#artifact').textContent = challenge.artifact;
  document.querySelector('#candidates').textContent = challenge.candidates.join('\n');
});
document.querySelector('#answer').addEventListener('submit', event => {
  event.preventDefault();
  ChallengeAPI.submit(slug, { password: document.querySelector('#password').value });
});