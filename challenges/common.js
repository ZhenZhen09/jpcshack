(() => {
  const result = document.querySelector('#result');
  function show(message, good) {
    if (!result) return;
    result.className = 'result ' + (good ? 'good' : 'bad');
    result.textContent = message;
  }
  async function request(url, options) {
    const response = await fetch(url, Object.assign({ credentials: 'same-origin', cache: 'no-store' }, options || {}));
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The challenge service could not complete that request.');
    return data;
  }
  window.ChallengeAPI = {
    async init(slug, render) {
      try {
        const data = await request('/api/challenges/' + slug + '/session');
        render(data.challenge);
        if (data.solved) show('Already solved. Flag: ' + data.flag, true);
      } catch (error) { show(error.message, false); }
    },
    async submit(slug, values) {
      try {
        const data = await request('/api/challenges/' + slug + '/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(values),
        });
        const message = (data.result && data.result.message) || (data.solved ? 'Solved. Flag: ' + data.flag : 'Submission received.');
        show(data.solved && data.flag && !message.includes(data.flag) ? message + ' Flag: ' + data.flag : message, !!((data.result && data.result.correct) || data.solved));
        return data;
      } catch (error) { show(error.message, false); }
    },
  };
})();
