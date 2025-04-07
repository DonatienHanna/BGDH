import requests
import pandas as pd
from datetime import datetime, timedelta
from django.conf import settings
from .models import Currency, CurrencyPair, PriceData

API_KEY = getattr(settings, 'ALPHA_VANTAGE_API_KEY', '073XRZ4KX6ENI78E')

class MarketDataService:
    """Service pour récupérer les données de marché depuis Alpha Vantage"""
    
    #here 
        #comments here
    # market_data/services.py
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
        
        # Extraire les symboles from/to
        from_symbol, to_symbol = symbol[:3], symbol[3:]
        
        # Déterminer la fonction API appropriée
        if interval in ['1d', '1day', 'daily']:
            function = 'FX_DAILY'
            url = f'https://www.alphavantage.co/query?function={function}&from_symbol={from_symbol}&to_symbol={to_symbol}&outputsize={outputsize}&apikey={API_KEY}'
        elif interval in ['1w', '1week', 'weekly']:
            function = 'FX_WEEKLY'
            url = f'https://www.alphavantage.co/query?function={function}&from_symbol={from_symbol}&to_symbol={to_symbol}&apikey={API_KEY}'
        elif interval in ['1mo', '1month', 'monthly']:
            function = 'FX_MONTHLY'
            url = f'https://www.alphavantage.co/query?function={function}&from_symbol={from_symbol}&to_symbol={to_symbol}&apikey={API_KEY}'
        else:
            function = 'FX_INTRADAY'
            url = f'https://www.alphavantage.co/query?function={function}&from_symbol={from_symbol}&to_symbol={to_symbol}&interval={av_interval}&outputsize={outputsize}&apikey={API_KEY}'
        
        print(f"Requesting data from: {url}")
        
        try:
            response = requests.get(url)
            data = response.json()
            
            # Vérifier s'il y a une erreur dans la réponse
            if 'Error Message' in data:
                print(f"API Error: {data['Error Message']}")
                return None
            
            if 'Information' in data:
                print(f"API Info: {data['Information']}")
                # Si c'est un message concernant la limite d'appels API, retourner None
                if 'call frequency' in data['Information']:
                    return None
            
            # Extraire les données de séries temporelles
            time_series_key = None
            for key in data.keys():
                if 'Time Series' in key:
                    time_series_key = key
                    break
            
            if not time_series_key or not data.get(time_series_key):
                print("No time series data found in response")
                print(f"Response keys: {data.keys()}")
                return None
            
            time_series = data[time_series_key]
            
            # Convertir en DataFrame
            df = pd.DataFrame.from_dict(time_series, orient='index')
            
            # Identifier les noms de colonnes (ils peuvent varier)
            column_mapping = {}
            for col in df.columns:
                if 'open' in col.lower():
                    column_mapping[col] = 'open'
                elif 'high' in col.lower():
                    column_mapping[col] = 'high'
                elif 'low' in col.lower():
                    column_mapping[col] = 'low'
                elif 'close' in col.lower():
                    column_mapping[col] = 'close'
                elif 'volume' in col.lower():
                    column_mapping[col] = 'volume'
            
            # Renommer les colonnes
            df = df.rename(columns=column_mapping)
            
            # Convertir les types de données
            for col in ['open', 'high', 'low', 'close']:
                if col in df.columns:
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