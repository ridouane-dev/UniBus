# bus_tracking/urls.py
from django.urls import path
from django.views.generic import TemplateView
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'bus_tracking'

urlpatterns = [
    # ============================================
    # API
    # ============================================
    path('api/buses/', views.get_all_buses, name='get_all_buses'),
    path('api/start/', views.start_service, name='start_service'),
    path('api/update/', views.update_location, name='update_location'),
    path('api/stop/', views.stop_service, name='stop_service'),
    path('api/bus/', views.get_bus_location, name='get_bus_location'),
    
    # Admin
    path('api/create-bus/', views.create_bus, name='create_bus'),
    path('api/delete-bus/', views.delete_bus, name='delete_bus'),
    
    # ============================================
    # PAGES HTML (PUBLIQUES - SANS AUTH)
    # ============================================
    
       # Page étudiante - Liste des bus (page d'accueil)
       
    path('',
         login_required(TemplateView.as_view(template_name='core/student_list.html')),
         name='student_list'),

    # Page étudiante - Carte
    path('student/map/',
         login_required(TemplateView.as_view(template_name='core/student_map.html')),
         name='student_map'),

    # Page chauffeur - Liste des bus
    path('driver/',
         login_required(TemplateView.as_view(template_name='core/driver_list.html')),
         name='driver_list'),

    # Page chauffeur - Dashboard (après démarrage)
    path('driver/dashboard/',
         login_required(TemplateView.as_view(template_name='core/driver_dashboard.html')),
         name='driver_dashboard'),
]