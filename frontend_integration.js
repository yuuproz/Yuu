// Add this to your meshook_clone.html script
const BACKEND = "https://YOUR-BACKEND-URL.onrender.com"; // <-- replace after deploy

async function fetchInfo(tiktokUrl){
  const res = await fetch(`${BACKEND}/api/info?url=${encodeURIComponent(tiktokUrl)}`);
  if(!res.ok) throw new Error(await res.text());
  return await res.json();
}

function downloadMP4(tiktokUrl){
  window.location.href = `${BACKEND}/api/download?url=${encodeURIComponent(tiktokUrl)}&format=mp4`;
}
function downloadMP3(tiktokUrl){
  window.location.href = `${BACKEND}/api/download?url=${encodeURIComponent(tiktokUrl)}&format=mp3`;
}
