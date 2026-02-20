from django.contrib import admin
from .models import Store, Category, Subcategory, Product

admin.site.register(Store)
admin.site.register(Category)
admin.site.register(Subcategory)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "subcategory", "store", 
        "check_date", "regular_price", "offer_price", "is_offer"
    )
    list_filter = ("store", "check_date", "is_offer")
    search_fields = ("name", "ean")
    readonly_fields = ("check_date",)
