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




class Fish(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="물고기 이름")
    grade = models.PositiveIntegerField(choices=[(1, '1등급'), (2, '2등급'), (3, '3등급')], verbose_name="등급")
    score = models.PositiveIntegerField(default=0, verbose_name="점수")
    # icon = models.ImageField(upload_to='fish_icons/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.grade}등급)"
    

class Trash(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="쓰레기 이름")
    # icon = models.ImageField(upload_to='trash_icons/', blank=True, null=True)

    def __str__(self):
        return self.name
    
class FishingLog(models.Model):
    # 가정: 캐릭터 모델이 member 앱에 있습니다.
    author = models.ForeignKey('member.Characters', on_delete=models.CASCADE, related_name="fishing_logs")
    catch_description = models.CharField(max_length=200, verbose_name="낚시 결과 설명") # 예: "2M 연어를 낚았다!"
    action_description = models.TextField(blank=True, null=True, verbose_name="행동 지문")
    caught_at = models.DateTimeField(auto_now_add=True)
    
    # 낚은 아이템 정보 (선택적) - 어떤 종류든 연결 가능하도록 GenericForeignKey 사용 고려 가능
    # caught_item_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    # caught_item_id = models.PositiveIntegerField(null=True)
    # caught_item = GenericForeignKey('caught_item_type', 'caught_item_id')

    class Meta:
        ordering = ['-caught_at']


# 4. 로그 댓글 모델 (기존 LogComment 재사용 가능하면 생략)
class FishingComment(models.Model):
    log = models.ForeignKey(FishingLog, on_delete=models.CASCADE, related_name="comments")
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)