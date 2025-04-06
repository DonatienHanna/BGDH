import requests
import pandas as pd
from datetime import datetime, timedelta
from django.conf import settings
from .models import Currency, CurrencyPair, PriceData

# Clé API Alpha Vantage (à configurer dans settings.py)
API_KEY = getattr(settings, 'ALPHA_VANTAGE_API_KEY', '073XRZ4KX6ENI78E')

class MarketDataService:
    """Service pour récupérer les données de marché depuis Alpha Vantage"""
    
    @staticmethod
    def fetch_forex_data(symbol, interval='1h', outputsize='compact'):
        """
        Récupère les données forex depuis Alpha Vantage
        
        Args:
            symbol (str): Symbole de la paire de devises (ex: EURUSD)
            interval (str): Intervalle de temps ('1min', '5min', '15min', '30min', '60min', 'daily')
            outputsize (str): Taille de la sortie ('compact' = 100 dernières données, 'full' = toutes les données)
        
        Returns:
            pandas.DataFrame: DataFrame contenant les données OHLCV
        """
        # Convertir l'intervalle Django en format Alpha Vantage
        av_interval_map = {
            '1m': '1min', '5m': '5min', '15m': '15min', '30m': '30min',
            '1h': '60min', '1d': 'daily', '1w': 'weekly', '1mo': 'monthly'
        }
        av_interval = av_interval_map.get(interval, '60min')
        
        # Construire l'URL de l'API
        function = 'FX_INTRADAY' if av_interval != 'daily' else 'FX_DAILY'
        from_symbol, to_symbol = symbol[:3], symbol[3:]
        
        url = f'https://www.alphavantage.co/query'
        params = {
            'function': function,
            'from_symbol': from_symbol,
            'to_symbol': to_symbol,
            'interval': av_interval if function == 'FX_INTRADAY' else None,
            'outputsize': outputsize,
            'apikey': API_KEY
        }
        
        # Filtrer les paramètres None
        params = {k: v for k, v in params.items() if v is not None}
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # Vérifier s'il y a une erreur dans la réponse
            if 'Error Message' in data:
                print(f"API Error: {data['Error Message']}")
                return None
            
            # Extraire les données de séries temporelles
            time_series_key = next((k for k in data.keys() if 'Time Series' in k), None)
            if not time_series_key or not data.get(time_series_key):
                print("No time series data found in response")
                return None
            
            time_series = data[time_series_key]
            
            # Convertir en DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            # Renommer les colonnes
            column_mapping = {
                '1. open': 'open',
                '2. high': 'high',
                '3. low': 'low',
                '4. close': 'close',
                '5. volume': 'volume'
            }
            df = df.rename(columns=column_mapping)
            
            # Convertir les types de données
            for col in ['open', 'high', 'low', 'close']:
                df[col] = pd.to_numeric(df[col])
            
            # Si volume existe (certaines API forex n'ont pas de volume)
            if 'volume' in df.columns:
                df['volume'] = pd.to_numeric(df['volume'])
            else:
                df['volume'] = 0
            
            # Ajouter l'index comme colonne de date
            df.reset_index(inplace=True)
            df.rename(columns={'index': 'timestamp'}, inplace=True)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            return df
            
        except Exception as e:
            print(f"Error fetching data from Alpha Vantage: {str(e)}")
            return None
    
    @staticmethod
    def update_forex_data(pair_symbol, interval='1h'):
        """
        Met à jour les données pour une paire de devises spécifique
        
        Args:
            pair_symbol (str): Symbole de la paire (ex: EURUSD)
            interval (str): Intervalle de temps
        
        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        try:
            # Récupérer la paire de devises
            try:
                pair = CurrencyPair.objects.get(symbol=pair_symbol)
            except CurrencyPair.DoesNotExist:
                # Créer la paire si elle n'existe pas
                base_code, quote_code = pair_symbol[:3], pair_symbol[3:]
                
                # Vérifier/créer les devises
                base_currency, _ = Currency.objects.get_or_create(
                    code=base_code,
                    defaults={'name': base_code}
                )
                quote_currency, _ = Currency.objects.get_or_create(
                    code=quote_code,
                    defaults={'name': quote_code}
                )
                
                # Créer la paire
                pair = CurrencyPair.objects.create(
                    base_currency=base_currency,
                    quote_currency=quote_currency,
                    symbol=pair_symbol,
                    is_active=True
                )
            
            # Récupérer la dernière date en base
            latest_price = PriceData.objects.filter(pair=pair).order_by('-timestamp').first()
            outputsize = 'compact'  # Par défaut, récupérer seulement les 100 dernières données
            
            if not latest_price:
                # Si aucune donnée, récupérer l'historique complet
                outputsize = 'full'
            
            # Récupérer les données depuis Alpha Vantage
            df = MarketDataService.fetch_forex_data(pair_symbol, interval, outputsize)
            
            if df is None or df.empty:
                return False
            
            # Filtrer les nouvelles données
            if latest_price:
                df = df[df['timestamp'] > latest_price.timestamp]
            
            # Enregistrer les données dans la base
            for _, row in df.iterrows():
                PriceData.objects.create(
                    pair=pair,
                    timestamp=row['timestamp'],
                    open_price=row['open'],
                    high_price=row['high'],
                    low_price=row['low'],
                    close_price=row['close'],
                    volume=row['volume']
                )
            
            print(f"Updated {len(df)} records for {pair_symbol}")
            return True
            
        except Exception as e:
            print(f"Error updating forex data for {pair_symbol}: {str(e)}")
            return False