"""
URL configuration for Bus project.

Routes principales :
- /admin/              : admin Django
- /manifest.json       : PWA manifest (racine)
- /sw.js               : Service Worker (racine)
- /favicon.ico         : favicon (racine)
- /user/               : auth + dashboard
- /payements/          : paiements (à venir)
- /                    : bus_tracking (pages publiques protégées)
"""
from django.contrib import admin
from django.urls import path, include
from django.http import FileResponse
from django.views.decorators.cache import never_cache
from django.conf import settings
import os

# ============================================
# PWA — Servir manifest.json et sw.js à la RACINE
# (obligatoire pour que le SW contrôle tout le site)
# ============================================

@never_cache
def manifest_view(request):
    """Sert /manifest.json depuis static/manifest.json"""
    path_file = os.path.join(settings.BASE_DIR, 'static', 'manifest.json')
    response = FileResponse(
        open(path_file, 'rb'),
        content_type='application/manifest+json'
    )
    response['Cache-Control'] = 'no-cache'
    return response


@never_cache
def service_worker_view(request):
    """Sert /sw.js depuis static/sw.js avec scope '/'"""
    path_file = os.path.join(settings.BASE_DIR, 'static', 'sw.js')
    response = FileResponse(
        open(path_file, 'rb'),
        content_type='application/javascript'
    )
    # CRUCIAL : autorise le SW à contrôler toute l'app depuis la racine
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


@never_cache
def favicon_view(request):
    """Sert /favicon.ico depuis static/icons/favicon.ico"""
    path_file = os.path.join(settings.BASE_DIR, 'static', 'icons', 'favicon.ico')
    if os.path.exists(path_file):
        return FileResponse(open(path_file, 'rb'), content_type='image/x-icon')
    # Fallback : 204 No Content si pas de favicon
    from django.http import HttpResponse
    return HttpResponse(status=204)


# ============================================
# URL PATTERNS
# ============================================
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # PWA — routes racine (AVANT tout le reste)
    path('manifest.json', manifest_view, name='manifest'),
    path('sw.js', service_worker_view, name='service_worker'),
    path('favicon.ico', favicon_view, name='favicon'),

    # Applications
    path('user/', include("user.urls")),
    path('payements/', include("payements.urls")),
    path('', include("bus_tracking.urls")),
]