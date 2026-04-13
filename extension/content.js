(() => {
  const LS_KEY = 'kaset_volume';
  
  function getVolume() {
    const val = localStorage.getItem(LS_KEY);
    return val ? parseFloat(val) : 1.0;
  }

  function applyVolume() {
    const vol = getVolume();
    const video = document.querySelector('video');
    if (video && Math.abs(video.volume - vol) > 0.01) {
      video.volume = vol;
    }
  }

  new MutationObserver(applyVolume).observe(document.documentElement, { 
    childList: true, 
    subtree: true 
  });

  setInterval(applyVolume, 50);
  
  window.addEventListener('storage', applyVolume);
})();
