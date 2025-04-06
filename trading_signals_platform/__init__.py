default_app_config = 'trading_signals_platform.apps.TradingSignalsPlatformConfig'

# Celery config
try:
    from .celery import app as celery_app
    __all__ = ['celery_app']
except ImportError:
    # Pour permettre de démarrer même si Celery n'est pas configuré
    pass