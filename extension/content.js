let volume = 1.0;

chrome.storage.local.get(['volume'], (result) => {
  volume = (result.volume ?? 100) / 100;
  applyVolume();
});

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.volume !== undefined) {
    volume = msg.volume;
    applyVolume();
  }
});

chrome.storage.onChanged.addListener((changes) => {
  if (changes.volume) {
    volume = changes.volume.newValue / 100;
    applyVolume();
  }
});

function applyVolume() {
  const video = document.querySelector('video');
  if (video) video.volume = volume;
}

new MutationObserver(applyVolume).observe(document.documentElement, { 
  childList: true, 
  subtree: true 
});

setInterval(applyVolume, 50);
