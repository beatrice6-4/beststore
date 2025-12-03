from django.db import models
from django.urls import reverse
from category.models import Category
from django.db.models import Avg, Count


class Product(models.Model):
    """Model representing a product."""
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def get_url(self):
        """Generate the URL for the product detail page."""
        return reverse('store:product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name


class ProductGallery(models.Model):
    """Model representing a product gallery."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.product.product_name} Gallery Image"


class VariationManager(models.Manager):
    """Manager for handling product variations."""
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


VARIATION_CATEGORY_CHOICES = (
    ('color', 'Color'),
    ('size', 'Size'),
)


class Variation(models.Model):
    """Model representing product variations (e.g., color, size)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_category = models.CharField(max_length=100, choices=VARIATION_CATEGORY_CHOICES)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return f"{self.variation_category}: {self.variation_value}"


class ReviewRating(models.Model):
    """Model representing product reviews and ratings."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)  # Use string-based lazy import
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.GenericIPAddressField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

    def average_review(self):
        """Calculate the average rating for the product."""
        reviews = ReviewRating.objects.filter(product=self.product, status=True).aggregate(average=Avg('rating'))
        return reviews['average'] or 0

    def count_review(self):
        """Count the number of reviews for the product."""
        reviews = ReviewRating.objects.filter(product=self.product, status=True).aggregate(count=Count('id'))
        return reviews['count'] or 0