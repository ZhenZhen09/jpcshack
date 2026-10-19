const slug = 'ghost-binary';
let artifact = '';
ChallengeAPI.init(slug, challenge => {
  artifact = challenge.artifact;
  document.querySelector('#artifact').textContent = artifact;
});
document.querySelector('#download').addEventListener('click', () => {
  if (!artifact) return;
  const bytes = Uint8Array.from(artifact.match(/../g), byte => parseInt(byte, 16));
  const blob = new Blob([bytes], { type: 'application/octet-stream' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'ghost.bin';
  anchor.click();
  URL.revokeObjectURL(url);
});
document.querySelector('#answer').addEventListener('submit', event => {
  event.preventDefault();
  ChallengeAPI.submit(slug, { key: document.querySelector('#key').value });
});