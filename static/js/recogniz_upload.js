console.log("Script de reconnaissance d'image chargé");
document.getElementById('image-upload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Aperçu local
    const reader = new FileReader();
    reader.onload = function(event) {
        const preview = document.getElementById('preview-uploaded-image');
        preview.src = event.target.result;
        preview.style.display = 'block';

        // Envoyer à Django pour détection/reconnaissance
        sendUploadedImage(event.target.result);
    };
    reader.readAsDataURL(file);
});

function sendUploadedImage(base64Image) {
    fetch('/recognize-face/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `image=${encodeURIComponent(base64Image)}`
    })
    .then(async response => {
        const contentType = response.headers.get("content-type");

        if (contentType.includes("application/json")) {
            const json = await response.json();
            alert("Erreur : " + json.message);
        } else {
            const blob = await response.blob();

            // Met à jour l’aperçu avec le cadrage serveur
            const preview = document.getElementById('preview-uploaded-image');
            preview.src = URL.createObjectURL(blob);

            // Infos utilisateur
            const userName = response.headers.get('X-User-Name') || 'Inconnu';
            const userEmail = response.headers.get('X-User-Email') || 'Inconnu';
            const userId = response.headers.get('X-User-Id') || 'Inconnu';
            const userStatus = response.headers.get('X-User-Status') || 'Inconnu';

            document.getElementById('user-name').value = userName;
            document.getElementById('user-email').value = userEmail;
            document.getElementById('user-id').value = userId;
            document.getElementById('user-status').value = userStatus;
        }
    })
    .catch(err => {
        console.error("Erreur de reconnaissance via image :", err);
    });
}