# signals/tasks.py
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