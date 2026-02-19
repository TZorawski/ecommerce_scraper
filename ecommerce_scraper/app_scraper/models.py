from django.db import models

class Store(models.Model):
    name = models.CharField(max_length=255)
    domain_key = models.CharField(max_length=255)
    organization_id = models.CharField(max_length=255)
    subsidiary_id = models.CharField(max_length=255)
    distribution_center_id = models.CharField(max_length=255)
    store_token = models.CharField(max_length=500)

    def __str__(self):
        return self.name

class Category(models.Model):
    vip_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    link = models.URLField(max_length=500)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} ({self.store.name})"
    
class Subcategory(models.Model):
    vip_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    link = models.URLField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    class Meta:
        verbose_name_plural = "Subcategories"

    def __str__(self):
        return f"{self.name} < {self.category.name}"
    
class Product(models.Model):
    vip_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    ean = models.CharField(max_length=20, db_index=True)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_offer = models.BooleanField(default=False)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    check_date = models.DateTimeField()
    
    # Relacionamentos
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name