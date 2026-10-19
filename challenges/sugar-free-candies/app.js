const slug = 'sugar-free-candies';
ChallengeAPI.init(slug, challenge => {
  document.querySelector('#artifact').textContent = challenge.equations.join('\n');
});
document.querySelector('#answer').addEventListener('submit', event => {
  event.preventDefault();
  ChallengeAPI.submit(slug, { x: document.querySelector('#x').value, y: document.querySelector('#y').value, z: document.querySelector('#z').value });
});