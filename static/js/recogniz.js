
const video1 = document.getElementById('video-recognition');
const outputFrame = document.getElementById('output-frame');
const startCameraBtn = document.getElementById('start-camera')
const captureBtn = document.getElementById('capture-btn-recognition');
const previewImage = document.getElementById("preview-uploaded-image");
const imageInput = document.getElementById("image-upload");
let stream= null;
let recognitionInterval = null

startCameraBtn.addEventListener('click', async function () {
   console.log("Tentative d'activation de la caméra...");
  try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video1.srcObject = stream;
    if (fileUploadSection) fileUploadSection.style.display = 'none';
    if (recognitionInterval) clearInterval(recognitionInterval);
    recognitionInterval = setInterval(autoRecognize, 1000);
    } catch (err) {
      alert("Erreur lors de l'activation de la caméra : " + err.message);
    }
  });
const fileUploadSection = document.getElementById('file-upload-section');



if (imageInput) {
    imageInput.addEventListener("change", function (e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (evt) {
                previewImage.src = evt.target.result;
                previewImage.style.display = "block";
            };
            reader.readAsDataURL(file);
        }
    });
}


async function autoRecognize() {
    if (!stream || !video1) return;
    const canvas = document.createElement('canvas');
    canvas.width = video1.videoWidth;
    canvas.height = video1.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video1, 0, 0);
    const dataURL = canvas.toDataURL('image/jpeg');

    // Envoie la frame au serveur
    fetch('/recognize-face/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `image=${encodeURIComponent(dataURL)}`
    })
    .then(async response => {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            const json = await response.json();
            // Optionnel : afficher une alerte ou rien si visage non reconnu
        } else {
            const blob = await response.blob();
            const userName = response.headers.get('X-User-Name') || 'Inconnu';
            const userEmail = response.headers.get('X-User-Email') || 'Inconnu';
            const userId = response.headers.get('X-User-Id') || 'Inconnu';

            outputFrame.src = URL.createObjectURL(blob);
            document.getElementById('user-name').value = userName;
            document.getElementById('user-email').value = userEmail;
            document.getElementById('user-id').value = userId;
        }
    })
    .catch(err => {
        console.error("Erreur lors de la reconnaissance :", err);
    });
}
