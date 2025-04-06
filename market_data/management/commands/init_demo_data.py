from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from market_data.models import Currency, CurrencyPair
from signals.models import Strategy
from django.utils import timezone
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize demo data for testing'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Initializing demo data...'))
        
        # Créer un super utilisateur pour l'administration
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpassword'
            )
            self.stdout.write(self.style.SUCCESS('Admin user created'))
        
        # Créer un utilisateur normal
        if not User.objects.filter(username='trader').exists():
            trader_user = User.objects.create_user(
                username='trader',
                email='trader@example.com',
                password='traderpassword',
                is_premium=True,
                risk_profile='moderate'
            )
            self.stdout.write(self.style.SUCCESS('Trader user created'))
        
        # Créer les devises courantes
        currencies = [
            ('USD', 'US Dollar'),
            ('EUR', 'Euro'),
            ('GBP', 'British Pound'),
            ('JPY', 'Japanese Yen'),
            ('AUD', 'Australian Dollar'),
            ('CAD', 'Canadian Dollar'),
            ('CHF', 'Swiss Franc'),
            ('NZD', 'New Zealand Dollar'),
            ('XAU', 'Gold')
        ]
        
        for code, name in currencies:
            Currency.objects.get_or_create(code=code, defaults={'name': name})
            self.stdout.write(self.style.SUCCESS(f'Currency {code} created or updated'))
        
        # Créer les paires de devises courantes
        pairs = [
            ('EURUSD', 'EUR', 'USD'),
            ('GBPUSD', 'GBP', 'USD'),
            ('USDJPY', 'USD', 'JPY'),
            ('XAUUSD', 'XAU', 'USD'),  # Or/USD
            ('AUDUSD', 'AUD', 'USD'),
            ('USDCAD', 'USD', 'CAD'),
            ('USDCHF', 'USD', 'CHF'),
            ('NZDUSD', 'NZD', 'USD')
        ]
        
        for symbol, base_code, quote_code in pairs:
            base_currency = Currency.objects.get(code=base_code)
            quote_currency = Currency.objects.get(code=quote_code)
            
            CurrencyPair.objects.get_or_create(
                symbol=symbol,
                defaults={
                    'base_currency': base_currency,
                    'quote_currency': quote_currency,
                    'is_active': True
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Currency pair {symbol} created or updated'))
        
        # Créer les stratégies
        strategies = [
            ('Bollinger Bands (27/2.7)', 'Stratégie basée sur les Bandes de Bollinger avec une période de 27 et une déviation de 2.7'),
            ('Williams %R (75)', 'Stratégie basée sur Williams %R avec une période de 75'),
            ('Stochastic (40/20/15)', 'Stratégie basée sur l\'oscillateur stochastique avec des périodes K=40, D=20 et ralentissement=15'),
            ('Combined BB-Williams-Stoch', 'Stratégie combinée utilisant les Bandes de Bollinger, Williams %R et Stochastique')
        ]
        
        for name, description in strategies:
            Strategy.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'is_active': True
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Strategy {name} created or updated'))
        
        self.stdout.write(self.style.SUCCESS('Demo data initialization completed'))