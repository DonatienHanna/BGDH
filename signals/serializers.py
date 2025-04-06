from rest_framework import serializers
from .models import Strategy, Signal, BacktestResult

class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = '__all__'

class SignalSerializer(serializers.ModelSerializer):
    pair_symbol = serializers.ReadOnlyField(source='pair.symbol')
    strategy_name = serializers.ReadOnlyField(source='strategy.name')
    
    class Meta:
        model = Signal
        fields = ['id', 'pair', 'pair_symbol', 'strategy', 'strategy_name', 
                  'signal_type', 'timeframe', 'entry_price', 'stop_loss', 
                  'take_profit', 'confidence', 'timestamp', 'expiration', 
                  'notes', 'is_active', 'created_at']

class BacktestResultSerializer(serializers.ModelSerializer):
    strategy_name = serializers.ReadOnlyField(source='strategy.name')
    pair_symbol = serializers.ReadOnlyField(source='pair.symbol')
    
    class Meta:
        model = BacktestResult
        fields = ['id', 'strategy', 'strategy_name', 'pair', 'pair_symbol', 
                  'timeframe', 'start_date', 'end_date', 'total_trades', 
                  'winning_trades', 'losing_trades', 'win_rate', 'profit_factor', 
                  'max_drawdown', 'sharpe_ratio', 'sortino_ratio', 
                  'result_data', 'created_at']