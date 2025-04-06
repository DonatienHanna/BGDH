# signals/analysis.py
# Conservons les importations et autres fonctions existantes et ajoutons/modifions les indicateurs demandés

class TechnicalIndicators:
    """Classe utilitaire pour calculer des indicateurs techniques"""
    
    # Conservons les méthodes existantes (calculate_sma, calculate_ema, calculate_rsi, calculate_macd, calculate_atr)
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=27, deviation=2.7, shift=0):
        """
        Calcule les bandes de Bollinger avec paramètres personnalisés
        
        Args:
            prices (pd.Series): Série de prix
            period (int): Période pour le calcul de la moyenne mobile (défaut: 27)
            deviation (float): Facteur de déviation standard (défaut: 2.7)
            shift (int): Décalage de la moyenne mobile (défaut: 0)
        
        Returns:
            dict: Dictionnaire contenant les bandes supérieure, moyenne et inférieure
        """
        # Calculer la moyenne mobile
        if shift == 0:
            middle_band = prices.rolling(window=period).mean()
        else:
            middle_band = prices.rolling(window=period).mean().shift(shift)
        
        # Calculer l'écart-type
        std = prices.rolling(window=period).std()
        
        # Calculer les bandes supérieure et inférieure
        upper_band = middle_band + (std * deviation)
        lower_band = middle_band - (std * deviation)
        
        return {
            'middle_band': middle_band,
            'upper_band': upper_band,
            'lower_band': lower_band
        }
    
    @staticmethod
    def calculate_williams_r(high, low, close, period=75):
        """
        Calcule l'indicateur Williams %R
        
        Args:
            high (pd.Series): Série des prix les plus hauts
            low (pd.Series): Série des prix les plus bas
            close (pd.Series): Série des prix de clôture
            period (int): Période pour le calcul (défaut: 75)
        
        Returns:
            pd.Series: Série contenant les valeurs de Williams %R
        """
        # Plus haut sur la période
        highest_high = high.rolling(window=period).max()
        
        # Plus bas sur la période
        lowest_low = low.rolling(window=period).min()
        
        # Calcul du Williams %R
        # La formule est: %R = -100 * (highest_high - close) / (highest_high - lowest_low)
        williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
        
        return williams_r
    
    @staticmethod
    def calculate_stochastic(high, low, close, k_period=40, d_period=20, slowing=15):
        """
        Calcule l'oscillateur stochastique
        
        Args:
            high (pd.Series): Série des prix les plus hauts
            low (pd.Series): Série des prix les plus bas
            close (pd.Series): Série des prix de clôture
            k_period (int): Période %K (défaut: 40)
            d_period (int): Période %D (défaut: 20)
            slowing (int): Période de ralentissement (défaut: 15)
        
        Returns:
            dict: Dictionnaire contenant %K et %D
        """
        # Plus bas sur la période
        lowest_low = low.rolling(window=k_period).min()
        
        # Plus haut sur la période
        highest_high = high.rolling(window=k_period).max()
        
        # Calcul du %K rapide (sans ralentissement)
        k_fast = 100 * (close - lowest_low) / (highest_high - lowest_low)
        
        # Application du ralentissement au %K
        k_slow = k_fast.rolling(window=slowing).mean()
        
        # Calcul du %D (moyenne mobile du %K ralenti)
        d_slow = k_slow.rolling(window=d_period).mean()
        
        return {
            'k': k_slow,
            'd': d_slow
        }
        
class SignalGenerator:
    # Conservons les méthodes existantes (get_price_data, etc.)
    
    @staticmethod
    def generate_bollinger_bands_signals(pair_symbol, period=27, deviation=2.7, shift=0):
        """
        Génère des signaux basés sur les bandes de Bollinger
        
        Args:
            pair_symbol (str): Symbole de la paire
            period (int): Période (défaut: 27)
            deviation (float): Déviation standard (défaut: 2.7)
            shift (int): Décalage (défaut: 0)
        
        Returns:
            dict: Dernier signal généré
        """
        try:
            # Récupérer les données de prix
            df = SignalGenerator.get_price_data(pair_symbol, limit=period * 3)
            if df is None or len(df) < period + 5:
                return None
            
            # Calculer les bandes de Bollinger
            bb = TechnicalIndicators.calculate_bollinger_bands(
                df['close'], period, deviation, shift
            )
            
            df['middle_band'] = bb['middle_band']
            df['upper_band'] = bb['upper_band']
            df['lower_band'] = bb['lower_band']
            
            # Générer les signaux
            df['signal'] = 0  # 0 = pas de signal, 1 = achat, -1 = vente
            
            # Signal d'achat: le prix touche ou passe sous la bande inférieure
            df.loc[df['close'] <= df['lower_band'], 'signal'] = 1
            
            # Signal de vente: le prix touche ou passe au-dessus de la bande supérieure
            df.loc[df['close'] >= df['upper_band'], 'signal'] = -1
            
            # Récupérer le dernier signal
            last_row = df.iloc[-1]
            signal_type = None
            
            if last_row['signal'] == 1:
                signal_type = 'BUY'
            elif last_row['signal'] == -1:
                signal_type = 'SELL'
            
            # Distance par rapport aux bandes (en pourcentage)
            upper_band_distance = ((last_row['upper_band'] - last_row['close']) / last_row['close']) * 100
            lower_band_distance = ((last_row['close'] - last_row['lower_band']) / last_row['close']) * 100
            
            # Retourner les informations
            result = {
                'pair': pair_symbol,
                'middle_band': float(last_row['middle_band']),
                'upper_band': float(last_row['upper_band']),
                'lower_band': float(last_row['lower_band']),
                'close': float(last_row['close']),
                'upper_band_distance': float(upper_band_distance),
                'lower_band_distance': float(lower_band_distance),
                'signal_type': signal_type if signal_type else 'HOLD',
                'entry_price': float(last_row['close']),
            }
            
            # Si un signal a été généré
            if signal_type:
                # Récupérer ou créer la stratégie
                strategy, _ = Strategy.objects.get_or_create(
                    name=f"Bollinger Bands ({period}/{deviation:.1f})",
                    defaults={'description': f"Bollinger Bands strategy with period {period}, deviation {deviation}, and shift {shift}"}
                )
                
                pair = CurrencyPair.objects.get(symbol=pair_symbol)
                
                # Calculer les niveaux de stop loss et take profit
                if signal_type == 'BUY':
                    stop_loss = last_row['close'] * 0.985  # -1.5% du prix d'entrée
                    take_profit = last_row['middle_band']  # Prendre profit à la bande moyenne
                else:  # SELL
                    stop_loss = last_row['close'] * 1.015  # +1.5% du prix d'entrée
                    take_profit = last_row['middle_band']  # Prendre profit à la bande moyenne
                
                # Calculer la confiance basée sur la distance par rapport à la bande
                if signal_type == 'BUY':
                    confidence = min(0.9, max(0.6, lower_band_distance / 2))
                else:  # SELL
                    confidence = min(0.9, max(0.6, upper_band_distance / 2))
                
                # Créer le signal
                signal = Signal.objects.create(
                    pair=pair,
                    strategy=strategy,
                    signal_type=signal_type,
                    timeframe='1h',
                    entry_price=last_row['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    confidence=confidence,
                    timestamp=timezone.now(),
                    expiration=timezone.now() + timedelta(days=1),
                    notes=f"Signal generated by Bollinger Bands ({period}/{deviation:.1f}) strategy"
                )
                
                # Ajouter les informations du signal au résultat
                result.update({
                    'signal_id': signal.id,
                    'stop_loss': float(stop_loss),
                    'take_profit': float(take_profit),
                    'confidence': confidence,
                    'timestamp': signal.timestamp
                })
            
            return result
            
        except Exception as e:
            print(f"Error generating Bollinger Bands signals: {str(e)}")
            return None
    
    @staticmethod
    def generate_williams_r_signals(pair_symbol, period=75, overbought=-20, oversold=-80):
        """
        Génère des signaux basés sur l'indicateur Williams %R
        
        Args:
            pair_symbol (str): Symbole de la paire
            period (int): Période (défaut: 75)
            overbought (int): Niveau de surachat (défaut: -20)
            oversold (int): Niveau de survente (défaut: -80)
        
        Returns:
            dict: Dernier signal généré
        """
        try:
            # Récupérer les données de prix
            df = SignalGenerator.get_price_data(pair_symbol, limit=period * 3)
            if df is None or len(df) < period + 5:
                return None
            
            # Calculer le Williams %R
            df['williams_r'] = TechnicalIndicators.calculate_williams_r(
                df['high'], df['low'], df['close'], period
            )
            
            # Générer les signaux
            df['signal'] = 0  # 0 = pas de signal, 1 = achat, -1 = vente
            
            # Signal d'achat: le Williams %R passe en dessous du niveau de survente
            df.loc[df['williams_r'] <= oversold, 'signal'] = 1
            
            # Signal de vente: le Williams %R passe au-dessus du niveau de surachat
            df.loc[df['williams_r'] >= overbought, 'signal'] = -1
            
            # Récupérer le dernier signal
            last_row = df.iloc[-1]
            signal_type = None
            
            if last_row['signal'] == 1:
                signal_type = 'BUY'
            elif last_row['signal'] == -1:
                signal_type = 'SELL'
            
            # Retourner les informations
            result = {
                'pair': pair_symbol,
                'williams_r': float(last_row['williams_r']),
                'oversold_level': oversold,
                'overbought_level': overbought,
                'signal_type': signal_type if signal_type else 'HOLD',
                'entry_price': float(last_row['close']),
            }
            
            # Si un signal a été généré
            if signal_type:
                # Récupérer ou créer la stratégie
                strategy, _ = Strategy.objects.get_or_create(
                    name=f"Williams %R ({period})",
                    defaults={'description': f"Williams %R strategy with period {period}, overbought level {overbought}, and oversold level {oversold}"}
                )
                
                pair = CurrencyPair.objects.get(symbol=pair_symbol)
                
                # Calculer les niveaux de stop loss et take profit basés sur l'ATR
                atr = TechnicalIndicators.calculate_atr(
                    df['high'], df['low'], df['close'], period=14
                ).iloc[-1]
                
                if signal_type == 'BUY':
                    stop_loss = last_row['close'] - (atr * 1.5)
                    take_profit = last_row['close'] + (atr * 2.5)
                else:  # SELL
                    stop_loss = last_row['close'] + (atr * 1.5)
                    take_profit = last_row['close'] - (atr * 2.5)
                
                # Calculer la confiance
                if signal_type == 'BUY':
                    # Plus le Williams %R est bas (sous le niveau de survente), plus la confiance est élevée
                    confidence = min(0.9, max(0.6, abs((oversold - last_row['williams_r']) / 20)))
                else:  # SELL
                    # Plus le Williams %R est haut (au-dessus du niveau de surachat), plus la confiance est élevée
                    confidence = min(0.9, max(0.6, abs((last_row['williams_r'] - overbought) / 20)))
                
                # Créer le signal
                signal = Signal.objects.create(
                    pair=pair,
                    strategy=strategy,
                    signal_type=signal_type,
                    timeframe='1h',
                    entry_price=last_row['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    confidence=confidence,
                    timestamp=timezone.now(),
                    expiration=timezone.now() + timedelta(days=1),
                    notes=f"Signal generated by Williams %R ({period}) strategy with value {last_row['williams_r']:.2f}"
                )
                
                # Ajouter les informations du signal au résultat
                result.update({
                    'signal_id': signal.id,
                    'stop_loss': float(stop_loss),
                    'take_profit': float(take_profit),
                    'confidence': confidence,
                    'timestamp': signal.timestamp
                })
            
            return result
            
        except Exception as e:
            print(f"Error generating Williams %R signals: {str(e)}")
            return None
    
    @staticmethod
    def generate_stochastic_signals(pair_symbol, k_period=40, d_period=20, slowing=15, overbought=80, oversold=20):
        """
        Génère des signaux basés sur l'oscillateur stochastique
        
        Args:
            pair_symbol (str): Symbole de la paire
            k_period (int): Période %K (défaut: 40)
            d_period (int): Période %D (défaut: 20)
            slowing (int): Période de ralentissement (défaut: 15)
            overbought (int): Niveau de surachat (défaut: 80)
            oversold (int): Niveau de survente (défaut: 20)
        
        Returns:
            dict: Dernier signal généré
        """
        try:
            # Récupérer les données de prix
            min_periods = max(k_period, d_period) + slowing + 10  # Pour s'assurer d'avoir assez de données
            df = SignalGenerator.get_price_data(pair_symbol, limit=min_periods * 2)
            if df is None or len(df) < min_periods:
                return None
            
            # Calculer l'oscillateur stochastique
            stoch = TechnicalIndicators.calculate_stochastic(
                df['high'], df['low'], df['close'], k_period, d_period, slowing
            )
            
            df['k'] = stoch['k']
            df['d'] = stoch['d']
            
            # Générer les signaux
            df['signal'] = 0  # 0 = pas de signal, 1 = achat, -1 = vente
            
            # Signal d'achat: %K et %D sont tous deux sous le niveau de survente et %K croise %D vers le haut
            df['k_crosses_d_up'] = (df['k'] > df['d']) & (df['k'].shift(1) <= df['d'].shift(1))
            df.loc[(df['k'] < oversold) & (df['d'] < oversold) & df['k_crosses_d_up'], 'signal'] = 1
            
            # Signal de vente: %K et %D sont tous deux au-dessus du niveau de surachat et %K croise %D vers le bas
            df['k_crosses_d_down'] = (df['k'] < df['d']) & (df['k'].shift(1) >= df['d'].shift(1))
            df.loc[(df['k'] > overbought) & (df['d'] > overbought) & df['k_crosses_d_down'], 'signal'] = -1
            
            # Récupérer le dernier signal (sur les 3 dernières périodes pour tenir compte du décalage)
            recent_signals = df.iloc[-3:]['signal'].to_list()
            signal_type = None
            
            if 1 in recent_signals:
                signal_type = 'BUY'
            elif -1 in recent_signals:
                signal_type = 'SELL'
            
            # Récupérer la dernière ligne
            last_row = df.iloc[-1]
            
            # Retourner les informations
            result = {
                'pair': pair_symbol,
                'k_value': float(last_row['k']) if not pd.isna(last_row['k']) else None,
                'd_value': float(last_row['d']) if not pd.isna(last_row['d']) else None,
                'oversold_level': oversold,
                'overbought_level': overbought,
                'signal_type': signal_type if signal_type else 'HOLD',
                'entry_price': float(last_row['close']),
            }
            
            # Si un signal a été généré
            if signal_type:
                # Récupérer ou créer la stratégie
                strategy, _ = Strategy.objects.get_or_create(
                    name=f"Stochastic ({k_period}/{d_period}/{slowing})",
                    defaults={'description': f"Stochastic Oscillator strategy with K period {k_period}, D period {d_period}, and slowing {slowing}"}
                )
                
                pair = CurrencyPair.objects.get(symbol=pair_symbol)
                
                # Calculer les niveaux de stop loss et take profit basés sur l'ATR
                atr = TechnicalIndicators.calculate_atr(
                    df['high'], df['low'], df['close'], period=14
                ).iloc[-1]
                
                if signal_type == 'BUY':
                    stop_loss = last_row['close'] - (atr * 2)
                    take_profit = last_row['close'] + (atr * 3)
                else:  # SELL
                    stop_loss = last_row['close'] + (atr * 2)
                    take_profit = last_row['close'] - (atr * 3)
                
                # Calculer la confiance
                if signal_type == 'BUY':
                    # Plus les valeurs %K et %D sont basses, plus la confiance est élevée
                    k_distance = max(0, oversold - last_row['k']) / oversold
                    d_distance = max(0, oversold - last_row['d']) / oversold
                    confidence = min(0.9, max(0.6, (k_distance + d_distance) / 2 + 0.6))
                else:  # SELL
                    # Plus les valeurs %K et %D sont élevées, plus la confiance est élevée
                    k_distance = max(0, last_row['k'] - overbought) / (100 - overbought)
                    d_distance = max(0, last_row['d'] - overbought) / (100 - overbought)
                    confidence = min(0.9, max(0.6, (k_distance + d_distance) / 2 + 0.6))
                
                # Créer le signal
                signal = Signal.objects.create(
                    pair=pair,
                    strategy=strategy,
                    signal_type=signal_type,
                    timeframe='1h',
                    entry_price=last_row['close'],
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    confidence=confidence,
                    timestamp=timezone.now(),
                    expiration=timezone.now() + timedelta(days=1),
                    notes=f"Signal generated by Stochastic Oscillator strategy with %K={last_row['k']:.2f} and %D={last_row['d']:.2f}"
                )
                
                # Ajouter les informations du signal au résultat
                result.update({
                    'signal_id': signal.id,
                    'stop_loss': float(stop_loss),
                    'take_profit': float(take_profit),
                    'confidence': confidence,
                    'timestamp': signal.timestamp
                })
            
            return result
            
        except Exception as e:
            print(f"Error generating Stochastic signals: {str(e)}")
            return None