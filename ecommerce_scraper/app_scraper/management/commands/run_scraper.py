import asyncio
import aiohttp
from django.core.management.base import BaseCommand
from app_scraper.services import VIPScraper, StoreService
from asgiref.sync import sync_to_async
#from scraper.models import ProductScrap

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando captura de dados..."))
        
        # Configuração das lojas conforme solicitado no teste
        
        #STORES = [
        #    {"name": "", "domain_key": "", "organization_id": "", "subsidiary_id": "", "distribution_center_id": "", "store_token": ""},
        #]

        async def run_all():
            sem = asyncio.Semaphore(5)
            tasks = []
            STORES = await sync_to_async(list)(StoreService.list_stores())
            for store in STORES:
                scraper = VIPScraper(store_config=store)
                tasks.append(self.process_store(sem, scraper, store))
            await asyncio.gather(*tasks)

        
        asyncio.run(run_all())
        self.stdout.write(self.style.SUCCESS('Processo finalizado com sucesso!'))

    async def process_store(self, sem, scraper, store):
        # Lógica para chamar o fetch_categories e fetch_products 
        # e salvar no banco usando sync_to_async do Django ou loop.run_in_executor
        async with sem:
            async with aiohttp.ClientSession() as session:
                self.stdout.write(f"Iniciando {scraper.store_name}...")

                try:
                    categories = await scraper.fetch_categories(session, store)
                    #products = await scraper.fetch_products(session)
                    #print(categories)
                    #print(products)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erro em {scraper.store_name}: {str(e)}"))