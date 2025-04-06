from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('pair/<int:pair_id>/', views.pair_detail, name='pair_detail'),
    path('strategy/<int:strategy_id>/', views.strategy_detail, name='strategy_detail'),
    path('signals/', views.signals_list, name='signals_list'),
    path('generate-signal/<int:pair_id>/', views.generate_signal, name='generate_signal'),
    
    # API endpoints
    path('api/pair/<int:pair_id>/chart-data/', views.api_pair_chart_data, name='api_pair_chart_data'),
    path('api/pair-performance/', views.api_pair_performance, name='api_pair_performance'),
]