const slider = document.getElementById('slider');
const valDisplay = document.getElementById('val');

chrome.storage.local.get(['volume'], (result) => {
  const vol = result.volume ?? 100;
  slider.value = vol;
  valDisplay.textContent = vol;
});

slider.addEventListener('input', () => {
  const vol = parseInt(slider.value);
  valDisplay.textContent = vol;
  chrome.storage.local.set({ volume: vol });
  chrome.tabs.query({ url: '*://music.youtube.com/*' }, (tabs) => {
    tabs.forEach(tab => chrome.tabs.sendMessage(tab.id, { volume: vol / 100 }));
  });
});
