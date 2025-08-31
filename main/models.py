from django.db import models
from django.conf import settings


# Create your models here.
class Comment(models.Model):
    category = models.CharField(max_length=20)  
    content = models.TextField()
    itemName = models.ImageField(null=True, blank=True)

    class Meta:
        db_table = "comment"
        
class Article(models.Model):
    title = models.CharField(max_length=20)  
    content = models.TextField()
    image = models.ImageField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True) 
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "article"
