(() => {
  'use strict';
  const badge = document.querySelector('.citation-badge');
  if (!badge) return;
  const script = document.currentScript;
  const url = new URL('gs_data.json', script.src);
  fetch(url, {cache: 'no-cache'})
    .then(response => { if (!response.ok) throw new Error('Unavailable'); return response.json(); })
    .then(data => {
      if (data.scholar_id !== 'aEts7nUAAAAJ' || !Number.isSafeInteger(data.citedby) || data.citedby < 0 || !Number.isFinite(Date.parse(data.updated))) return;
      badge.querySelector('b').textContent = data.citedby.toLocaleString('en-US');
      badge.title = `Google Scholar total citations · Updated ${data.updated.slice(0, 10)}`;
      badge.setAttribute('aria-label', `${data.citedby} Google Scholar citations, updated ${data.updated.slice(0, 10)}`);
    })
    .catch(() => { /* Preserve the server-rendered fallback and last verified value. */ });
})();
