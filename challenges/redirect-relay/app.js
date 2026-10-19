const slug = "redirect-relay";
ChallengeAPI.init(slug, challenge => {
  document.querySelector('#artifact').textContent = challenge.artifact;
  document.querySelector('#hint').textContent = challenge.hint;
});
document.querySelector('#answer').addEventListener('submit', event => {
  event.preventDefault();
  ChallengeAPI.submit(slug, { answer: document.querySelector('#flag').value });
});
