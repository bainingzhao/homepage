(() => {
  'use strict';
  const videos = [...document.querySelectorAll('video[data-viewport-play]')];
  if (!('IntersectionObserver' in window)) return; // Native controls remain usable.
  const visible = new Map(videos.map(video => [video, false]));
  const shouldPlay = video => visible.get(video) && !document.hidden;
  function sync(video) {
    if (!shouldPlay(video)) {
      video.pause();
      return;
    }
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
