from django.db import models

class BusLocation(models.Model):
    """Position d'un bus en temps réel - 1 table unique"""
    bus_name = models.CharField(max_length=50, default="Bus 1")
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        status = "🟢" if self.is_active else "🔴"
        return f"{status} {self.bus_name} - {self.latitude}, {self.longitude}"
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Position du bus"
        verbose_name_plural = "Positions des bus"