from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .forms import UserProfileForm, MultipleImageUploadForm, UserForm
from .models import UserImage, UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

def is_admin(user):
    return user.is_superuser

@login_required
def dashboard(request):
    users = User.objects.all()
    profiles = UserProfile.objects.select_related('user').all()
    form = UserProfileForm()
    return render(request, 'dashboard.html', {'users': users, 'profiles': profiles, 'form': form})

@user_passes_test(is_admin)
@login_required
def add_user(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, admin=request.user)
        image_form = MultipleImageUploadForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid() and image_form.is_valid():
            try:
                user = user_form.save(commit=False)
                password = user_form.cleaned_data['password']
                user.set_password(password)
                user.save()
                print("✅ Utilisateur créé :", user)

                profile = profile_form.save(commit=False)
                profile.user = user
                profile.admin = request.user
                profile.save()
                print("✅ Profil enregistré :", profile)

                for image in request.FILES.getlist('images'):
                    img = UserImage.objects.create(user=user, image=image)
                    print("✅ Image enregistrée :", img)

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
