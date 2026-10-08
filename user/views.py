# user/views.py
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from .forms import LoginForm, RegisterForm


class LoginView(TemplateView):
    """Vue de connexion."""
    template_name = "user/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = LoginForm()
        return context

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user)
            messages.success(request, f"Bienvenue {user.prenom} !")
            next_url = request.GET.get("next") or reverse("user:dashboard")
            return redirect(next_url)

        return render(request, self.template_name, {"form": form})


class RegisterView(TemplateView):
    """Vue d'inscription."""
    template_name = "user/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = RegisterForm()
        return context

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Votre compte a été créé avec succès !")
            return redirect("user:dashboard")

        return render(request, self.template_name, {"form": form})


@login_required
def dashboard_view(request):
    """Page temporaire après connexion."""
    return render(request, "user/dashboard.html")


def logout_view(request):
    """Déconnexion."""
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect("user:login")