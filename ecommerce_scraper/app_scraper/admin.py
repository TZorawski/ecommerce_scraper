from django.contrib import admin
from .models import Store, Category, Subcategory, Product

admin.site.register(Store)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Product)
