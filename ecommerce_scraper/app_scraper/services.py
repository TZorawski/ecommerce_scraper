import aiohttp
import logging
from typing import Dict
from decimal import Decimal
from django.utils import timezone
import os
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from .models import Store, Category, Subcategory, Product

load_dotenv()
logger = logging.getLogger(__name__)

class StoreService:
    @staticmethod
    def list_stores() -> Store:
        return Store.objects.all()
    
class CategoryService:
    @staticmethod
    @sync_to_async
    def save_category(category_data) -> Category:
        store = Store.objects.get(id=category_data['store'])
        category, created = Category.objects.update_or_create(
            vip_id = category_data['vip_id'],
            store = store,
            defaults = {
                'name': category_data['name'],
                'link': category_data['link']
            }
        )
        return category

class SubcategoryService:
    @staticmethod
    @sync_to_async
    def save_subcategory(subcategory_data) -> Subcategory:
        category = Category.objects.get(id=subcategory_data['category'])
        subcategory, created = Subcategory.objects.update_or_create(
            vip_id = subcategory_data['vip_id'],
            category = category,
            defaults={
                'name': subcategory_data['name'],
                'link': subcategory_data['link']
            }
        )
        return subcategory

class ProductService:
    @staticmethod
    @sync_to_async
    def save_product(store_id, subcategory_id, prod_data) -> Product:
        regular_price = Decimal(str(prod_data['regular_price']))
        offer_price = Decimal(str(prod_data['offer_price'])) if prod_data.get('offer_price') else None

        product, created = Product.objects.update_or_create(
            vip_id = prod_data['id'],
            category = subcategory_id,
            defaults={
                'name': prod_data['name'],
                'ean': prod_data.get('ean', ''),
                'regular_price': regular_price,
                'is_offer': prod_data.get('is_offer', False),
                'offer_price': offer_price,
                'check_date': timezone.now(),
                'store': store_id,
                'subcategory': subcategory_id
            }
        )
        return product
    
    @staticmethod
    @sync_to_async
    def save_product_list(store_id, subcategory_id, prod_list):
        subcategory = Subcategory.objects.get(id=subcategory_id)
        store = Store.objects.get(id=store_id)

        objs = [
            Product(
                vip_id = item['vip_id'],
                name = item['name'],
                ean = item.get('ean', ''),
                regular_price = Decimal(str(item['regular_price'])),
                is_offer = item.get('is_offer', False),
                offer_price = Decimal(str(item['offer_price'])) if item.get('offer_price') else None,
                check_date = timezone.now(),
                store = store,
                subcategory = subcategory
            )
            for item in prod_list
        ]
        Product.objects.bulk_create(objs, ignore_conflicts=True)

class VIPScraper:
    vip_backend_url = os.getenv('VIP_BACKEND_URL')
    
    def __init__(self, store_config: Store):
        self.store_id = store_config.id
        self.store_name = store_config.name
        self.domain_key = store_config.domain_key
        self.organization_id = store_config.organization_id
        self.subsidiary_id = store_config.subsidiary_id
        self.distribution_center_id = store_config.distribution_center_id
        self.store_token = store_config.store_token

        self.store_base_url = VIPScraper.vip_backend_url + str(self.organization_id) + "/filial/" + self.subsidiary_id + "/centro_distribuicao/" + self.distribution_center_id + "/loja/classificacoes_mercadologicas/departamentos/"
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Authorization":  f'Bearer {self.store_token}',
            "organizationid": self.organization_id,
            "domainkey": self.domain_key,
        }

    async def fetch_categories(self, session: aiohttp.ClientSession, store_id) -> Dict:
        url = self.store_base_url + "arvore"
        async with session.get(url, headers=self.headers) as resp:
            data = await resp.json()
            
            categories = []
            for cat in data["data"]:
                category = {"name": cat["descricao"], "vip_id": cat["classificacao_mercadologica_id"], "link": cat["link"], "store": store_id}
                category_stored = await CategoryService.save_category(category_data=category)
                subcategories = []
                for sub in cat['children']:
                    subcategory = {"name": sub["descricao"], "vip_id": sub["classificacao_mercadologica_id"], "link": sub["link"], "category": category_stored.id}
                    subcategory_stored = await SubcategoryService.save_subcategory(subcategory_data=subcategory)
                    subcategory['id'] = subcategory_stored.id
                    subcategories.append(subcategory)
                category['subcategories'] = subcategories
                categories.append(category)

            return categories
            

    async def fetch_products(self, session: aiohttp.ClientSession, category_vip_id, subcategory_vip_id):
        page = 1
        all_products = []
        
        while True:
            url = self.store_base_url + str(category_vip_id) + "/produtos?page=" + str(page) + "&secao=" + str(subcategory_vip_id)
            async with session.get(url, headers=self.headers) as resp:
                if resp.status != 200:
                    break
                
                data = await resp.json()
                products = data.get('data', [])
                
                if not products:
                    break
                
                for p in products:
                    if p.get('disponivel', False):
                        all_products.append({
                            "vip_id": p['produto_id'],
                            "name": p['descricao'],
                            "ean": p.get('codigo_barras'),
                            "regular_price": p['preco'],
                            "is_offer": p['em_oferta'],
                            "offer_price": p.get('oferta', {}).get('preco_oferta', 0) if p['em_oferta'] else 0,
                        })
                page += 1

        return all_products