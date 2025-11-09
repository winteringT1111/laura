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
    dungeon_b3_contribution = models.PositiveIntegerField(default=0, verbose_name="던전 B3 기여도(성공 횟수)") # 👈 B3 기여도
    dungeon_b1_drakus_contribution = models.PositiveIntegerField(default=0, verbose_name="드라쿠스 B1 기여도(pt)") # 👈 드라쿠스 B1 기여도

    def update_dungeon_contribution(self, dungeon_name):
        """캐릭터의 던전별 기여도를 업데이트합니다."""
        if dungeon_name == "엘리시온 던전 B1":
            total = DungeonLog.objects.filter(author_char=self.char, dungeon__name=dungeon_name).aggregate(Sum('distance_walked'))['distance_walked__sum']
            self.dungeon_b1_contribution = total if total is not None else 0
        elif dungeon_name == "엘리시온 던전 B3":
            # B3는 성공한 로그의 개수를 기여도로 계산
            total = DungeonLog.objects.filter(author_char=self.char, dungeon__name=dungeon_name, was_successful=True).count()
            self.dungeon_b3_contribution = total if total is not None else 0
        elif dungeon_name == "드라쿠스 던전 B1": # 👈 드라쿠스 B1 로직
            total = DungeonLog.objects.filter(author_char=self.char, dungeon__name=dungeon_name).aggregate(Sum('points_earned'))['points_earned__sum']
            self.dungeon_b1_drakus_contribution = total if total is not None else 0
   
        self.save()
        


# your_app/models.py
from django.db import models
from django.conf import settings
from django.db.models import Sum

class Dungeon(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="던전 이름")
    # B3의 경우, 목표를 100(%)으로 설정합니다.
    goal_progress = models.PositiveIntegerField(default=100, verbose_name="목표 진행도(%)")
    current_progress = models.PositiveIntegerField(default=0, verbose_name="현재 진행도(%)")
    goal_points = models.PositiveIntegerField(default=1000000, verbose_name="목표 포인트")
    current_points = models.PositiveIntegerField(default=0, verbose_name="현재 누적 포인트")

    def __str__(self):
        return self.name

    def update_progress(self):
        """이 던전의 진행도를 업데이트합니다."""
        if self.name == "엘리시온 던전 B3":
            # B3는 성공한 로그의 개수를 진행도로 사용합니다.
            total_success_logs = DungeonLog.objects.filter(dungeon=self, was_successful=True).count()
            self.current_progress = min(total_success_logs, self.goal_progress) # 100%를 넘지 않도록
        elif self.name == "엘리시온 던전 B1":
            # B1는 기존의 거리 합산 로직을 유지
            total_distance = DungeonLog.objects.filter(dungeon=self).aggregate(Sum('distance_walked'))['distance_walked__sum']
            self.current_progress = total_distance if total_distance is not None else 0
        elif self.name == "드라쿠스 던전 B1": # 👈 드라쿠스 B1 로직
            total = DungeonLog.objects.filter(dungeon=self).aggregate(Sum('points_earned'))['points_earned__sum']
            self.current_points = total if total is not None else 0
        self.save()

    @property
    def progress_percentage(self):
        """진행률 계산 (0~100 사이 값)"""
        if self.goal_progress == 0:
            return 0
        return min(int((self.current_progress / self.goal_progress) * 100), 100)


class DungeonLog(models.Model):
    """던전 로그 모델 (B1, B3 공용)"""
    dungeon = models.ForeignKey(Dungeon, on_delete=models.CASCADE, related_name="logs")
    author_char = models.ForeignKey('member.Characters', on_delete=models.CASCADE, related_name="dungeon_logs")
    title = models.CharField(max_length=200, verbose_name="로그 제목")
    action_description = models.TextField(blank=True, null=True, verbose_name="행동 지문")
    log_image = models.ImageField(upload_to='dungeon_logs/', blank=True, null=True, verbose_name="로그 이미지")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # --- B1 전용 ---
    distance_walked = models.PositiveIntegerField(default=0, verbose_name="걸은 거리(m)")
    # --- B3 전용 ---
    was_successful = models.BooleanField(default=False, verbose_name="함정 통과 여부")

    points_earned = models.PositiveIntegerField(default=0, verbose_name="획득 포인트") # 👈 포인트 필드 추가

    class Meta:
        ordering = ['-created_at']


# B3 함정 메시지를 저장할 새 모델
class TrapMessage(models.Model):
    text = models.TextField(verbose_name="함정/부상 메시지")
    
    def __str__(self):
        return self.text[:50]
    

class DungeonComment(models.Model):
    # This links the comment to a specific log
    log = models.ForeignKey(DungeonLog, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.log.title}"