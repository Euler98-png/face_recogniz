from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
import os
from django.utils import timezone
# Utilisation du modèle utilisateur personnalisé AdminUser
class AdminUser(AbstractUser):
    # Tu peux ajouter d'autres champs ici si nécessaire pour AdminUser
    pass

# Utilisation de get_user_model() pour récupérer le modèle personnalisé d'utilisateur
User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_profiles')  # Référence à l'administrateur
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    function = models.CharField(max_length=20, choices=[('Manager', 'Manager'), ('Developer', 'Developer'), ('Designer', 'Designer'), ('Tester', 'Tester'), ('Other', 'Other')])
    hire_date = models.DateField(default=timezone.now)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    matricule = models.CharField(max_length=20)
   

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

def user_image_path(instance, filename):
    return f'user_images/{instance.user.username}/{filename}'


def embedding_path(instance, filename):
    return f'user_embeddings/{instance.user.username}/{filename}'


class UserImage(models.Model):
    SOURCE_CHOICES = [
        ('upload', 'Upload'),
        ('capture', 'Capture'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=user_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='upload')  # ✅ nouveau champ

    embedding = models.FileField(upload_to=embedding_path, null=True, blank=True)


    def __str__(self):
        return f"Image for {self.user.username} - {self.image.name}"

    def delete(self, *args, **kwargs):
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)

