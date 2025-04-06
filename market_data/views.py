from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Currency, CurrencyPair, PriceData, EconomicIndicator, EconomicData
from .serializers import (CurrencySerializer, CurrencyPairSerializer, 
                         PriceDataSerializer, EconomicIndicatorSerializer, 
                         EconomicDataSerializer)

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'name']

class CurrencyPairViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CurrencyPair.objects.filter(is_active=True)
    serializer_class = CurrencyPairSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['symbol']
    filterset_fields = ['base_currency', 'quote_currency', 'is_active']

class PriceDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PriceData.objects.all()
    serializer_class = PriceDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pair']
    
    def get_queryset(self):
        queryset = PriceData.objects.all().order_by('-timestamp')
        
        # Filtrer par paire de devises
        pair_id = self.request.query_params.get('pair', None)
        if pair_id:
            queryset = queryset.filter(pair_id=pair_id)
        
        # Filtrer par plage de dates
        start_date = self.request.query_params.get('start_date', None)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        end_date = self.request.query_params.get('end_date', None)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        # Limiter le nombre de résultats pour les performances
        limit = int(self.request.query_params.get('limit', 1000))
        return queryset[:limit]
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        pair_id = request.query_params.get('pair', None)
        if not pair_id:
            return Response({"error": "Pair ID is required"}, status=400)
        
        try:
            latest_price = PriceData.objects.filter(pair_id=pair_id).latest('timestamp')
            serializer = self.get_serializer(latest_price)
            return Response(serializer.data)
        except PriceData.DoesNotExist:
            return Response({"error": "No price data found for this pair"}, status=404)

class EconomicIndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EconomicIndicator.objects.filter(is_active=True)
    serializer_class = EconomicIndicatorSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'code', 'country']
    filterset_fields = ['country', 'is_active']

class EconomicDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EconomicData.objects.all().order_by('-timestamp')
    serializer_class = EconomicDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['indicator']
    
    def get_queryset(self):
        queryset = EconomicData.objects.all().order_by('-timestamp')
        
        # Filtrer par indicateur
        indicator_id = self.request.query_params.get('indicator', None)
        if indicator_id:
            queryset = queryset.filter(indicator_id=indicator_id)
        
        # Filtrer par pays
        country = self.request.query_params.get('country', None)
        if country:
            queryset = queryset.filter(indicator__country=country)
        
        # Filtrer par plage de dates
        start_date = self.request.query_params.get('start_date', None)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        end_date = self.request.query_params.get('end_date', None)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        # Limiter le nombre de résultats
        limit = int(self.request.query_params.get('limit', 100))
        return queryset[:limit]