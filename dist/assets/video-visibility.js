(() => {
  'use strict';
  const videos = [...document.querySelectorAll('video[data-viewport-play]')];
  function load(video) {
    const source = video.querySelector('source[data-src]');
    if (!source) return;
    source.src = source.dataset.src;
    source.removeAttribute('data-src');
    video.load();
  }
  videos.forEach(video => {
    video.muted = true;
    video.playsInline = true;
    // Allow direct interaction even before the observer callback has arrived.
    video.addEventListener('pointerdown', () => load(video), {once: true});
    video.addEventListener('keydown', () => load(video), {once: true});
  });
  if (!('IntersectionObserver' in window)) {
    videos.forEach(load); // No automatic playback; native controls still work.
    return;
  }
  const visible = new Map(videos.map(video => [video, false]));
  const shouldPlay = video => visible.get(video) && !document.hidden;
  function sync(video) {
    if (!shouldPlay(video)) {
      video.pause();
      return;
    }
    load(video);
    if (!video.paused) return;
    const pending = video.play();
    if (pending) pending.then(() => {
      // Scrolling or switching tabs can happen while playback is starting.
      if (!shouldPlay(video)) video.pause();
    }).catch(() => { /* Browser may require a tap; keep native controls available. */ });
  }
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      visible.set(entry.target, entry.isIntersecting && entry.intersectionRatio >= 0.25);
      sync(entry.target);
    });
  }, {threshold: [0, 0.25]});
  videos.forEach(video => observer.observe(video));
  document.addEventListener('visibilitychange', () => videos.forEach(sync));
  window.addEventListener('pagehide', () => videos.forEach(video => video.pause()));
  window.addEventListener('pageshow', () => videos.forEach(sync));
})();
