from django.contrib import admin
from users.models import CharInfo, Dungeon
from member.models import *
from store.models import *
from main.models import *

# Register your models here.
admin.site.register(CharInfo)
admin.site.register(Item)
admin.site.register(Inventory)
admin.site.register(Inventory_ingredient)
admin.site.register(Inventory_recipe)
admin.site.register(Characters)
admin.site.register(Gift)
admin.site.register(IngredientGift)
admin.site.register(Recipe)
admin.site.register(Attendance)
admin.site.register(Fish)
admin.site.register(Trash)
admin.site.register(Dungeon)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    # 'name' 필드를 기준으로 재료를 검색할 수 있도록 설정합니다.
    search_fields = ['name']

# --- Quest Admin 설정 ---
class QuestRewardItemInline(admin.TabularInline):
    model = QuestRewardItem
    extra = 1
    # 이제 이 기능이 정상적으로 작동합니다.
    autocomplete_fields = ['ingredient'] 

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'duration_days')
    inlines = [QuestRewardItemInline]


class DialogueLineInline(admin.TabularInline):
    model = DialogueLine
    extra = 1
    ordering = ('order',)

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter_number', 'story_type')
    inlines = [DialogueLineInline]