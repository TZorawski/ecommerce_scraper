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
        category, created = Category.objects.update_or_create(
            vip_id = category_data['vip_id'],
            store = category_data['store'],
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
        subcategory, created = Subcategory.objects.update_or_create(
            vip_id = subcategory_data['vip_id'],
            category = subcategory_data['category'],
            defaults={
                'name': subcategory_data['name'],
                'link': subcategory_data['link']
            }
        )
        return subcategory

class ProductService:
    @staticmethod
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

    async def fetch_categories(self, session: aiohttp.ClientSession, store: Store) -> Dict:
        url = self.store_base_url + "arvore"
        async with session.get(url, headers=self.headers) as resp:
            data = await resp.json()
            print("===================================")
            
            # Lógica para extrair slugs de categorias nível 2
            categories = []
            for cat in data["data"]:
                print('cat ' + cat["descricao"])
                category = {"name": cat["descricao"], "vip_id": cat["classificacao_mercadologica_id"], "link": cat["link"], "store": store}
                category_stored = await CategoryService.save_category(category_data=category)
                subcategories = []
                for sub in cat['children']:
                    print('sub ' + sub["descricao"])
                    subcategory = {"name": sub["descricao"], "vip_id": sub["classificacao_mercadologica_id"], "link": sub["link"], "category": category_stored}
                    subcategory_stored = await SubcategoryService.save_subcategory(subcategory_data=subcategory)
                    subcategories.append(subcategory_stored)
                category['subcategories'] = subcategories
                categories.append(category)
            print("finish categorieeeeeeeeeeeeesssssssss")
            return categories
            

    async def fetch_products(self, session: aiohttp.ClientSession):
        # category_slug: str
        page = 1
        all_products = []
        category_id = 3
        subcategory_id = 22
        
        #while True:
        #params = {
        #    "categorySlug": category_slug,
        #    "page": page,
        #    "limit": 50
        #}

        url = self.store_base_url + str(category_id) + "/produtos?page=" + str(page) + "&secao=" + str(subcategory_id)
        async with session.get(url, headers=self.headers) as resp:
            #if resp.status != 200:
            #    break
            
            data = await resp.json()
            print("===================================")
            products = data.get('data', [])
            
            #if not products:
            #    break
            
            for p in products:
                if p.get('disponivel', False):
                    all_products.append({
                        "product_code": p['produto_id'],
                        "name": p['descricao'],
                        "ean": p.get('codigo_barras'),
                        "regular_price": p['preco'],
                        "is_offer": p['em_oferta'],
                        "offer_price": p.get('oferta', {}).get('preco_oferta', 0) if p['em_oferta'] else 0,
                        "check_date": 'hoje',
                        "category": p['secao_id'],
                        "store_name": self.store_name
                    })
            page += 1
        return all_products