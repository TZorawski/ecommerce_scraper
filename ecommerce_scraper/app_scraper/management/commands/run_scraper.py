import asyncio
import aiohttp
from django.core.management.base import BaseCommand
from app_scraper.services import VIPScraper, StoreService, ProductService
from asgiref.sync import sync_to_async
#from scraper.models import ProductScrap

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando captura de dados..."))

        async def run_all():
            sem = asyncio.Semaphore(5)
            tasks = []
            STORES = await sync_to_async(list)(StoreService.list_stores())
            for store in STORES:
                scraper = VIPScraper(store_config=store)
                tasks.append(self.process_store(sem, scraper, store_id=store.id))
            await asyncio.gather(*tasks)

        
        asyncio.run(run_all())
        self.stdout.write(self.style.SUCCESS('Processo finalizado com sucesso!'))

    async def process_store(self, sem, scraper, store_id):
        async with sem:
            async with aiohttp.ClientSession() as session:
                self.stdout.write(f"Iniciando {scraper.store_name}...")

                try:
                    categories = await scraper.fetch_categories(session, store_id)
                    for category in categories:
                        for subcategory in category["subcategories"]:
                            products = []
                            category_vip_id = category["vip_id"]
                            subcategory_vip_id = subcategory["vip_id"]
                            products = await scraper.fetch_products(session, category_vip_id, subcategory_vip_id)
                            await ProductService.save_product_list(store_id, subcategory_id=subcategory["id"], prod_list=products)
                            #break
                        break

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erro em {scraper.store_name}: {str(e)}"))