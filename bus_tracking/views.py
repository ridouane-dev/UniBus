# bus_tracking/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import BusLocation
import json

# ============================================
# API - LISTE DES BUS (pour chauffeurs et étudiants)
# ============================================

def get_all_buses(request):
    """
    Récupère TOUS les bus (actifs ET inactifs)
    GET /api/buses/
    """
    buses = BusLocation.objects.all()
    
    data = []
    for bus in buses:
        data.append({
            'bus_name': bus.bus_name,
            'lat': bus.latitude,
            'lng': bus.longitude,
            'is_active': bus.is_active,
            'updated_at': bus.updated_at.strftime('%H:%M:%S')
        })
    
    return JsonResponse(data, safe=False)

# ============================================
# API - DÉMARRER LE SERVICE (chauffeur)
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
def start_service(request):
    """
    Le chauffeur démarre le service pour un bus spécifique
    POST /api/start/
    Body: { "bus_name": "Bus A", "lat": 48.8566, "lng": 2.3522 }
    """
    try:
        data = json.loads(request.body)
        bus_name = data.get('bus_name')
        lat = data.get('lat')
        lng = data.get('lng')
        
        if not bus_name:
            return JsonResponse({'error': 'bus_name requis'}, status=400)
        
        if lat is None or lng is None:
            return JsonResponse({'error': 'lat et lng requis'}, status=400)
        
        # Mettre à jour ou créer le bus
        bus, created = BusLocation.objects.update_or_create(
            bus_name=bus_name,
            defaults={
                'latitude': lat,
                'longitude': lng,
                'is_active': True
            }
        )
        
        return JsonResponse({
            'status': 'started',
            'bus': bus.bus_name,
            'is_active': bus.is_active
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================
# API - ENVOI POSITION (chauffeur)
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
def update_location(request):
    """
    Le chauffeur envoie la position GPS
    POST /api/update/
    Body: { "bus_name": "Bus A", "lat": 48.8567, "lng": 2.3523 }
    """
    try:
        data = json.loads(request.body)
        bus_name = data.get('bus_name')
        lat = data.get('lat')
        lng = data.get('lng')
        
        if not bus_name:
            return JsonResponse({'error': 'bus_name requis'}, status=400)
        
        if lat is None or lng is None:
            return JsonResponse({'error': 'lat et lng requis'}, status=400)
        
        # Mettre à jour la position
        bus, created = BusLocation.objects.update_or_create(
            bus_name=bus_name,
            defaults={
                'latitude': lat,
                'longitude': lng,
                # On garde is_active comme il est (ne pas changer)
            }
        )
        
        return JsonResponse({
            'status': 'ok',
            'bus': bus.bus_name,
            'updated_at': bus.updated_at.strftime('%H:%M:%S')
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================
# API - ARRÊTER LE SERVICE (chauffeur)
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
def stop_service(request):
    """
    Le chauffeur arrête le service
    POST /api/stop/
    Body: { "bus_name": "Bus A" }
    """
    try:
        data = json.loads(request.body)
        bus_name = data.get('bus_name')
        
        if not bus_name:
            return JsonResponse({'error': 'bus_name requis'}, status=400)
        
        try:
            bus = BusLocation.objects.get(bus_name=bus_name)
            bus.is_active = False
            bus.save()
            
            return JsonResponse({
                'status': 'stopped',
                'bus': bus.bus_name
            })
        except BusLocation.DoesNotExist:
            return JsonResponse({'error': 'Bus non trouvé'}, status=404)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================
# API - POSITION D'UN BUS SPÉCIFIQUE (étudiant)
# ============================================

# bus_tracking/views.py (ajout)

def get_bus_location(request):
    """
    Récupère la position d'un bus spécifique (pour Google Maps)
    GET /api/bus/?bus_name=Bus%20A
    """
    bus_name = request.GET.get('bus_name')
    
    if not bus_name:
        return JsonResponse({'error': 'bus_name requis'}, status=400)
    
    try:
        bus = BusLocation.objects.get(bus_name=bus_name)
        return JsonResponse({
            'bus_name': bus.bus_name,
            'lat': bus.latitude,
            'lng': bus.longitude,
            'is_active': bus.is_active,
            'updated_at': bus.updated_at.strftime('%H:%M:%S'),
            'timestamp': bus.updated_at.isoformat()
        })
    except BusLocation.DoesNotExist:
        return JsonResponse({'error': 'Bus non trouvé'}, status=404)

# ============================================
# API - CRÉER UN NOUVEAU BUS (admin seulement)
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
def create_bus(request):
    """
    Créer un nouveau bus (pour l'admin)
    POST /api/create-bus/
    Body: { "bus_name": "Bus D" }
    """
    try:
        data = json.loads(request.body)
        bus_name = data.get('bus_name')
        
        if not bus_name:
            return JsonResponse({'error': 'bus_name requis'}, status=400)
        
        if BusLocation.objects.filter(bus_name=bus_name).exists():
            return JsonResponse({'error': 'Ce bus existe déjà'}, status=400)
        
        # Créer un bus avec des coordonnées par défaut (0,0)
        bus = BusLocation.objects.create(
            bus_name=bus_name,
            latitude=0,
            longitude=0,
            is_active=False
        )
        
        return JsonResponse({
            'status': 'created',
            'bus': bus.bus_name
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================
# API - SUPPRIMER UN BUS (admin seulement)
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
def delete_bus(request):
    """
    Supprimer un bus
    POST /api/delete-bus/
    Body: { "bus_name": "Bus A" }
    """
    try:
        data = json.loads(request.body)
        bus_name = data.get('bus_name')
        
        if not bus_name:
            return JsonResponse({'error': 'bus_name requis'}, status=400)
        
        count, _ = BusLocation.objects.filter(bus_name=bus_name).delete()
        
        if count > 0:
            return JsonResponse({'status': 'deleted', 'bus': bus_name})
        else:
            return JsonResponse({'error': 'Bus non trouvé'}, status=404)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)