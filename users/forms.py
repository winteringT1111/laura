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

class DungeonLogFormDrakusB1(forms.ModelForm): # 👈 드라쿠스 B1 전용 폼
    class Meta:
        model = DungeonLog
        # 'distance_walked', 'was_successful' 필드 제외
        fields = ['title', 'action_description', 'points_earned', 'log_image']
        widgets = {
            'action_description': forms.Textarea(attrs={'rows': 5, 'placeholder': '행동 지문을 적어주세요.'}),
            'title': forms.TextInput(attrs={'placeholder': '기록 제목'}),
            'points_earned': forms.NumberInput(attrs={'placeholder': '예: 5000'}),
        }
        labels = {
            'title': '제목',
            'action_description': '행동 지문',
            'points_earned': '획득 포인트(pt)', # 👈 라벨 변경
            'log_image': '기록 첨부',
        }

class DungeonLogFormDrakusB3(forms.ModelForm): # 👈 드라쿠스 B3 전용 폼
    class Meta:
        model = DungeonLog
        # 'distance_walked', 'points_earned', 'was_successful', 'damage_dealt' 제외
        fields = ['title', 'action_description', 'log_image']
        widgets = {
            'action_description': forms.Textarea(attrs={'rows': 5, 'placeholder': '(공백제외 200자)'}),
            'title': forms.TextInput(attrs={'placeholder': '전투 로그 제목'}),
        }
        labels = {
            'title': '제목',
            'action_description': '행동 지문',
            'log_image': '전투 기록 첨부',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 'log_image' 필드를 선택 사항(필수가 아님)으로 설정합니다.
        self.fields['log_image'].required = False