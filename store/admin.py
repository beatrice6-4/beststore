from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import Product, Variation, ReviewRating, ProductGallery
import admin_thumbnails

# ========================= PRODUCT GALLERY INLINE =========================
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    fields = ('image_thumbnail', 'image')
    readonly_fields = ('image_thumbnail',)


# ========================= PRODUCT ADMIN =========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Beautiful Product Admin Interface"""
    
    list_display = (
        'colored_product_name',
        'slug',
        'colored_price',
        'colored_stock',
        'colored_availability',
        'category',
        'rating_display',
        'created_at'
    )
    
    list_filter = (
        'is_available',
        'category',
        'created_at',
        'modified_at',
    )
    
    search_fields = (
        'product_name',
        'slug',
        'category__category_name',
        'description',
    )
    
    prepopulated_fields = {'slug': ('product_name',)}
    
    readonly_fields = (
        'created_at',
        'modified_at',
        'product_preview',
        'rating_badge',
    )
    
    fieldsets = (
        ('📦 Product Information', {
            'fields': ('product_name', 'slug', 'category', 'image', 'product_preview'),
            'classes': ('wide',),
            'description': 'Basic product details and identification'
        }),
        ('💰 Pricing & Stock', {
            'fields': ('price', 'stock'),
            'classes': ('wide',),
        }),
        ('📝 Description', {
            'fields': ('description',),
            'classes': ('wide', 'collapse'),
        }),
        ('⭐ Ratings & Status', {
            'fields': ('is_available', 'rating_badge'),
            'classes': ('wide',),
        }),
        ('📅 Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse', 'grp-collapse'),
            'description': 'Auto-generated timestamps'
        }),
    )
    
    inlines = [ProductGalleryInline]
    
    ordering = ('-created_at',)
    
    date_hierarchy = 'created_at'
    
    actions = ['make_available', 'make_unavailable', 'increase_stock', 'decrease_stock']
    
    class Media:
        css = {
            'all': ('admin/css/product_admin.css',)
        }
    
    # ============ DISPLAY METHODS ============
    def colored_product_name(self, obj):
        """Display product name with color and icon"""
        return format_html(
            '<span style="color: #667eea; font-weight: 600;"><i class="fas fa-box"></i> {}</span>',
            obj.product_name
        )
    colored_product_name.short_description = 'Product Name'
    
    def colored_price(self, obj):
        """Display price with currency symbol and color"""
        return format_html(
            '<span style="color: #28a745; font-weight: 600; font-size: 14px;">Ksh {}</span>',
            f'{obj.price:,.2f}'
        )
    colored_price.short_description = '💰 Price'
    
    def colored_stock(self, obj):
        """Display stock with color coding"""
        if obj.stock > 50:
            color = '#28a745'
            status = '✓ High'
        elif obj.stock > 10:
            color = '#ffc107'
            status = '⚠ Medium'
        else:
            color = '#dc3545'
            status = '✗ Low'
        
        return format_html(
            '<span style="color: {}; font-weight: 600;">{} ({})</span>',
            color, obj.stock, status
        )
    colored_stock.short_description = '📦 Stock'
    
    def colored_availability(self, obj):
        """Display availability status with icon"""
        if obj.is_available:
            return format_html(
                '<span style="color: #28a745; font-weight: 600;"><i class="fas fa-check-circle"></i> Available</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: 600;"><i class="fas fa-times-circle"></i> Unavailable</span>'
            )
    colored_availability.short_description = '✓ Status'
    
    def rating_display(self, obj):
        """Display product rating with stars"""
        if hasattr(obj, 'averageReview'):
            rating = obj.averageReview or 0
            return format_html(
                '<span style="color: #ffc107;">{"⭐" * int(rating)} {:.1f}/5.0</span>',
                rating
            )
        return format_html('<span style="color: #adb5bd;">No ratings</span>')
    rating_display.short_description = '⭐ Rating'
    
    def product_preview(self, obj):
        """Display product image preview"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "No image"
    product_preview.short_description = '🖼️ Product Preview'
    
    def rating_badge(self, obj):
        """Display rating as a badge"""
        if hasattr(obj, 'averageReview'):
            rating = obj.averageReview or 0
            return format_html(
                '<span style="background: #ffc107; color: #fff; padding: 8px 16px; border-radius: 20px; font-weight: 600;"> ⭐ {:.1f}/5.0</span>',
                rating
            )
        return format_html('<span style="color: #adb5bd;">No ratings yet</span>')
    rating_badge.short_description = 'Rating Badge'
    
    # ============ ACTIONS ============
    def make_available(self, request, queryset):
        """Mark products as available"""
        count = queryset.update(is_available=True)
        self.message_user(request, f'✓ {count} product(s) marked as available.')
    make_available.short_description = '✓ Mark selected products as available'
    
    def make_unavailable(self, request, queryset):
        """Mark products as unavailable"""
        count = queryset.update(is_available=False)
        self.message_user(request, f'✗ {count} product(s) marked as unavailable.')
    make_unavailable.short_description = '✗ Mark selected products as unavailable'
    
    def increase_stock(self, request, queryset):
        """Increase stock by 10 units"""
        count = queryset.count()
        for product in queryset:
            product.stock += 10
            product.save()
        self.message_user(request, f'✓ Stock increased for {count} product(s).')
    increase_stock.short_description = '📈 Increase stock by 10 units'
    
    def decrease_stock(self, request, queryset):
        """Decrease stock by 5 units"""
        count = queryset.count()
        for product in queryset:
            if product.stock >= 5:
                product.stock -= 5
                product.save()
        self.message_user(request, f'📉 Stock decreased for {count} product(s).')
    decrease_stock.short_description = '📉 Decrease stock by 5 units'

# ========================= VARIATION ADMIN (CORRECTED) =========================
@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    """Beautiful Variation Admin Interface"""
    
    list_display = (
        'colored_product',
        'colored_category',
        'colored_value',
        'colored_status',
        'created_badge'
    )
    
    list_filter = (
        'product',
        'variation_category',
        'is_active',
    )
    
    search_fields = (
        'product__product_name',
        'variation_value',
        'variation_category',
    )
    
    readonly_fields = (
        # Remove 'updated_date' if it doesn't exist
        # Only include fields that actually exist in your model
    )
    
    fieldsets = (
        ('📦 Product', {
            'fields': ('product',),
            'classes': ('wide',),
        }),
        ('🎨 Variation Details', {
            'fields': ('variation_category', 'variation_value', 'is_active'),
            'classes': ('wide',),
            'description': 'Configure variation type, value, and status'
        }),
    )
    
    ordering = ('product', 'variation_category')
    
    actions = ['mark_active', 'mark_inactive']
    
    class Media:
        css = {
            'all': ('admin/css/variation_admin.css',)
        }
    
    # ============ DISPLAY METHODS ============
    def colored_product(self, obj):
        """Display product with icon"""
        return format_html(
            '<span style="color: #667eea; font-weight: 600;"><i class="fas fa-box"></i> {}</span>',
            obj.product.product_name
        )
    colored_product.short_description = '📦 Product'
    
    def colored_category(self, obj):
        """Display variation category with color"""
        category_colors = {
            'color': '#ff6b6b',
            'size': '#4ecdc4',
            'material': '#45b7d1',
            'brand': '#96ceb4',
        }
        color = category_colors.get(obj.variation_category.lower(), '#667eea')
        return format_html(
            '<span style="background: {}; color: #fff; padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 12px;">{}</span>',
            color, obj.variation_category
        )
    colored_category.short_description = '🎨 Category'
    
    def colored_value(self, obj):
        """Display variation value"""
        return format_html(
            '<span style="color: #2c3e50; font-weight: 600;">{}</span>',
            obj.variation_value
        )
    colored_value.short_description = '✏️ Value'
    
    def colored_status(self, obj):
        """Display active/inactive status with icon"""
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745; font-weight: 600;"><i class="fas fa-check-circle"></i> Active</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: 600;"><i class="fas fa-times-circle"></i> Inactive</span>'
            )
    colored_status.short_description = '✓ Status'
    
    def created_badge(self, obj):
        """Display created date as badge"""
        # Check if your model has 'created_date', 'date_created', or similar
        # Adjust based on your actual model field
        if hasattr(obj, 'created_date'):
            date_str = obj.created_date.strftime('%d %b %Y')
        elif hasattr(obj, 'date_created'):
            date_str = obj.date_created.strftime('%d %b %Y')
        else:
            date_str = 'N/A'
        
        return format_html(
            '<span style="background: #e7f3ff; color: #004085; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            date_str
        )
    created_badge.short_description = '📅 Created'
    
    # ============ ACTIONS ============
    def mark_active(self, request, queryset):
        """Mark variations as active"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'✓ {count} variation(s) activated.')
    mark_active.short_description = '✓ Activate selected variations'
    
    def mark_inactive(self, request, queryset):
        """Mark variations as inactive"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'✗ {count} variation(s) deactivated.')
    mark_inactive.short_description = '✗ Deactivate selected variations'


# ========================= REVIEW RATING ADMIN (CORRECTED) =========================
@admin.register(ReviewRating)
class ReviewRatingAdmin(admin.ModelAdmin):
    """Beautiful Review & Rating Admin Interface"""
    
    list_display = (
        'colored_product',
        'colored_user',
        'rating_stars',
        'colored_status',
        'review_preview',
        'created_date_badge'
    )
    
    list_filter = (
        'rating',
        'product',
    )
    
    search_fields = (
        'product__product_name',
        'user__username',
        'review_text',
    )
    
    readonly_fields = (
        'product',
        'user',
        'review_display',
    )
    
    fieldsets = (
        ('📦 Product & User', {
            'fields': ('product', 'user'),
            'classes': ('wide',),
        }),
        ('⭐ Review Details', {
            'fields': ('rating', 'review_display'),
            'classes': ('wide',),
        }),
    )
    
    ordering = ('-id',)  # Order by ID in descending order if no date field exists
    
    class Media:
        css = {
            'all': ('admin/css/review_admin.css',)
        }
    
    # ============ DISPLAY METHODS ============
    def colored_product(self, obj):
        """Display product"""
        return format_html(
            '<span style="color: #667eea; font-weight: 600;"><i class="fas fa-box"></i> {}</span>',
            obj.product.product_name
        )
    colored_product.short_description = '📦 Product'
    
    def colored_user(self, obj):
        """Display user with icon"""
        return format_html(
            '<span style="color: #764ba2; font-weight: 600;"><i class="fas fa-user-circle"></i> {}</span>',
            obj.user.username
        )
    colored_user.short_description = '👤 User'
    
    def rating_stars(self, obj):
        """Display rating as stars"""
        stars = '⭐' * int(obj.rating) + '☆' * (5 - int(obj.rating))
        return format_html(
            '<span style="color: #ffc107; font-size: 16px;">{}</span>',
            stars
        )
    rating_stars.short_description = '⭐ Rating'
    
    def colored_status(self, obj):
        """Display status badge"""
        return format_html(
            '<span style="background: #d4edda; color: #155724; padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 12px;">✓ Published</span>'
        )
    colored_status.short_description = '✓ Status'
    
    def review_preview(self, obj):
        """Display preview of review text"""
        preview = obj.review_text[:50] + '...' if len(obj.review_text) > 50 else obj.review_text
        return format_html(
            '<span style="color: #6c757d; font-style: italic;">"{}"</span>',
            preview
        )
    review_preview.short_description = '💬 Review Preview'
    
    def created_date_badge(self, obj):
        """Display created date"""
        # Adjust field name based on your actual model
        if hasattr(obj, 'created_date'):
            date_str = obj.created_date.strftime('%d %b %Y')
        elif hasattr(obj, 'date_created'):
            date_str = obj.date_created.strftime('%d %b %Y')
        else:
            date_str = 'N/A'
        
        return format_html(
            '<span style="background: #e7f3ff; color: #004085; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            date_str
        )
    created_date_badge.short_description = '📅 Date'
    
    def review_display(self, obj):
        """Display full review text"""
        return format_html(
            '<div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #667eea;"><p style="margin: 0; color: #2c3e50; line-height: 1.6;">{}</p></div>',
            obj.review_text
        )
    review_display.short_description = '📝 Full Review'