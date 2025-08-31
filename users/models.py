from django.db import models
from django.conf import settings
from member.models import Characters
# Create your models here.

class CharInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    char = models.ForeignKey(Characters, on_delete=models.CASCADE)
    galeon = models.IntegerField()
    classToken= models.IntegerField()
    searchDone = models.IntegerField()
    attendance_date = models.DateField(null=True, blank=True) 
    attendance_count = models.IntegerField(default=0)  # 누적 출석 일 수 추가
    today_attended = models.BooleanField(default=False)  # 금일 출석 여부 추가

    class Meta:
        db_table = "charInfo"
        