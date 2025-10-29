from django.db import models
from django.conf import settings
from main.models import Chapter, Quest
from django.db.models import Sum
# Create your models here.

class CharInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    char = models.ForeignKey('member.Characters', on_delete=models.CASCADE)
    gold = models.IntegerField()
    exp = models.IntegerField()
    quest = models.IntegerField()
    attendance_date = models.DateField(null=True, blank=True) 
    attendance_count = models.IntegerField(default=0)  # 누적 출석 일 수 추가
    today_attended = models.BooleanField(default=False)  # 금일 출석 여부 추가
    completed_chapters = models.ManyToManyField(Chapter, blank=True, related_name='completed_by_characters')
    completed_quests = models.ManyToManyField(Quest, blank=True, related_name='completed_by_char_info')
    fishing_score = models.PositiveIntegerField(default=0, verbose_name="낚시 점수")

    dungeon_b1_contribution = models.PositiveIntegerField(default=0, verbose_name="엘리시온 던전 B1 기여도(m)")

    def update_dungeon_contribution(self, dungeon_name="던전 B1"):
        """특정 던전에 대한 이 캐릭터의 총 기여도 업데이트"""
        total = DungeonLog.objects.filter(author_char=self.char, dungeon__name=dungeon_name).aggregate(Sum('distance_walked'))['distance_walked__sum']
        if dungeon_name == "엘리시온 던전 B1": # 다른 던전도 추가 가능
            self.dungeon_b1_contribution = total if total is not None else 0
        self.save()

    class Meta:
        db_table = "charInfo"
        


class Dungeon(models.Model):
    """던전 자체의 정보를 담는 모델 (예: B1, B2 등)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="던전 이름")
    goal_distance = models.PositiveIntegerField(default=4000, verbose_name="목표 거리(m)")
    current_distance = models.PositiveIntegerField(default=0, verbose_name="현재 누적 거리(m)")

    def __str__(self):
        return self.name

    def update_progress(self):
        """이 던전에 대한 모든 로그의 거리를 합산하여 current_distance 업데이트"""
        total = DungeonLog.objects.filter(dungeon=self).aggregate(Sum('distance_walked'))['distance_walked__sum']
        self.current_distance = total if total is not None else 0
        self.save()

    @property
    def progress_percentage(self):
        """진행률 계산 (0~100 사이 값)"""
        if self.goal_distance == 0:
            return 0
        return min(int((self.current_distance / self.goal_distance) * 100), 100)
    

    
class DungeonLog(models.Model):
    """사용자가 던전에서 걸은 기록을 남기는 로그"""
    dungeon = models.ForeignKey(Dungeon, on_delete=models.CASCADE, related_name="logs")
    author_char = models.ForeignKey('member.Characters', on_delete=models.CASCADE, related_name="dungeon_logs") # Characters 모델 연결
    title = models.CharField(max_length=200, verbose_name="로그 제목")
    action_description = models.TextField(blank=True, null=True, verbose_name="행동 지문")
    distance_walked = models.PositiveIntegerField(default=0, verbose_name="걸은 거리(m)")
    log_image = models.ImageField(upload_to='dungeon_logs/', blank=True, null=True, verbose_name="로그 이미지")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # 최신 로그가 위로

    def __str__(self):
        return f"{self.author_char.charName} - {self.dungeon.name} ({self.distance_walked}m)"