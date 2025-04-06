# signals/tasks.py
from celery import shared_task
from market_data.models import CurrencyPair
from .analysis import SignalGenerator  # Assurez-vous que ce fichier existe

@shared_task
def generate_bollinger_bands_signals_task(pair_symbol=None):
    """
    Tâche Celery pour générer des signaux basés sur les bandes de Bollinger
    
    Args:
        pair_symbol (str, optional): Symbole de la paire. Si None, génère des signaux pour toutes les paires actives.
    
    Returns:
        dict: Résultats de la génération de signaux
    """
    results = {}
    
    if pair_symbol:
        # Générer des signaux pour une paire spécifique
        result = SignalGenerator.generate_bollinger_bands_signals(pair_symbol)
        results[pair_symbol] = result
    else:
        # Générer des signaux pour toutes les paires actives
        pairs = CurrencyPair.objects.filter(is_active=True)
        for pair in pairs:
            result = SignalGenerator.generate_bollinger_bands_signals(pair.symbol)
            results[pair.symbol] = result
    
    return results

@shared_task
def generate_williams_r_signals_task(pair_symbol=None):
    """
    Tâche Celery pour générer des signaux basés sur Williams %R
    
    Args:
        pair_symbol (str, optional): Symbole de la paire. Si None, génère des signaux pour toutes les paires actives.
    
    Returns:
        dict: Résultats de la génération de signaux
    """
    results = {}
    
    if pair_symbol:
        # Générer des signaux pour une paire spécifique
        result = SignalGenerator.generate_williams_r_signals(pair_symbol)
        results[pair_symbol] = result
    else:
        # Générer des signaux pour toutes les paires actives
        pairs = CurrencyPair.objects.filter(is_active=True)
        for pair in pairs:
            result = SignalGenerator.generate_williams_r_signals(pair.symbol)
            results[pair.symbol] = result
    
    return results

@shared_task
def generate_stochastic_signals_task(pair_symbol=None):
    """
    Tâche Celery pour générer des signaux basés sur l'oscillateur stochastique
    
    Args:
        pair_symbol (str, optional): Symbole de la paire. Si None, génère des signaux pour toutes les paires actives.
    
    Returns:
        dict: Résultats de la génération de signaux
    """
    results = {}
    
    if pair_symbol:
        # Générer des signaux pour une paire spécifique
        result = SignalGenerator.generate_stochastic_signals(pair_symbol)
        results[pair_symbol] = result
    else:
        # Générer des signaux pour toutes les paires actives
        pairs = CurrencyPair.objects.filter(is_active=True)
        for pair in pairs:
            result = SignalGenerator.generate_stochastic_signals(pair.symbol)
            results[pair.symbol] = result
    
    return results

@shared_task
def generate_combined_strategy_signals_task(pair_symbol=None, timeframe='1h'):
    """
    Tâche Celery pour générer des signaux basés sur la stratégie combinée
    
    Args:
        pair_symbol (str, optional): Symbole de la paire. Si None, génère des signaux pour toutes les paires actives.
        timeframe (str): Intervalle de temps ('1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1mo')
    
    Returns:
        dict: Résultats de la génération de signaux
    """
    results = {}
    
    if pair_symbol:
        # Générer des signaux pour une paire spécifique
        result = SignalGenerator.generate_combined_strategy_signals(pair_symbol, timeframe)
        results[pair_symbol] = result
    else:
        # Générer des signaux pour toutes les paires actives
        pairs = CurrencyPair.objects.filter(is_active=True)
        for pair in pairs:
            result = SignalGenerator.generate_combined_strategy_signals(pair.symbol, timeframe)
            results[pair.symbol] = result
    
    return results