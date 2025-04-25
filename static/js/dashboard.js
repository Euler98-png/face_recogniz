// Gestion du modal
const modal = {
    show(modalId) {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            modalElement.classList.add('active');
        }
    },
    hide(modalId) {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            modalElement.classList.remove('active');
        }
    }
};

// Gestion des formulaires avec AJAX
document.addEventListener('DOMContentLoaded', function() {
    // Formulaire d'ajout d'utilisateur
    const addUserForm = document.getElementById('addUserForm');
    if (addUserForm) {
        addUserForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            try {
                const formData = new FormData(this);
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                });

                const data = await response.json();
                
                if (response.ok) {
                    showNotification('Utilisateur ajouté avec succès', 'success');
                    modal.hide('addUserModal');
                    window.location.reload();
                } else {
                    showNotification(data.message || 'Erreur lors de l\'ajout', 'error');
                }
            } catch (error) {
                showNotification('Erreur lors de la communication avec le serveur', 'error');
            }
        });
    }

    // Suppression d'utilisateur
    document.querySelectorAll('.delete-user-form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
                try {
                    const formData = new FormData(this);
                    const response = await fetch(this.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                        }
                    });

                    const data = await response.json();
                    
                    if (response.ok) {
                        showNotification('Utilisateur supprimé avec succès', 'success');
                        this.closest('tr').remove();
                    } else {
                        showNotification(data.message || 'Erreur lors de la suppression', 'error');
                    }
                } catch (error) {
                    showNotification('Erreur lors de la communication avec le serveur', 'error');
                }
            }
        });
    });
});
// Gestion de l'aperçu de l'image
document.addEventListener('DOMContentLoaded', function () {
    const input = document.querySelector('input[name="images"]');
    const preview = document.getElementById('preview');

    input.addEventListener('change', function () {
      preview.innerHTML = ''; // Efface les anciennes miniatures
      for (const file of input.files) {
        const reader = new FileReader();
        reader.onload = function (e) {
          const img = document.createElement('img');
          img.src = e.target.result;
          img.classList.add('img-thumbnail');
          img.style.height = '100px';
          img.style.objectFit = 'cover';
          preview.appendChild(img);
        };
        reader.readAsDataURL(file);
      }
    });
  });

// Système de notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    
    const container = document.querySelector('.dashboard-container');
    container.insertBefore(notification, container.firstChild);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}