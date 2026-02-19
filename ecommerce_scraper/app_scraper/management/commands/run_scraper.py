import asyncio
import aiohttp
from django.core.management.base import BaseCommand
from app_scraper.services import VIPScraper
#from scraper.models import ProductScrap

class Command(BaseCommand):
    

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando captura de dados..."))
        
        # Configuração das lojas conforme solicitado no teste
        STORES = [
            
        ]

        async def run_all():
            tasks = []
            for store in STORES:
                scraper = VIPScraper(store)
                tasks.append(self.process_store(scraper))
            await asyncio.gather(*tasks)

        asyncio.run(run_all())
        self.stdout.write(self.style.SUCCESS('Processo finalizado com sucesso!'))

    async def process_store(self, scraper):
        # Lógica para chamar o fetch_categories e fetch_products 
        # e salvar no banco usando sync_to_async do Django ou loop.run_in_executor
        async with aiohttp.ClientSession() as session:
            self.stdout.write(f"Iniciando {scraper.store_name}...")

            try:
                #categories = await scraper.fetch_categories(session)
                products = await scraper.fetch_products(session)
                #print(categories)
                print(products)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro em {scraper.store_name}: {str(e)}"))