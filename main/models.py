from django.db import models
from django.conf import settings
from store.models import Ingredient


# 1. 퀘스트와 보상 재료를 '수량'과 함께 연결하는 중간 모델
class QuestRewardItem(models.Model):
    quest = models.ForeignKey('Quest', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="수량")

class Quest(models.Model):
    title = models.CharField(max_length=200, verbose_name="퀘스트 제목")
    description = models.TextField(verbose_name="상세 내용")
    start_date = models.DateField(auto_now_add=True, verbose_name="시작일")
    duration_days = models.PositiveIntegerField(default=1, verbose_name="기한 (일)")
    
    # Rewards
    reward_gold = models.PositiveIntegerField(default=0, verbose_name="보상 골드")
    reward_items = models.ManyToManyField(Ingredient, through=QuestRewardItem, blank=True, related_name='quests')

    def __str__(self):
        return self.title

class QuestLog(models.Model):
    # Assumes your Character model is in the 'member' app
    author = models.ForeignKey('member.Characters', on_delete=models.CASCADE, related_name="quest_logs")
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="logs")
    
    title = models.CharField(max_length=200, verbose_name="게시글 제목")
    content = models.TextField(verbose_name="로그 내용")
    image = models.ImageField(upload_to='quest_logs/', blank=True, null=True, verbose_name="첨부 이미지")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Show newest logs first

class LogComment(models.Model):
    log = models.ForeignKey(QuestLog, on_delete=models.CASCADE, related_name="comments")
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)




class Chapter(models.Model):
    # 챕터의 기본 정보
    title = models.CharField(max_length=200, verbose_name="챕터 제목")
    subtitle = models.CharField(max_length=200, verbose_name="부제", blank=True)
    chapter_number = models.PositiveIntegerField(verbose_name="챕터 번호")
    story_type = models.CharField(max_length=10, choices=[('main', '메인'), ('sub', '서브')], default='main', verbose_name="스토리 타입")
    summary = models.TextField(verbose_name="줄거리 요약")
    
    # 표시될 이미지들
    background_image = models.ImageField(upload_to='story_backgrounds/', verbose_name="스토리 배경 이미지")
    list_image = models.ImageField(upload_to='chapter_thumbnails/', verbose_name="챕터 목록 이미지")

    def __str__(self):
        return self.title

class DialogueLine(models.Model):
    # ✨ 핵심: 이 대사가 어떤 챕터에 속해 있는지 연결합니다.
    # Chapter가 삭제되면, 관련된 대사들도 모두 함께 삭제됩니다 (CASCADE).
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='dialogue_lines')
    
    # 대사의 내용
    character_name = models.CharField(max_length=100, blank=True, verbose_name="화자 이름")
    text = models.TextField(verbose_name="대사 내용")
    
    # ❗️ 매우 중요: 대사의 순서를 결정할 필드입니다.
    order = models.PositiveIntegerField(verbose_name="순서")

    class Meta:
        # 'order' 필드를 기준으로 항상 정렬되도록 설정합니다.
        ordering = ['order']

    def __str__(self):
        return f"{self.chapter.title} - Line {self.order}"