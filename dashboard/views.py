from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
import json
import pandas as pd

from market_data.models import CurrencyPair, PriceData
from signals.models import Signal, Strategy
from signals.analysis import SignalGenerator
from signals.tasks import generate_combined_strategy_signals_task

@login_required
def dashboard_home(request):
    """Vue pour la page d'accueil du tableau de bord"""
    # Récupérer les paires de devises actives
    currency_pairs = CurrencyPair.objects.filter(is_active=True)
    
    # Récupérer les stratégies actives
    strategies = Strategy.objects.filter(is_active=True)
    
    # Récupérer les derniers signaux
    latest_signals = Signal.objects.all().order_by('-timestamp')[:10]
    
    context = {
        'currency_pairs': currency_pairs,
        'strategies': strategies,
        'latest_signals': latest_signals,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def pair_detail(request, pair_id):
    """Vue pour la page de détail d'une paire de devises"""
    pair = get_object_or_404(CurrencyPair, id=pair_id)
    
    # Récupérer les derniers prix
    latest_price = PriceData.objects.filter(pair=pair).order_by('-timestamp').first()
    
    # Récupérer les derniers signaux pour cette paire
    latest_signals = Signal.objects.filter(pair=pair).order_by('-timestamp')[:10]
    
    # Calculer les statistiques
    yesterday = timezone.now() - timedelta(days=1)
    
    # Prix d'il y a 24h
    previous_price = PriceData.objects.filter(
        pair=pair, 
        timestamp__lte=yesterday
    ).order_by('-timestamp').first()
    
    # Variation sur 24h
    daily_change = 0
    if previous_price and latest_price:
        daily_change = ((latest_price.close_price - previous_price.close_price) / previous_price.close_price) * 100
    
    # Volume sur 24h
    daily_volume = PriceData.objects.filter(
        pair=pair, 
        timestamp__gte=yesterday
    ).aggregate(total_volume=Sum('volume'))['total_volume'] or 0
    
    # Nombre de signaux d'achat et de vente
    buy_signals_count = Signal.objects.filter(pair=pair, signal_type='BUY').count()
    sell_signals_count = Signal.objects.filter(pair=pair, signal_type='SELL').count()
    
    context = {
        'pair': pair,
        'latest_price': latest_price,
        'latest_signals': latest_signals,
        'daily_change': daily_change,
        'daily_volume': daily_volume,
        'buy_signals_count': buy_signals_count,
        'sell_signals_count': sell_signals_count,
    }
    
    return render(request, 'dashboard/pair_detail.html', context)

@login_required
def strategy_detail(request, strategy_id):
    """Vue pour la page de détail d'une stratégie"""
    strategy = get_object_or_404(Strategy, id=strategy_id)
    
    # Récupérer les derniers signaux pour cette stratégie
    latest_signals = Signal.objects.filter(strategy=strategy).order_by('-timestamp')[:20]
    
    # Calculer les statistiques de performance
    total_signals = Signal.objects.filter(strategy=strategy).count()
    buy_signals = Signal.objects.filter(strategy=strategy, signal_type='BUY').count()
    sell_signals = Signal.objects.filter(strategy=strategy, signal_type='SELL').count()
    avg_confidence = Signal.objects.filter(strategy=strategy).aggregate(Avg('confidence'))['confidence__avg'] or 0
    
    # Distribution des signaux par paire
    signals_by_pair = Signal.objects.filter(strategy=strategy).values('pair__symbol').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'strategy': strategy,
        'latest_signals': latest_signals,
        'total_signals': total_signals,
        'buy_signals': buy_signals,
        'sell_signals': sell_signals,
        'avg_confidence': avg_confidence,
        'signals_by_pair': signals_by_pair,
    }
    
    return render(request, 'dashboard/strategy_detail.html', context)

@login_required
def signals_list(request):
    """Vue pour la liste de tous les signaux"""
    # Filtrer les signaux
    pair_id = request.GET.get('pair')
    strategy_id = request.GET.get('strategy')
    signal_type = request.GET.get('type')
    days = request.GET.get('days', 7)
    
    # Construire la requête de base
    signals = Signal.objects.filter(
        timestamp__gte=timezone.now() - timedelta(days=int(days))
    ).order_by('-timestamp')
    
    # Appliquer les filtres
    if pair_id:
        signals = signals.filter(pair_id=pair_id)
    
    if strategy_id:
        signals = signals.filter(strategy_id=strategy_id)
    
    if signal_type:
        signals = signals.filter(signal_type=signal_type)
    
    # Récupérer les paires et stratégies pour les filtres
    pairs = CurrencyPair.objects.filter(is_active=True)
    strategies = Strategy.objects.filter(is_active=True)
    
    context = {
        'signals': signals,
        'pairs': pairs,
        'strategies': strategies,
        'selected_pair': pair_id,
        'selected_strategy': strategy_id,
        'selected_type': signal_type,
        'selected_days': days,
    }
    
    return render(request, 'dashboard/signals_list.html', context)

@login_required
def generate_signal(request, pair_id):
    """Vue pour générer manuellement un signal"""
    if request.method == 'POST':
        pair = get_object_or_404(CurrencyPair, id=pair_id)
        strategy_type = request.POST.get('strategy', 'combined')
        timeframe = request.POST.get('timeframe', '1h')
        
        # Générer le signal
        result = None
        if strategy_type == 'combined':
            # Appeler directement la fonction pour avoir un retour immédiat
            result = SignalGenerator.generate_combined_strategy_signals(pair.symbol, timeframe)
        elif strategy_type == 'bollinger':
            result = SignalGenerator.generate_bollinger_bands_signals(pair.symbol, timeframe)
        elif strategy_type == 'williams':
            result = SignalGenerator.generate_williams_r_signals(pair.symbol, timeframe)
        elif strategy_type == 'stochastic':
            result = SignalGenerator.generate_stochastic_signals(pair.symbol, timeframe)
        
        # Rediriger vers la page de détail de la paire
        return redirect('pair_detail', pair_id=pair_id)
    
    # Si ce n'est pas une requête POST, rediriger vers la page de détail
    return redirect('pair_detail', pair_id=pair_id)

# dashboard/views.py (suite)

@login_required
def api_pair_chart_data(request, pair_id):
    """API pour récupérer les données de graphique pour une paire"""
    pair = get_object_or_404(CurrencyPair, id=pair_id)
    timeframe = request.GET.get('timeframe', '1d')
    
    # Récupérer les données de prix
    df = SignalGenerator.get_price_data(pair.symbol, timeframe=timeframe, limit=100)
    
    if df is None or len(df) < 27:  # Minimum requis pour les calculs
        return JsonResponse({'error': 'Pas assez de données disponibles'})
    
    # Calculer les indicateurs
    # Bandes de Bollinger
    bb = TechnicalIndicators.calculate_bollinger_bands(
        df['close'], period=27, deviation=2.7, shift=0
    )
    df['bb_middle'] = bb['middle_band']
    df['bb_upper'] = bb['upper_band']
    df['bb_lower'] = bb['lower_band']
    
    # Williams %R
    df['williams_r'] = TechnicalIndicators.calculate_williams_r(
        df['high'], df['low'], df['close'], period=75
    )
    
    # Stochastique
    stoch = TechnicalIndicators.calculate_stochastic(
        df['high'], df['low'], df['close'], k_period=40, d_period=20, slowing=15
    )
    df['stoch_k'] = stoch['k']
    df['stoch_d'] = stoch['d']
    
    # Reset index pour avoir la date comme colonne
    df = df.reset_index()
    
    # Convertir les dates en chaînes de caractères pour JSON
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Données pour le graphique des prix OHLC
    price_data = {
        'timestamps': df['timestamp'].tolist(),
        'open': df['open'].tolist(),
        'high': df['high'].tolist(),
        'low': df['low'].tolist(),
        'close': df['close'].tolist(),
        'volume': df['volume'].tolist(),
    }
    
    # Données pour le graphique Bollinger
    bollinger_data = {
        'timestamps': df['timestamp'].tolist(),
        'close': df['close'].tolist(),
        'middle': df['bb_middle'].tolist(),
        'upper': df['bb_upper'].tolist(),
        'lower': df['bb_lower'].tolist(),
    }
    
    # Données pour le graphique Williams %R
    williams_data = {
        'timestamps': df['timestamp'].tolist(),
        'williams_r': df['williams_r'].tolist(),
        'overbought': [-20] * len(df),  # Ligne de surachat
        'oversold': [-80] * len(df),    # Ligne de survente
    }
    
    # Données pour le graphique Stochastique
    stochastic_data = {
        'timestamps': df['timestamp'].tolist(),
        'k': df['stoch_k'].tolist(),
        'd': df['stoch_d'].tolist(),
        'overbought': [80] * len(df),   # Ligne de surachat
        'oversold': [20] * len(df),     # Ligne de survente
    }
    
    # Récupérer les signaux récents pour cette paire
    recent_signals = Signal.objects.filter(
        pair=pair,
        timeframe=timeframe,
        timestamp__gte=timezone.now() - timedelta(days=7 if timeframe == '1d' else 2)
    ).order_by('-timestamp')[:10]
    
    # Convertir les signaux pour les afficher sur le graphique
    signal_data = []
    for signal in recent_signals:
        signal_data.append({
            'timestamp': signal.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'price': float(signal.entry_price),
            'type': signal.signal_type,
            'confidence': float(signal.confidence),
        })
    
    # Retourner toutes les données
    return JsonResponse({
        'price_data': price_data,
        'bollinger_data': bollinger_data,
        'williams_data': williams_data,
        'stochastic_data': stochastic_data,
        'signal_data': signal_data,
    })

@login_required
def api_pair_performance(request):
    """API pour récupérer les données de performance des paires"""
    # Récupérer les paires actives
    pairs = CurrencyPair.objects.filter(is_active=True)
    days = int(request.GET.get('days', 7))
    
    start_date = timezone.now() - timedelta(days=days)
    
    datasets = []
    labels = []
    
    # Générer des étiquettes pour les derniers jours
    for i in range(days):
        date = start_date + timedelta(days=i)
        labels.append(date.strftime('%d/%m'))
    
    # Récupérer les données pour chaque paire
    colors = ['#4e73df', '#1cc88a', '#f6c23e', '#e74a3b', '#36b9cc', '#6f42c1', '#fd7e14', '#20c9a6']
    
    for i, pair in enumerate(pairs):
        # Récupérer les prix de clôture pour la période
        prices = PriceData.objects.filter(
            pair=pair,
            timestamp__gte=start_date
        ).order_by('timestamp')
        
        if not prices:
            continue
        
        # Calculer la variation en pourcentage par rapport au premier jour
        base_price = prices.first().close_price
        
        # Préparer les données pour le graphique
        data = []
        
        for j in range(days):
            date = start_date + timedelta(days=j)
            day_price = prices.filter(timestamp__date=date.date()).order_by('-timestamp').first()
            
            if day_price:
                # Variation en pourcentage
                percentage_change = ((day_price.close_price - base_price) / base_price) * 100
                data.append(float(percentage_change))
            else:
                # Si pas de donnée pour ce jour, utiliser la dernière valeur connue
                data.append(data[-1] if data else 0)
        
        # Ajouter le dataset pour cette paire
        color_index = i % len(colors)
        datasets.append({
            'label': pair.symbol,
            'data': data,
            'borderColor': colors[color_index],
            'backgroundColor': 'transparent',
            'pointBackgroundColor': colors[color_index],
        })
    
    return JsonResponse({
        'labels': labels,
        'datasets': datasets,
    })