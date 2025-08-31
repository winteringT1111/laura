from django.db import models
from django.conf import settings
from store import models as itemModels
# Create your models here.

class Characters(models.Model):
    charID = models.AutoField(primary_key=True)  
    charName = models.TextField()  
    charEngName= models.TextField()
    charFirstName = models.TextField()
    charCatchPhrase = models.TextField() 
    charPhrase = models.TextField()
    charImageB = models.TextField()  
    charImageA = models.TextField()
    charImageP = models.TextField() 
    charImageU = models.TextField()
    charCommission = models.BooleanField()
    charCommissionInfo = models.TextField(null=True) 
    charImageInfo = models.TextField(null=True)  
    charAge = models.IntegerField()
    charGrade = models.IntegerField()
    charSex = models.TextField()
    charHeight = models.IntegerField()
    charWeight = models.IntegerField()
    charBlood = models.TextField()
    charHouse = models.TextField() 
    charNationality = models.TextField()
    charKeyword1 = models.TextField()
    charKeyword2 = models.TextField()
    charKeyword3 = models.TextField()
    charPersonality = models.TextField() 
    charEtc = models.TextField()
    charWand1 = models.TextField()
    charWand2 = models.TextField()
    charWand3 = models.TextField()
    charWand4 = models.TextField()
    charWandInfo = models.TextField(null=True)
    charProfileMusic = models.TextField(null=True)
    
    class Meta:
        db_table = "character"
        
        

class Purchase(models.Model):
    purchaseID = models.AutoField(primary_key=True)  
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    itemInfo = models.ForeignKey(itemModels.Item, on_delete=models.CASCADE)
    itemCount = models.IntegerField()
    orderDate = models.DateField(null=True)

    class Meta:
        db_table = "purchase"
        
        
        
class Gift(models.Model):
    giftID = models.AutoField(primary_key=True)  
    giver_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gifts_given'  # Custom related name for the giver
    )
    receiver_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gifts_received'  # Custom related name for the receiver
    )
    itemInfo = models.ForeignKey(itemModels.Item, on_delete=models.CASCADE)
    anonymous = models.BooleanField()
    message = models.TextField(null=True)
    itemCount = models.IntegerField()
    orderDate = models.DateField(null=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        db_table = "gift"
     
        
class MagicGift(models.Model):
    giftID = models.AutoField(primary_key=True)  
    giver_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gifts_given2'  # Custom related name for the giver
    )
    receiver_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gifts_received2'  # Custom related name for the receiver
    )
    itemInfo = models.ForeignKey(itemModels.Item_magic, on_delete=models.CASCADE)
    anonymous = models.BooleanField()
    message = models.TextField(null=True)
    itemCount = models.IntegerField()
    orderDate = models.DateField(null=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        db_table = "magicgift"
        
        
class GachaGift(models.Model):
    giftID = models.AutoField(primary_key=True)  
    giver_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gifts_given3'  # Custom related name for the giver
    )
    receiver_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gifts_received3'  # Custom related name for the receiver
    )
    itemInfo = models.ForeignKey(itemModels.Gacha, on_delete=models.CASCADE)
    anonymous = models.BooleanField()
    message = models.TextField(null=True)
    itemCount = models.IntegerField()
    orderDate = models.DateField(null=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        db_table = "gachagift"
   
        
class Inventory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    itemInfo = models.ForeignKey(itemModels.Item, on_delete=models.CASCADE)
    itemCount = models.IntegerField()

    class Meta:
        db_table = "inventory"
        
        
class Inventory_magic(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    itemInfo = models.ForeignKey(itemModels.Item_magic, on_delete=models.CASCADE)
    itemCount = models.IntegerField()

    class Meta:
        db_table = "inventory_magic"
          
          
class Inventory_potion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    itemInfo = models.ForeignKey(itemModels.Potion, on_delete=models.CASCADE)
    itemCount = models.IntegerField()

    class Meta:
        db_table = "inventory_potion"
        
          
class Inventory_gacha(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    itemInfo = models.ForeignKey(itemModels.Gacha, on_delete=models.CASCADE)
    itemCount = models.IntegerField()

    class Meta:
        db_table = "inventory_gacha"
        
class Inventory_ring(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owner'  # Custom related name for the giver
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user2'  # Custom related name for the receiver
    )
    itemInfo = models.ForeignKey(itemModels.Item, on_delete=models.CASCADE)
    itemCount = models.IntegerField()

    class Meta:
        db_table = "inventory_ring"
          
          
          
class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_attendance = models.IntegerField(default=0)  # 누적 출석 수
    attendance_date = models.DateField(null=True, blank=True) 
    broom_item_received = models.BooleanField(default=False)  # 빗자루 아이템 수령 여부

    def __str__(self):
        return f"{self.user.username} - {self.total_attendance}일 출석"