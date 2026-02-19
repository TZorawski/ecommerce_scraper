import asyncio
import aiohttp
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class VIPScraper:
    vip_backend_url = ""
    
    def __init__(self, store_config: Dict):
        self.store_name = store_config['name']
        self.domain_key = store_config['domain_key']
        self.organization_id = store_config['organization_id']
        self.subsidiary_id = store_config['subsidiary_id']
        self.distribution_center_id = store_config['distribution_center_id']
        self.store_token = store_config['store_token']

        self.store_base_url = VIPScraper.vip_backend_url + str(self.organization_id) + "/filial/" + self.subsidiary_id + "/centro_distribuicao/" + self.distribution_center_id + "/loja/classificacoes_mercadologicas/departamentos/"
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Authorization":  f'Bearer {self.store_token}',
            "organizationid": self.organization_id,
            "domainkey": self.domain_key,
        }

    async def fetch_categories(self, session: aiohttp.ClientSession) -> Dict:
        url = self.store_base_url + "arvore"
        async with session.get(url, headers=self.headers) as resp:
            data = await resp.json()
            print("===================================")
            
            # Lógica para extrair slugs de categorias nível 2
            categories = []
            for cat in data['data']:
                category = {'name': cat['descricao'], 'subcategories': []}
                subcategories = []
                for sub in cat['children']:
                    subcategories.append(sub['descricao'])
                category['subcategories'] = subcategories
                categories.append(category)
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