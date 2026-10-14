# user/forms.py
import re
from django import forms
from django.contrib.auth import authenticate
from .models import User


class RegisterForm(forms.ModelForm):
    """Formulaire d'inscription."""

    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-navy-500 focus:ring-2 focus:ring-navy-200 outline-none transition",
            "placeholder": "••••••••",
            "autocomplete": "new-password",
        }),
    )
    password_confirm = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-navy-500 focus:ring-2 focus:ring-navy-200 outline-none transition",
            "placeholder": "••••••••",
            "autocomplete": "new-password",
        }),
    )

    class Meta:
        model = User
        fields = ["nom", "prenom", "numero_tel"]
        widgets = {
            "nom": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-navy-500 focus:ring-2 focus:ring-navy-200 outline-none transition",
                "placeholder": "Entrer votre nom",
            }),
            "prenom": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-navy-500 focus:ring-2 focus:ring-navy-200 outline-none transition",
                "placeholder": "Entrer votre prenom",
            }),
            "numero_tel": forms.TextInput(attrs={
                "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-navy-500 focus:ring-2 focus:ring-navy-200 outline-none transition",
                "placeholder": "90 00 00 00",
                "autocomplete": "tel",
            }),
        }

    def clean_numero_tel(self):
        numero = self.cleaned_data.get("numero_tel", "").strip()
        # Enlève les espaces et tirets
        numero_clean = re.sub(r"[\s\-\(\)]", "", numero)

        # Validation basique (adapte la regex à ton pays)
        if not re.match(r"^\+?\d{8,15}$", numero_clean):
            raise forms.ValidationError("Veuillez entrer un numéro de téléphone valide.")

        if User.objects.filter(numero_tel=numero_clean).exists():
            raise forms.ValidationError("Ce numéro est déjà utilisé.")

        return numero_clean

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get("password")
        pwd_confirm = cleaned.get("password_confirm")

        if pwd and pwd_confirm and pwd != pwd_confirm:
            self.add_error("password_confirm", "Les mots de passe ne correspondent pas.")

        if pwd and len(pwd) < 8:
            self.add_error("password", "Le mot de passe doit contenir au moins 8 caractères.")

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Formulaire de connexion."""

    numero_tel = forms.CharField(
        label="Numéro de téléphone",
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-navy-500 focus:ring-2 focus:ring-navy-200 outline-none transition",
            "placeholder": "90 00 00 00",
            "autocomplete": "tel",
        }),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-navy-500 focus:ring-2 focus:ring-navy-200 outline-none transition",
            "placeholder": "••••••••",
            "autocomplete": "current-password",
        }),
    )

    def clean_numero_tel(self):
        numero = self.cleaned_data.get("numero_tel", "").strip()
        return re.sub(r"[\s\-\(\)]", "", numero)

    def clean(self):
        cleaned = super().clean()
        numero = cleaned.get("numero_tel")
        password = cleaned.get("password")

        if numero and password:
            user = authenticate(numero_tel=numero, password=password)
            if user is None:
                raise forms.ValidationError("Numéro de téléphone ou mot de passe incorrect.")
            if not user.is_active:
                raise forms.ValidationError("Ce compte est désactivé.")
            cleaned["user"] = user

        return cleaned