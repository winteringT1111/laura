# your_app/forms.py
from django import forms
from .models import DungeonLog

class DungeonLogForm(forms.ModelForm):
    class Meta:
        model = DungeonLog
        # author_char와 dungeon은 뷰에서 설정
        fields = ['title', 'action_description', 'distance_walked', 'log_image']
        widgets = {
            'action_description': forms.Textarea(attrs={'rows': 5, 'placeholder': '행동 지문을 적어주세요'}),
            'title': forms.TextInput(attrs={'placeholder': '기록 제목'}),
            'distance_walked': forms.NumberInput(attrs={'placeholder': '예: 150'}),
        }
        labels = {
            'title': '제목',
            'action_description': '행동 지문',
            'distance_walked': '걸은 거리(m)',
            'log_image': '탐험 기록 첨부',
        }


class DungeonLogFormB3(forms.ModelForm): # B3 전용 폼
    class Meta:
        model = DungeonLog
        fields = ['title', 'action_description', 'log_image']
        widgets = {
            'action_description': forms.Textarea(attrs={'rows': 5, 'placeholder': '텍스트를 적어주세요'}),
            'title': forms.TextInput(attrs={'placeholder': '탐험 제목'}),
        }
        labels = {
            'title': '제목',
            'action_description': '행동 지문',
            'log_image': '로그 첨부',
        }