from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from market_data.views import (CurrencyViewSet, CurrencyPairViewSet, 
                              PriceDataViewSet, EconomicIndicatorViewSet, 
                              EconomicDataViewSet)
from signals.views import StrategyViewSet, SignalViewSet, BacktestResultViewSet

# Création du routeur
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'currencies', CurrencyViewSet)
router.register(r'currency-pairs', CurrencyPairViewSet)
router.register(r'price-data', PriceDataViewSet)
router.register(r'economic-indicators', EconomicIndicatorViewSet)
router.register(r'economic-data', EconomicDataViewSet)
router.register(r'strategies', StrategyViewSet)
router.register(r'signals', SignalViewSet)
router.register(r'backtest-results', BacktestResultViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
