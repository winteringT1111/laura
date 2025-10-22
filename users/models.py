from django.db import models
from django.conf import settings
from main.models import Chapter, Quest
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

    class Meta:
        db_table = "charInfo"
        