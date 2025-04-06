from django.contrib import admin
from .models import Currency, CurrencyPair, PriceData, EconomicIndicator, EconomicData

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active')
    search_fields = ('code', 'name')
    list_filter = ('is_active',)

@admin.register(CurrencyPair)
class CurrencyPairAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'base_currency', 'quote_currency', 'is_active')
    search_fields = ('symbol',)
    list_filter = ('is_active', 'base_currency', 'quote_currency')

@admin.register(PriceData)
class PriceDataAdmin(admin.ModelAdmin):
    list_display = ('pair', 'timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume')
    search_fields = ('pair__symbol',)
    list_filter = ('pair', 'timestamp')
    date_hierarchy = 'timestamp'

@admin.register(EconomicIndicator)
class EconomicIndicatorAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'country', 'is_active')
    search_fields = ('code', 'name', 'country')
    list_filter = ('is_active', 'country')

@admin.register(EconomicData)
class EconomicDataAdmin(admin.ModelAdmin):
    list_display = ('indicator', 'timestamp', 'value', 'previous_value', 'forecast_value')
    search_fields = ('indicator__code', 'indicator__name')
    list_filter = ('indicator', 'timestamp')
    date_hierarchy = 'timestamp'