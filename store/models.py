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
        

class Item_magic(models.Model):
    itemID = models.AutoField(primary_key=True)  
    itemName = models.TextField()
    itemInfo = models.TextField()
    itemDegree = models.IntegerField()
    itemCategory = models.TextField()
    itemCategory2 = models.TextField()

    class Meta:
        db_table = "items_magic"
        
        
class Potion(models.Model):
    itemID = models.AutoField(primary_key=True)  
    itemName = models.TextField()
    itemInfo = models.TextField()
    potionRecipe = models.TextField()
    degree = models.IntegerField()
    price = models.IntegerField()
    discovered = models.BooleanField()
    discoverer = models.TextField(null=True)
    itemCategory= models.TextField(default="마법 약")
    
    class Meta:
        db_table = "potion"
        
        
class Cookie(models.Model):
    itemID = models.AutoField(primary_key=True)  
    itemInfo = models.TextField()
    
    
class Scroll(models.Model):
    itemID = models.AutoField(primary_key=True)  
    itemInfo = models.TextField()
    
class Gacha(models.Model):
    itemID = models.AutoField(primary_key=True)  
    itemName = models.TextField()
    itemImage = models.TextField()
    itemCategory = models.TextField()
    itemInfo = models.TextField()
    
    
class House(models.Model):
    grinffindor = models.IntegerField(default=0)
    hufflepuff = models.IntegerField(default=0)
    ravenclaw = models.IntegerField(default=0)
    slyderin = models.IntegerField(default=0)
    
    class Meta:
        db_table = "House"
    
    
class PotionStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    xp = models.IntegerField(default=0) 
    degree = models.IntegerField(default=3) 

    class Meta:
        db_table = "PotionStatus"
    