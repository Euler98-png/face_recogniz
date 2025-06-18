from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from .forms import UserProfileForm, MultipleImageUploadForm, UserForm
from .models import User, UserProfile, UserImage
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import base64
import uuid
from django.conf import settings
import numpy as np
import cv2
import os
from .utils import extract_face, is_match, get_embedding
from numpy import dot
from numpy.linalg import norm


User = get_user_model()


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirection inversée : admin → reconnaissance / user → dashboard
            if user.is_superuser or user.is_staff:
                return redirect('/interface/')
            else:
                return redirect('/dashboard/')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")

    return render(request, 'login.html')



def is_admin(user):
    return user.is_superuser

@login_required
def dashboard(request):
    users = User.objects.all()
    profiles = UserProfile.objects.select_related('user').all()
    form = UserProfileForm()
    return render(request, 'dashboard.html', {'users': users, 'profiles': profiles, 'form': form})


@login_required
def add_user(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, admin=request.user)
        image_form = MultipleImageUploadForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid() and image_form.is_valid():
            try:
                # Création de l'utilisateur
                user = user_form.save(commit=False)
                password = user_form.cleaned_data['password']
                user.set_password(password)
                user.save()
                print("✅ Utilisateur créé :", user)

                # Création du profil utilisateur
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.admin = request.user
                profile.save()
                print("✅ Profil enregistré :", profile)

                # Traitement des images uploadées
                for image in request.FILES.getlist('images'):
                    img_instance = UserImage.objects.create(user=user, image=image, source='upload')
                    save_embedding_from_image_instance(img_instance)

                # Traitement des images capturées
                captured_images = request.POST.getlist('captured_images[]')
                for captured_image in captured_images:
                    try:
                        format, imgstr = captured_image.split(';base64,')
                        ext = format.split('/')[-1]
                        file_name = f"capture_{uuid.uuid4().hex}.{ext}"
                        image_file = ContentFile(base64.b64decode(imgstr), name=file_name)
                        img_instance = UserImage.objects.create(user=user, image=image_file, source='capture')
                        save_embedding_from_image_instance(img_instance)
                    except Exception as e:
                        print("❌ Erreur lors de l'enregistrement d'une image capturée :", e)

                messages.success(request, "Utilisateur ajouté avec succès.")
                return redirect('dashboard')

            except Exception as e:
                print("🔥 Erreur lors de la création :", e)
                messages.error(request, "Erreur lors de la création : " + str(e))

        else:
            print("🛑 Formulaire invalide")
            print("UserForm errors:", user_form.errors)
            print("ProfileForm errors:", profile_form.errors)
            print("ImageForm errors:", image_form.errors)

        return render(request, 'add_user.html', {
            'user_form': user_form,
            'form': profile_form,
            'image_form': image_form
        })

    else:
        user_form = UserForm()
        profile_form = UserProfileForm(admin=request.user)
        image_form = MultipleImageUploadForm()

    return render(request, 'add_user.html', {
        'user_form': user_form,
        'form': profile_form,
        'image_form': image_form
    })

def save_embedding_from_image_instance(img_instance):
    try:
        image_path = img_instance.image.path
        img = cv2.imread(image_path)
        if img is None:
            print(f" Impossible de charger l'image : {image_path}")
            return
        print(f"image chargée : {image_path} , dimensions = {img.shape}")


        face, _ = extract_face(img)

        if face is not None:
            print("Face shape:", face.shape, "dtype:", face.dtype)
            cv2.imwrite('/tmp/face_debug.jpg', face)

            face = cv2.resize(face, (160, 160))
            embedding = get_embedding(face)

            if embedding is not None:
                # Construction du chemin d'enregistrement
                embedding_filename = os.path.splitext(os.path.basename(image_path))[0] + '_embedding.npy'
                # Définir le chemin relatif pour stocker l'embedding dans un dossier par utilisateur
                embedding_rel_path = os.path.join('embeddings', str(img_instance.user.id), embedding_filename)
                embedding_full_path = os.path.join(settings.MEDIA_ROOT, embedding_rel_path)  # chemin absolu

                # Création du dossier si nécessaire
                os.makedirs(os.path.dirname(embedding_full_path), exist_ok=True)

                # ✅ Sauvegarde effective du fichier .npy
                np.save(embedding_full_path, embedding)

                # ✅ Enregistrement dans le champ FileField
                img_instance.embedding.name = embedding_rel_path
                img_instance.save()

                print("✅ Embedding enregistré :", img_instance.embedding.name)

            else:
                print("⚠️ Embedding non généré")
        else:
            print("⚠️ Aucun visage détecté pour :", image_path)

    except Exception as e:
        print("❌ Erreur dans save_embedding_from_image_instance:", e)


@csrf_exempt
def recognize_uploaded_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        try:
            # 1. Sauvegarder l'image temporairement
            uploaded_file = request.FILES["image"]
            file_name = default_storage.save("temp_uploaded/" + uploaded_file.name, ContentFile(uploaded_file.read()))
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)

            # 2. Lire l'image
            img = cv2.imread(file_path)
            if img is None:
                print("❌ Image non lisible :", file_path)
                return JsonResponse({"status": "error", "message": "Image non lisible"})

            # 3. Extraire le visage
            face, box = extract_face(img)
            if face is None:
                print("❌ Aucun visage détecté :", file_path)
                return JsonResponse({"status": "error", "message": "Aucun visage détecté"})

            # 4. Calculer l'embedding
            face = cv2.resize(face, (160, 160))
            uploaded_embedding = get_embedding(face)
            if uploaded_embedding is None:
                print("❌ Échec de génération d'embedding")
                return JsonResponse({"status": "error", "message": "Échec de génération d'embedding"})

            # 5. Comparaison avec les embeddings en base
            min_dist = float("inf")
            matched_user = None

            embeddings_count = 0
            for user_img in UserImage.objects.exclude(embedding=""):
                try:
                    emb_path = os.path.join(settings.MEDIA_ROOT, user_img.embedding.name)
                    if not os.path.exists(emb_path):
                        print(f"⚠️ Embedding manquant : {emb_path}")
                        continue
                    db_embedding = np.load(emb_path)
                    # Vérification de la forme de l'embedding
                    if db_embedding is None or db_embedding.shape != uploaded_embedding.shape:
                        print(f"⚠️ Embedding corrompu ou shape différente : {emb_path}")
                        continue

                    dist = cosine_distance(uploaded_embedding, db_embedding)
                    embeddings_count += 1
                    if dist < min_dist:
                        min_dist = dist
                        matched_user = user_img.user
                except Exception as e:
                    print("❌ Erreur lecture embedding:", e)
                    continue

            print(f"Comparaison effectuée avec {embeddings_count} embeddings. min_dist={min_dist}")

            # 6. Seuil de reconnaissance
            threshold = 0.6
            if matched_user and min_dist < threshold:
                profile = getattr(matched_user, 'profile', None)
                if profile:
                    return JsonResponse({
                        "status": "ok",
                        "user": {
                            "username": matched_user.username,
                            "first_name": profile.first_name,
                            "last_name": profile.last_name,
                            "email": profile.email,
                            "matricule": profile.matricule,
                        }
                    })
                else:
                    print("⚠️ Profil utilisateur non trouvé")
                    return JsonResponse({"status": "error", "message": "Profil utilisateur non trouvé"})
            else:
                return JsonResponse({"status": "unknown", "message": "Visage non reconnu"})

        except Exception as e:
            print("❌ Exception globale recognize_uploaded_image:", e)
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Méthode non autorisée ou image manquante"})


def cosine_distance(a, b):
    return 1 - dot(a, b) / (norm(a) * norm(b))


def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)
    images = user.images.all()

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        image_form = MultipleImageUploadForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid() and image_form.is_valid():
            user_form.save()
            profile_form.save()

            # ✅ Images uploadées
            for image in request.FILES.getlist('images'):
                img_instance = UserImage.objects.create(user=user, image=image, source='upload')
                save_embedding_from_image_instance(img_instance)

            # ✅ Images capturées via webcam (base64)
            captured_images = request.POST.getlist('captured_images[]')
            for captured_image in captured_images:
                try:
                    format, imgstr = captured_image.split(';base64,')
                    ext = format.split('/')[-1]
                    file_name = f"capture_{uuid.uuid4().hex}.{ext}"
                    image_file = ContentFile(base64.b64decode(imgstr), name=file_name)
                    img_instance = UserImage.objects.create(user=user, image=image_file, source='capture')
                    save_embedding_from_image_instance(img_instance)
                except Exception as e:
                    print("❌ Erreur image capturée (edit):", e)

            messages.success(request, "Utilisateur mis à jour avec succès.")
            return redirect('dashboard')

    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
        image_form = MultipleImageUploadForm()

    return render(request, 'edit_user.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'image_form': image_form,
        'images': images,
    })



@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Supprimer le profil s'il existe
    if hasattr(user, 'profile'):
        user.profile.delete()

    # Supprimer les images associées (si besoin)
    user.images.all().delete()

    # Supprimer l'utilisateur
    user.delete()

    messages.success(request, "Utilisateur supprimé avec succès.")
    return redirect('dashboard')


@login_required
def view_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)
    images = user.images.all()  # Images liées à cet utilisateur

    return render(request, 'view_user.html', {
        'profile': profile,
        'images': images,
        'user': user
    })


def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('recognition_interface')  # ou autre nom de route
        else:
            return render(request, 'login.html', {'error': "Accès refusé."})
    return render(request, 'login.html')

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def recognition_interface(request):
    return render(request, 'recognition_interface.html')



@csrf_exempt
def recognize_face(request):
    if request.method == 'POST':
        data = request.POST.get('image')
        if not data:
            print("Aucune image reçue")
            return JsonResponse({'status': 'error', 'message': 'No image'})

        try:
            format, img_base64 = data.split(';base64,')
            img_data = base64.b64decode(img_base64)
            print("Taille img_data",len(img_data))
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            print("Image shape:", img.shape if img is not None else "None")
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Erreur décodage image'})

        face, box = extract_face(img)
        print("Face détectée :", face is not None)
        label = "Inconnu"
        user_data = {
            'name': 'Inconnu',
            'email': 'Inconnu',
            'id': 'Inconnu',
            
        }

        if face is not None:
            face = cv2.resize(face, (160, 160))
            embedding = get_embedding(face)

            if embedding is not None:
                min_dist = float("inf")
                matched_user = None
                for user_img in UserImage.objects.exclude(embedding=""):
                    try:
                        emb_path = user_img.embedding.path
                        db_embedding = np.load(emb_path)
                        if db_embedding is None or db_embedding.shape != embedding.shape:
                            continue
                        dist = cosine_distance(embedding, db_embedding)
                        if dist < min_dist:
                            min_dist = dist
                            matched_user = user_img.user
                    except Exception as e:
                        print("❌ Erreur lors du chargement d’un embedding:", e)
                        continue

                threshold = 0.6
                if matched_user and min_dist < threshold:
                    label = f"{matched_user.first_name} {matched_user.last_name}"
                    user_data = {
                        'name': label,
                        'username': matched_user.username,
                        'first_name': matched_user.first_name,
                        'last_name': matched_user.last_name,
                        'email': matched_user.email,
                        'id': str(matched_user.id),
                    }

            if box is not None:
                (x, y, w, h) = box
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

        _, jpeg = cv2.imencode('.jpg', img)
        response = HttpResponse(jpeg.tobytes(), content_type='image/jpeg')
        response['X-User-Name'] = user_data['name']
        response['X-User-Email'] = user_data['email']
        response['X-User-Id'] = user_data['id']
        return response

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'})