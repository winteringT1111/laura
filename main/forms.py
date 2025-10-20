# your_app/forms.py
from django import forms
from .models import QuestLog, Quest
from datetime import date, timedelta

class QuestLogForm(forms.ModelForm):
    class Meta:
        model = QuestLog
        # The 'author' is set automatically in the view
        fields = ['quest', 'title', 'content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10, 'placeholder': '로그 내용을 작성해주세요.'}),
            'title': forms.TextInput(attrs={'placeholder': '게시글 제목'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show currently active quests in the dropdown
        today = date.today()
        # Example: show quests started in the last 3 days
        active_quests = Quest.objects.filter(start_date__gte=today - timedelta(days=3))
        self.fields['quest'].queryset = active_quests
        self.fields['quest'].label = "수행한 퀘스트"