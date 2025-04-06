from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.routers import DefaultRouter

# Import des viewsets d'API
from users.views import UserViewSet
from market_data.views import (CurrencyViewSet, CurrencyPairViewSet, 
                              PriceDataViewSet, EconomicIndicatorViewSet, 
                              EconomicDataViewSet)
from signals.views import StrategyViewSet, SignalViewSet, BacktestResultViewSet

# Création du routeur pour l'API REST
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
    
    # API REST
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    
    # Authentication
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # Dashboard
    path('', include('dashboard.urls')),
]