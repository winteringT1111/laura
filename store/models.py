from django.db import models
from django.conf import settings

# Create your models here.

class Item(models.Model):
    itemID = models.AutoField(primary_key=True)  
    itemName = models.TextField()
    itemCategory= models.TextField()
    itemInfo = models.TextField()
    itemPrice = models.IntegerField()

    class Meta:
        db_table = "items"
        

class Ingredient(models.Model):
    itemID = models.AutoField(primary_key=True)  
    itemName = models.TextField()
    itemCategory= models.TextField()
    itemInfo = models.TextField()
    itemPrice = models.IntegerField()
    itemShow = models.BooleanField()

    class Meta:
        db_table = "ingredients"
        
        
class Recipe(models.Model):
    itemID = models.AutoField(primary_key=True)  
    itemName = models.TextField()
    itemCategory= models.TextField()
    itemInfo = models.TextField()
    recipe = models.TextField()
    discovered = models.BooleanField()
    discoverer = models.TextField(null=True)
    
    class Meta:
        db_table = "Recipe"
        
        
class Cookie(models.Model):
    itemID = models.AutoField(primary_key=True)  
    itemInfo = models.TextField()
    
    
class Scroll(models.Model):
    itemID = models.AutoField(primary_key=True)  
    itemInfo = models.TextField()
