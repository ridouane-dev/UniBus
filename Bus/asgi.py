"""
ASGI config for Bus project.

Point d'entrée pour :
- HTTP (Django normal)
- WebSockets (Django Channels, à venir)

Ce fichier est utilisé par Daphne/Uvicorn en production.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# ============================================
# Initialiser Django AVANT tout import Channels
# ============================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bus.settings')

django_asgi_app = get_asgi_application()

# ============================================
# Import des routes WebSocket (à venir)
# ============================================
# Quand tu créeras tes consumers, décommente ces lignes :
#
# from bus_tracking.routing import websocket_urlpatterns
#
# websocket_router = AllowedHostsOriginValidator(
#     AuthMiddlewareStack(
#         URLRouter(websocket_urlpatterns)
#     )
# )

# ============================================
# Application ASGI principale
# ============================================
application = ProtocolTypeRouter({
    # HTTP classique (Django)
    "http": django_asgi_app,

    # WebSocket (à activer plus tard)
    # "websocket": websocket_router,
})