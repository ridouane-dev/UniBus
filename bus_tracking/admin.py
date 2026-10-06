# bus_tracking/admin.py
from django.contrib import admin
from .models import BusLocation

@admin.register(BusLocation)
class BusLocationAdmin(admin.ModelAdmin):
    list_display = ['bus_name', 'latitude', 'longitude', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['bus_name']
    readonly_fields = ['updated_at']
    actions = ['mark_active', 'mark_inactive']
    
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)
    mark_active.short_description = "Marquer comme actif"
    
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
    mark_inactive.short_description = "Marquer comme inactif"