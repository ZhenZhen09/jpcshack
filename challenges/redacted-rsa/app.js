const slug = 'redacted-rsa';
ChallengeAPI.init(slug, challenge => {
  document.querySelector('#artifact').textContent = 'n = ' + challenge.n + '\ne = ' + challenge.e + '\nciphertext blocks:\n' + challenge.blocks.join(' ');
});
document.querySelector('#answer').addEventListener('submit', event => {
  event.preventDefault();
  ChallengeAPI.submit(slug, { p: document.querySelector('#p').value, q: document.querySelector('#q').value });
});