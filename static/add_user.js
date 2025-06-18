  const video = document.getElementById('video');
  const canvas = document.getElementById('canvas');
  const startCameraBtn = document.getElementById('start-camera');
  const captureBtn = document.getElementById('capture-photo');
  const sendBtn = document.getElementById('send-photo');
  const imageGrid = document.getElementById('captured-images');
  const hiddenInputs = document.getElementById('hidden-images-inputs');

let stream;

// Activer la caméra
startCameraBtn.addEventListener('click', async function () {
  console.log("Tentative d'activation de la caméra...");
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      document.querySelector('.webcam-container').style.display = 'block';
      captureBtn.style.display = 'inline-block';
      sendBtn.style.display = 'inline-block';
    } catch (err) {
      alert("Erreur lors de l'activation de la caméra : " + err.message);
    }
  });
// Arrêter la caméra
function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    video.srcObject = null;
    document.querySelector('.webcam-container').style.display = 'none';
    captureBtn.style.display = 'none';
    sendBtn.style.display = 'none';
  }
}
// Capturer l'image depuis la vidéo
captureBtn.addEventListener('click', function () {
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL('image/png');

    // 👉 Créer un aperçu dans la grille
    const img = document.createElement('img');
    img.src = dataURL;
    imageGrid.appendChild(img);

    // 💾 Ajouter un champ caché pour l'image
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'captured_images[]';
    input.value = dataURL;
    hiddenInputs.appendChild(input);
  });

// Envoyer l’image capturée
sendBtn.addEventListener('click', () => {
  const dataURL = canvas.toDataURL('image/png');
  const userId = null; // L'utilisateur n'existe pas encore ! => voir section suivante

  fetch("{% url 'save_captured_image' %}", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": "{{ csrf_token }}"
    },
    body: JSON.stringify({
      image: dataURL,
      user_id: userId  // ⚠️ ici ça ne marchera que si l'utilisateur est déjà enregistré
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      const img = document.createElement('img');
      img.src = dataURL;
      img.style.maxWidth = "100px";
      img.classList.add("m-2");
      capturedImagesContainer.appendChild(img);
      alert("✅ Image enregistrée !");
    } else {
      alert("❌ Erreur : " + data.error);
    }
  });
});
console.log("Script add_user.js chargé avec succès.");

