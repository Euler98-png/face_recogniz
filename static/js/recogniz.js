const video1 = document.getElementById('video-recognition');
const outputFrame = document.getElementById('output-frame');
const startCameraBtn = document.getElementById('start-camera')
const captureBtn = document.getElementById('capture-btn-recognition');

startCameraBtn.addEventListener('click', async function () {
  console.log("Tentative d'activation de la caméra...");
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      captureBtn.style.display = 'inline-block';
      sendBtn.style.display = 'inline-block';
    } catch (err) {
      alert("Erreur lors de l'activation de la caméra : " + err.message);
    }
  });


function captureAndSend() {

    if(!startCameraBtn || !video1) {
        console.warn("Caméra non active ou image non prête.");
        return;
    }
    const canvas = document.createElement('canvas');
    canvas.width = video1.videoWidth;
    canvas.height = video1.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video1, 0, 0);

    const dataURL = canvas.toDataURL('image/jpeg');

    fetch('/recognize-face/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `image=${encodeURIComponent(dataURL)}`
    })
    .then(async response => {
        // Séparer JSON des headers et image
        const contentType = response.headers.get("content-type");
        if (contentType.includes("application/json")) {
            const json = await response.json();
            alert("Erreur : " + json.message);
        } else {
            const blob = await response.blob();
            const userName = response.headers.get('X-User-Name') || 'Inconnu';
            const userEmail = response.headers.get('X-User-Email') || 'Inconnu';
            const userId = response.headers.get('X-User-Id') || 'Inconnu';
            const userStatus = response.headers.get('X-User-Status') || 'Inconnu';

            outputFrame.src = URL.createObjectURL(blob);
            document.getElementById('user-name').value = userName;
            document.getElementById('user-email').value = userEmail;
            document.getElementById('user-id').value = userId;
            document.getElementById('user-status').value = userStatus;
        }
    })
    .catch(err => {
        console.error("Erreur lors de la reconnaissance :", err);
    });
}

