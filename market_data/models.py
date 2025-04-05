# market_data/models.py
from django.db import models

class Currency(models.Model):
    """Modèle pour stocker les informations sur les devises"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class CurrencyPair(models.Model):
    """Modèle pour les paires de devises"""
    base_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='base_pairs')
    quote_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='quote_pairs')
    symbol = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.symbol

class PriceData(models.Model):
    """Modèle pour stocker les données de prix historiques"""
    pair = models.ForeignKey(CurrencyPair, on_delete=models.CASCADE, related_name='prices')
    timestamp = models.DateTimeField()
    open_price = models.DecimalField(max_digits=18, decimal_places=8)
    high_price = models.DecimalField(max_digits=18, decimal_places=8)
    low_price = models.DecimalField(max_digits=18, decimal_places=8)
    close_price = models.DecimalField(max_digits=18, decimal_places=8)
    volume = models.DecimalField(max_digits=24, decimal_places=8)
    
    class Meta:
        unique_together = ('pair', 'timestamp')
        indexes = [
            models.Index(fields=['pair', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.pair.symbol} - {self.timestamp}"

class EconomicIndicator(models.Model):
    """Modèle pour stocker les indicateurs économiques"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    country = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.code} - {self.country}"

class EconomicData(models.Model):
    """Modèle pour stocker les données des indicateurs économiques"""
    indicator = models.ForeignKey(EconomicIndicator, on_delete=models.CASCADE, related_name='data_points')
    timestamp = models.DateTimeField()
    value = models.DecimalField(max_digits=18, decimal_places=4)
    previous_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    forecast_value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    
    class Meta:
        unique_together = ('indicator', 'timestamp')
        indexes = [
            models.Index(fields=['indicator', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.indicator.code} - {self.timestamp}"