from django.contrib import admin
from .models import Product, Category, ProductGallery, Variation, ReviewRating


class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


class VariationInline(admin.TabularInline):
    model = Variation
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'slug')
    prepopulated_fields = {'slug': ('category_name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'price', 'stock', 'category', 'is_available', 'created_at')
    list_filter = ('is_available', 'category', 'created_at')
    search_fields = ('product_name', 'description')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline, VariationInline]


@admin.register(ProductGallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'alt_text')
    list_filter = ('product',)


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'variation_category', 'variation_value', 'is_active')
    list_filter = ('variation_category', 'is_active', 'product')


@admin.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('product__product_name', 'user__username', 'subject')
    readonly_fields = ('created_at', 'updated_at', 'ip')