from celery import shared_task
from .services import MarketDataService
from .models import CurrencyPair

@shared_task
def update_forex_data_task(pair_symbol=None, interval='1h'):
    """
    Tâche Celery pour mettre à jour les données forex
    
    Args:
        pair_symbol (str, optional): Symbole de la paire à mettre à jour
                                     Si None, met à jour toutes les paires actives
        interval (str): Intervalle de temps
    
    Returns:
        dict: Résultats de la mise à jour
    """
    results = {}
    
    if pair_symbol:
        # Mettre à jour une paire spécifique
        success = MarketDataService.update_forex_data(pair_symbol, interval)
        results[pair_symbol] = "Success" if success else "Failed"
    else:
        # Mettre à jour toutes les paires actives
        pairs = CurrencyPair.objects.filter(is_active=True)
        for pair in pairs:
            success = MarketDataService.update_forex_data(pair.symbol, interval)
            results[pair.symbol] = "Success" if success else "Failed"
    
    return results