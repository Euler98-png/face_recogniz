from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, UserImage
from django.forms import DateInput, modelformset_factory
from django.contrib.auth import get_user_model
import datetime


User = get_user_model()


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']




class UserProfileForm(forms.ModelForm):
    hire_date = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),
        label="Date d'embauche"
    )

    class Meta:
        model = UserProfile
        fields = ['phone', 'function', 'hire_date', 'salary', 'gender', 'matricule']

    def __init__(self, *args, **kwargs):
        self.admin = kwargs.pop('admin', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)

        if not self.fields['hire_date'].initial:
            self.fields['hire_date'].initial = datetime.date.today()
        if self.admin:
            self.fields['hire_date'].widget.attrs['placeholder'] = 'Choisir une date'

# Widget pour permettre le chargement multiple d’images
class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultiFileField(forms.FileField):
    widget = MultiFileInput

    def clean(self, data, initial=None):
        if not data and initial:
            return initial
        return [super(MultiFileField, self).clean(d, initial) for d in data]

# Formulaire d’upload multiple d’images
class MultipleImageUploadForm(forms.Form):
    images = MultiFileField(
        required=False,
        label="Choisissez plusieurs images",
        help_text="Vous pouvez sélectionner plusieurs fichiers en même temps."
    )
