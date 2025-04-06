from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Strategy, Signal, BacktestResult
from .serializers import StrategySerializer, SignalSerializer, BacktestResultSerializer

class StrategyViewSet(viewsets.ModelViewSet):
    queryset = Strategy.objects.filter(is_active=True)
    serializer_class = StrategySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

class SignalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Signal.objects.filter(is_active=True).order_by('-timestamp')
    serializer_class = SignalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pair', 'strategy', 'signal_type', 'timeframe']
    
    def get_queryset(self):
        queryset = Signal.objects.filter(is_active=True).order_by('-timestamp')
        
        # Filtres additionnels
        pair_id = self.request.query_params.get('pair', None)
        if pair_id:
            queryset = queryset.filter(pair_id=pair_id)
        
        strategy_id = self.request.query_params.get('strategy', None)
        if strategy_id:
            queryset = queryset.filter(strategy_id=strategy_id)
        
        signal_type = self.request.query_params.get('signal_type', None)
        if signal_type:
            queryset = queryset.filter(signal_type=signal_type)
        
        # Filtre par date
        start_date = self.request.query_params.get('start_date', None)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        end_date = self.request.query_params.get('end_date', None)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        # Limite du nombre de résultats
        limit = int(self.request.query_params.get('limit', 50))
        return queryset[:limit]
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        # Récupère les derniers signaux pour chaque stratégie et paire
        pair_id = request.query_params.get('pair', None)
        timeframe = request.query_params.get('timeframe', None)
        
        queryset = self.get_queryset()
        
        if pair_id:
            queryset = queryset.filter(pair_id=pair_id)
        
        if timeframe:
            queryset = queryset.filter(timeframe=timeframe)
        
        # Groupe par stratégie et récupère le dernier signal pour chaque
        latest_signals = {}
        for signal in queryset:
            key = f"{signal.strategy_id}_{signal.pair_id}"
            if key not in latest_signals or signal.timestamp > latest_signals[key].timestamp:
                latest_signals[key] = signal
        
        serializer = self.get_serializer(list(latest_signals.values()), many=True)
        return Response(serializer.data)

class BacktestResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BacktestResult.objects.all().order_by('-created_at')
    serializer_class = BacktestResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['strategy', 'pair', 'timeframe']