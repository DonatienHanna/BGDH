# signals/models.py
from django.db import models
from market_data.models import CurrencyPair

class Strategy(models.Model):
    """Modèle pour définir les stratégies de trading"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Signal(models.Model):
    """Modèle pour les signaux de trading générés"""
    SIGNAL_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('HOLD', 'Hold'),
    ]
    
    TIMEFRAMES = [
        ('1m', '1 Minute'),
        ('5m', '5 Minutes'),
        ('15m', '15 Minutes'),
        ('30m', '30 Minutes'),
        ('1h', '1 Hour'),
        ('4h', '4 Hours'),
        ('1d', '1 Day'),
        ('1w', '1 Week'),
    ]
    
    pair = models.ForeignKey(CurrencyPair, on_delete=models.CASCADE, related_name='signals')
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name='signals')
    signal_type = models.CharField(max_length=10, choices=SIGNAL_TYPES)
    timeframe = models.CharField(max_length=5, choices=TIMEFRAMES)
    entry_price = models.DecimalField(max_digits=18, decimal_places=8)
    stop_loss = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    take_profit = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    confidence = models.FloatField(help_text="Confidence level from 0 to 1")
    timestamp = models.DateTimeField()
    expiration = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['pair', 'timestamp']),
            models.Index(fields=['strategy', 'timestamp']),
            models.Index(fields=['signal_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.pair.symbol} - {self.signal_type} - {self.timestamp}"

class BacktestResult(models.Model):
    """Modèle pour stocker les résultats des backtests de stratégies"""
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name='backtests')
    pair = models.ForeignKey(CurrencyPair, on_delete=models.CASCADE, related_name='backtests')
    timeframe = models.CharField(max_length=5, choices=Signal.TIMEFRAMES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_trades = models.IntegerField()
    winning_trades = models.IntegerField()
    losing_trades = models.IntegerField()
    win_rate = models.FloatField()
    profit_factor = models.FloatField()
    max_drawdown = models.FloatField()
    sharpe_ratio = models.FloatField(null=True, blank=True)
    sortino_ratio = models.FloatField(null=True, blank=True)
    result_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.strategy.name} - {self.pair.symbol} - {self.start_date.date()} to {self.end_date.date()}"