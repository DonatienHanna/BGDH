from django.core.management.base import BaseCommand
from market_data.models import Currency, CurrencyPair
from market_data.tasks import update_forex_data_task

class Command(BaseCommand):
    help = 'Initialize market data with common forex pairs'
    
    def handle(self, *args, **options):
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
            self.stdout.write(self.style.SUCCESS(f'Currency {code} created or already exists'))
        
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
            
            pair, created = CurrencyPair.objects.get_or_create(
                symbol=symbol,
                defaults={
                    'base_currency': base_currency,
                    'quote_currency': quote_currency,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Currency pair {symbol} created'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Currency pair {symbol} already exists'))
        
        # Initialiser les données historiques pour XAU/USD
        self.stdout.write(self.style.WARNING('Fetching historical data for XAUUSD...'))
        result = update_forex_data_task('XAUUSD', '1h')
        
        if result.get('XAUUSD') == 'Success':
            self.stdout.write(self.style.SUCCESS('Successfully fetched XAUUSD historical data'))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch XAUUSD historical data'))