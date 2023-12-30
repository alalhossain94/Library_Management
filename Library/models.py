from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# =====================================Category Model=========================================#
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

# =====================================Book Model=========================================#
class BookModel(models.Model):
    image = models.ImageField(upload_to='book/uploads/', blank=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    borrowing_price = models.CharField(max_length=15)
    category = models.ManyToManyField(Category)
     
    def __str__(self):
        return self.title