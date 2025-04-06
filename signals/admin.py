from django.contrib import admin
from .models import Strategy, Signal, BacktestResult

@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = ('pair', 'strategy', 'signal_type', 'timeframe', 'entry_price', 'confidence', 'timestamp', 'is_active')
    search_fields = ('pair__symbol', 'strategy__name', 'notes')
    list_filter = ('signal_type', 'timeframe', 'is_active', 'strategy', 'pair', 'timestamp')
    date_hierarchy = 'timestamp'
    readonly_fields = ('created_at',)

@admin.register(BacktestResult)
class BacktestResultAdmin(admin.ModelAdmin):
    list_display = ('strategy', 'pair', 'timeframe', 'start_date', 'end_date', 'total_trades', 'win_rate', 'profit_factor', 'created_at')
    search_fields = ('strategy__name', 'pair__symbol')
    list_filter = ('strategy', 'pair', 'timeframe')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)