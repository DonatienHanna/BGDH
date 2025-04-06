from rest_framework import serializers
from .models import Currency, CurrencyPair, PriceData, EconomicIndicator, EconomicData

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

class CurrencyPairSerializer(serializers.ModelSerializer):
    base_currency_code = serializers.ReadOnlyField(source='base_currency.code')
    quote_currency_code = serializers.ReadOnlyField(source='quote_currency.code')
    
    class Meta:
        model = CurrencyPair
        fields = ['id', 'symbol', 'base_currency', 'quote_currency', 
                  'base_currency_code', 'quote_currency_code', 'is_active']

class PriceDataSerializer(serializers.ModelSerializer):
    pair_symbol = serializers.ReadOnlyField(source='pair.symbol')
    
    class Meta:
        model = PriceData
        fields = ['id', 'pair', 'pair_symbol', 'timestamp', 'open_price', 
                  'high_price', 'low_price', 'close_price', 'volume']

class EconomicIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicIndicator
        fields = '__all__'

class EconomicDataSerializer(serializers.ModelSerializer):
    indicator_name = serializers.ReadOnlyField(source='indicator.name')
    
    class Meta:
        model = EconomicData
        fields = ['id', 'indicator', 'indicator_name', 'timestamp', 
                  'value', 'previous_value', 'forecast_value']