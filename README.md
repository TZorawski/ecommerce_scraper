# Scraper E-commerce

## Tecnologias utilizadas:
- Python (3.14)
- Django (6.0.2)
- PostgreSQL
- AIOHTTP

O AIOHTTP foi escolhido por ser mais leve e por apresentar melhor performance que o HTTPX.

## Instruções de instalação e execução
1. Clonar o repositório
>git clone https://github.com/TZorawski/ecommerce_scraper.git

>cd ecommerce_scraper

2. Criar ambiente virtual
>python -m venv venv

>source venv/bin/activate  # Linux/Mac

>venv\Scripts\activate     # Windows

3. Instalar dependências
>pip install -r requirements.txt

4. Na raíz do projeto crie um arquivo .env e coloque a variável VIP_BACKEND_URL, que é a url base para acesso à API

5. Execute o arquivo create_database.sql no seu PostgreSQL

6. Executar migrações
>python manage.py migrate

7. Rodar o servidor
>python manage.py runserver

8. Abra outro terminal e execute
>python manage.py run_scraper