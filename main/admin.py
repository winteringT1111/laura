from django.contrib import admin
from users.models import CharInfo
from member.models import *
from store.models import *
from main.models import *

# Register your models here.
admin.site.register(CharInfo)
admin.site.register(Item)
admin.site.register(Item_magic)
admin.site.register(Inventory)
admin.site.register(Inventory_magic)
admin.site.register(Inventory_gacha)
admin.site.register(Inventory_potion)
admin.site.register(Characters)
admin.site.register(Gift)
admin.site.register(MagicGift)
admin.site.register(GachaGift)
admin.site.register(Potion)
admin.site.register(PotionStatus)
admin.site.register(Attendance)

admin.site.register(Article)