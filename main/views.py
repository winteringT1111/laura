from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from member.models import *
from users.models import CharInfo
from main.models import *
from store.models import *
from django.utils import timezone
from django.http import JsonResponse
import random,ast,json
from django.http import JsonResponse
from .models import Quest, QuestLog, LogComment
from .forms import QuestLogForm
from django.db.models import F, ExpressionWrapper, DateField # Ensure ExpressionWrapper and DateField are imported
from datetime import date, timedelta
# Create your views here.


def main_page(request):
    return render(request, "main.html")

def notice(request):
    return render(request, "notice/notice.html")

def world(request):
    return render(request, "notice/world.html")

def system(request):
    return render(request, "notice/system.html")

def species(request):
    return render(request, "notice/species.html")

def war(request):
    return render(request, "notice/war.html")

def worldstory(request):
    return render(request, "notice/story.html")

def realm(request):
    return render(request, "notice/realm.html")

def novarium(request):
    return render(request, "notice/realm/novarium.html")

def belisar(request):
    return render(request, "notice/realm/belisar.html")

def zerka(request):
    return render(request, "notice/realm/zerka.html")

def tarvel(request):
    return render(request, "notice/realm/tarvel.html")

def elysion(request):
    return render(request, "notice/realm/elysion.html")

def cardin(request):
    return render(request, "notice/realm/cardin.html")

def drakus(request):
    return render(request, "notice/realm/drakus.html")

def necros(request):
    return render(request, "notice/realm/necros.html")

def serapium(request):
    return render(request, "notice/realm/serapium.html")


from django.templatetags.static import static
import json
@login_required
def story_view(request, room_name):
    try:
        chapter = Chapter.objects.get(id=room_name)
        dialogue_lines = chapter.dialogue_lines.all()
        
        script = []
        for line in dialogue_lines:
            character_name = line.character_name
            formatted_text = line.text
            
            script.append({
                "name": character_name,
                "text": formatted_text,
            })
        background_url = chapter.background_image.url if chapter.background_image else static('img/default_background.png')
    except Chapter.DoesNotExist:
        script = [{"name": "시스템", "text": "해당 스토리를 찾을 수 없습니다."}]
        background_url = static('img/default_background.png') # 에러 발생 시 기본 배경

    context = {'script': script, 'background_image_url': background_url} 

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'story_partial.html', context)
    
    return render(request, 'story.html', context)


@login_required 
@require_POST   
def claim_story_reward(request):
    try:
        # 1. JavaScript가 보낸 chapter_id를 받습니다.
        data = json.loads(request.body)
        chapter_id = data.get('chapter_id')
        
        if not chapter_id:
            return JsonResponse({'status': 'error', 'message': 'Chapter ID not provided'}, status=400)

        charinfo = CharInfo.objects.get(user=request.user)
        chapter_to_complete = Chapter.objects.get(id=chapter_id)

        # 2. ✨ 핵심 로직: 이미 완료한 챕터인지 확인합니다.
        if chapter_to_complete in charinfo.completed_chapters.all():
            # 이미 완료했다면, 보상을 주지 않고 "이미 받음" 상태를 반환합니다.
            return JsonResponse({'status': 'already_claimed', 'message': 'Reward already claimed.'})

        # 3. 최초 완료라면, 보상을 지급하고 완료 목록에 추가합니다.
        charinfo.gold += 50
        charinfo.completed_chapters.add(chapter_to_complete) # 완료 목록에 추가
        charinfo.save() # gold와 many-to-many 관계 모두 저장
        
        return JsonResponse({'status': 'success', 'message': 'Reward claimed!'})
    except Chapter.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Chapter not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def room(request):
    main_stories = []
    sub_stories = []
    completed_chapter_ids = []

    # 2. 로그인된 유저인지 확인합니다. (오류 방지를 위해 중요!)
    if request.user.is_authenticated:
        # 'story_type' 필드를 기준으로 메인/서브 스토리를 각각 가져옵니다.
        main_stories = Chapter.objects.filter(story_type='main').order_by('chapter_number')
        sub_stories = Chapter.objects.filter(story_type='sub').order_by('chapter_number')

        # 현재 유저가 완료한 챕터 ID 목록을 가져옵니다.
        # 'character'는 User 모델과 연결된 이름에 따라 다를 수 있습니다.
        if hasattr(request.user, 'character'):
            character = request.user.character
            completed_chapter_ids = list(character.completed_chapters.values_list('id', flat=True))

    # 3. 조회한 모든 데이터를 context 딕셔너리에 담습니다.
    context = {
        'main_stories': main_stories,
        'sub_stories': sub_stories,
        'completed_chapter_ids': completed_chapter_ids,
    }
    
    # 4. context와 함께 템플릿을 렌더링합니다.
    return render(request, "room.html", context)


@login_required(login_url='/login')
def supply(request):
    getUser = request.user
    charinfo = CharInfo.objects.get(user=getUser)
    userinfo = Characters.objects.get(charID=charinfo.char_id)
    
    # 현재 시간 확인
    current_time = timezone.localtime(timezone.now())
    current_hour = current_time.hour
    today_date = current_time.date()
    
    if request.method == "POST":
        # 출석 가능한 시간 6시 ~ 20시
        if 6 <= current_hour < 20:
            # 오늘 이미 출석한 기록이 있으면 출석 불가
            if charinfo.attendance_date == today_date:
                show_modal = "modal2"
                modal_message = "이미 오늘의 보급을 수령했습니다."
            else:
                # 출석이 가능하면 출석 처리
                charinfo.gold += 100  # 갈레온 추가
                charinfo.exp += 1000 # 수업토큰
                charinfo.quest = 1 # 일일퀘스트 한도 초기화
                charinfo.attendance_date = today_date  # 출석일 업데이트
                charinfo.today_attended = True  # 금일 출석 여부 업데이트
                
                # 누적 출석 일 수 업데이트
                charinfo.attendance_count += 1
                charinfo.save()
                
                show_modal = "modal1"
                modal_message = "보급을 수령했습니다."
        else:
            # 출석 시간이 아닌 경우
            show_modal = "modal2"
            modal_message = "보급 신청이 가능한 시각이 아닙니다."
        
        return JsonResponse({
            'show_modal': show_modal, 
            'modal_message': modal_message,
            'attendance_count': charinfo.attendance_count,  # 누적 출석 일 수
            'today_attended': charinfo.today_attended  # 금일 출석 현황
        })
    
    context = {
        'character': userinfo,
        'attendance_count': charinfo.attendance_count,  # 템플릿에 누적 출석 일 수 전달
        'today_attended': charinfo.today_attended  # 템플릿에 금일 출석 여부 전달
    }
    
    return render(request, "class/supply.html", context)


@login_required
def quest_board(request):
    today = date.today()

    # 1. Get all potentially active quests from the database
    potential_quests = Quest.objects.filter(start_date__lte=today).order_by('-start_date')

    # 2. Create the final list of data in a single, efficient loop
    active_quests_data = []
    for quest in potential_quests:
        expiration_date = quest.start_date + timedelta(days=quest.duration_days)

        # Check if the quest is currently active
        if quest.start_date <= today < expiration_date:
            remaining_days = (expiration_date - today).days

            # --- Build the JSON data for rewards ---
            rewards_list = []
            for reward in quest.questrewarditem_set.all():
                rewards_list.append({
                    'name': reward.ingredient.itemName,
                    'quantity': reward.quantity,
                })

            # --- Append the final dictionary to our list ---
            active_quests_data.append({
                'quest': quest,
                'remaining_days': remaining_days,
                'rewards_json': json.dumps(rewards_list)
            })

    # The rest of your view logic is correct
    quest_logs = QuestLog.objects.all().select_related('author', 'quest')
    try:
        char_info = CharInfo.objects.get(user=request.user)
        can_perform_quest = char_info.quest > 0
    except CharInfo.DoesNotExist:
        char_info = None
        can_perform_quest = False
    
    context = {
        'active_quests': active_quests_data,
        'quest_logs': quest_logs,
        'can_perform_quest': can_perform_quest,
        'char_info': char_info,
    }
    return render(request, 'quest/quest_board.html', context)


@login_required
def create_quest_log(request):
    char_info = CharInfo.objects.get(user=request.user)

    if char_info.quest <= 0:
        return redirect('main:quest_board')

    if request.method == 'POST':
        form = QuestLogForm(request.POST, request.FILES)
        if form.is_valid():
            quest = form.cleaned_data['quest']
            if char_info.completed_quests.filter(id=quest.id).exists():
                form.add_error(None, "이미 완료하여 보상을 받은 퀘스트입니다.")
            else:
                char_info.quest -= 1
                
                new_log = form.save(commit=False)
                new_log.author = char_info.char
                new_log.save()

                # --- ✨ 보상 지급 로직 수정 ✨ ---
                
                # 1. 골드 지급
                char_info.gold += quest.reward_gold
                
                # 2. 재료 지급 (여러 개 처리)
                # 퀘스트에 연결된 모든 보상 재료 정보를 가져옵니다.
                rewards_to_give = quest.questrewarditem_set.all()
                
                for reward in rewards_to_give:
                    # 유저의 인벤토리에서 해당 재료를 찾거나, 없으면 새로 만듭니다.
                    inventory_slot, created = Inventory_ingredient.objects.get_or_create(
                        user=request.user,
                        itemInfo=reward.ingredient,
                        defaults={'itemCount': 0} # 새로 만들 경우 itemCount의 초기값
                    )
                    # 수량을 더해줍니다.
                    inventory_slot.itemCount += reward.quantity
                    inventory_slot.save()

                # 3. 퀘스트 완료 처리 및 유저 정보 저장
                char_info.completed_quests.add(quest)
                char_info.save()

                # 4. 자동 댓글 생성
                reward_texts = []
                if quest.reward_gold > 0:
                    reward_texts.append(f"골드: {quest.reward_gold}")
                for reward in rewards_to_give:
                    reward_texts.append(f"{reward.ingredient.itemName} x{reward.quantity}")
                
                comment_text = f"퀘스트를 완료하여 보상을 획득했습니다! ({', '.join(reward_texts)})"
                LogComment.objects.create(log=new_log, comment_text=comment_text)

                return redirect('main:quest_board')
    else:
        form = QuestLogForm()
    return render(request, 'quest/create_quest_log.html', {'form': form})



    

# 마법의 약
@login_required(login_url='/login')
def potion(request):
    inven = Inventory_magic.objects.filter(user_id=request.user)
    paginator = Paginator(inven, 16)  # 한 페이지에 3개의 아이템

    # 페이지 번호를 가져오기
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 각 페이지의 아이템 목록을 생성
    pages_items = [paginator.page(i).object_list for i in paginator.page_range]
    token = CharInfo.objects.get(user=request.user).classToken
    
    try:
        status = PotionStatus.objects.get(user=request.user)
    except PotionStatus.DoesNotExist:
        status = PotionStatus(user=request.user, xp=0, degree=3)
        status.save()
        
    return render(request, "class/potion.html", {"page_obj": page_obj, "pages_items": pages_items, "token":token, "status":status})


@require_POST
def check_combination(request):
    
    char = CharInfo.objects.get(user=request.user)  # Get character data
    status = PotionStatus.objects.get(user=request.user)
    getUser = request.user
    
    try:
        # Parse the selected items from the request body
        data = json.loads(request.body)
        selected_items = data.get('selected_items', [])

        # Sort selected items to ensure order doesn't affect comparison
        selected_items_set = set(selected_items)

        # Initialize response variables
        result = "failure"
        image = "img/store/빈 물약.png"
        message = "" 

        potions = Potion.objects.all()

        for potion in potions:
            potion_recipe = set(ast.literal_eval(potion.potionRecipe))
            if selected_items_set == potion_recipe:
                # 등급 조정
                if status.degree > potion.degree:
                    break
                
                result = "success"
                image = f"img/store/{potion.itemName}.png" 
                if potion.discovered:
                    message = f"{potion.itemName} 조합에 성공했습니다!"
                    status.xp +=15
                    status.save()
                else:
                    message = f"{potion.itemName} 조합에 최초 성공했습니다!"
                    potion.discovered = True
                    potion.discoverer = request.user.username
                    status.xp +=30
                    potion.save()
                    status.save()
                
                # 인벤토리에 넣어주기
                target = potion
                all_items = Inventory_potion.objects.filter(user_id=getUser).values_list('itemInfo', flat=True)
                
                if target.itemID in all_items:
                    update_item = Inventory_potion.objects.get(itemInfo=target, user=getUser)
                    update_item.itemCount += 1
                    update_item.save()
                else:
                    inven = Inventory_potion(itemCount=1,
                                    itemInfo=target,
                                    user=getUser)
                    inven.save()    
                break 

        if result == 'failure':
            try:
                inven = Inventory.objects.get(user=request.user, itemInfo__itemName="빈 물약")
                inven.itemCount += 1
                inven.save()
            except:
                item_info = Item.objects.get(itemName="빈 물약")
                Inventory.objects.create(
                    user=request.user,
                    itemInfo=item_info,
                    itemCount=1
                )
            status.xp +=10
            status.save()
            
        # 토큰 차감
        char.classToken -= 1
        char.save()
        
        # 선택한 아이템 차감
        for item in selected_items_set:
            inven = Inventory_magic.objects.get(user=request.user, itemInfo__itemName=item)
            if int(inven.itemCount) == 1:
                inven.delete()
            else:
                inven.itemCount -= 1
                inven.save()
                
        if status.xp >= 170:
            status.degree = 2
            status.save()
        if status.xp >= 400:
            status.degree = 1
            status.save()

        # Return the result as a JSON response
        return JsonResponse({'result': result, 'image': image, 'message':message})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)


# 약초학
@login_required(login_url='/login')
def herb(request):
    random_herb_item = Item_magic.objects.filter(itemCategory2='약초학').order_by('?').first()
    random_number = random.randint(1, 3)
    getUser = request.user
    user = CharInfo.objects.get(user=getUser)
    
    if request.method == "POST":
        itemname = request.POST['herbname']
        count = int(request.POST['count'])
        print(itemname,count)
        
        target = Item_magic.objects.get(itemName=itemname)

        all_items = Inventory_magic.objects.filter(user_id=getUser).values_list('itemInfo', flat=True)
        
        if target.itemID in all_items:
            update_item = Inventory_magic.objects.get(itemInfo=target, user=getUser)
            update_item.itemCount += count
            update_item.save()
        else:
            inven = Inventory_magic(itemCount=count,
                            itemInfo=target,
                            user=getUser)
            inven.save()
            
        user.classToken -= 1
        user.save()
    
    
    context = {'herb': random_herb_item,
               'count': random_number,
               'token':user.classToken}
    
    return render(request, "class/herbology.html", context)


from django.db import transaction

@login_required(login_url='/login')
def recipe(request):
    inven = Inventory_ingredient.objects.filter(user=request.user, itemCount__gt=0)
    
    try:
        token = CharInfo.objects.get(user=request.user).gold
    except CharInfo.DoesNotExist:
        token = 0
        
    # --- ✨ 레시피 북을 위한 데이터 가공 ---
    all_recipes_data = []
    # 모든 레시피를 가져옵니다.
    for recipe in Recipe.objects.all().order_by('itemName'):
        try:
            ingredients = ast.literal_eval(recipe.recipe)
        except (ValueError, SyntaxError):
            ingredients = []

        # ✅ Split the discoverer's name here
        discoverer_first_name = ""
        if recipe.discoverer:
            # Get the full name, split by space, and take the first part
            discoverer_first_name = recipe.discoverer.split(' ')[0]

        all_recipes_data.append({
            'recipe': recipe,
            'ingredients': ingredients,
            'discoverer_first_name': discoverer_first_name 
        })
        
    context = {
        'inventory_items': inven,
        'token': token,
        'all_recipes': all_recipes_data, # 👈 가공된 레시피 데이터를 context에 추가
    }
    return render(request, "class/recipe.html", context)


@require_POST
@login_required
@transaction.atomic  # 👈 이 함수 내의 모든 DB 작업이 전부 성공하거나 전부 실패하도록 보장
def combine(request):
    try:
        data = json.loads(request.body)
        selected_items = data.get('selected_items', [])
        selected_items_set = set(selected_items)
        user = request.user
        char_info = CharInfo.objects.get(user=user)

        # 1. 토큰 및 재료 보유 여부 사전 확인
        if char_info.exp <= 0:
            return JsonResponse({'error': '경험치가 부족합니다.'}, status=400)
        
        for item_name in selected_items:
            if not Inventory_ingredient.objects.filter(user=user, itemInfo__itemName=item_name, itemCount__gt=0).exists():
                return JsonResponse({'error': f"'{item_name}' 재료가 부족합니다."}, status=400)

        # 2. 조합법 확인
        found_recipe = None
        for recipe in Recipe.objects.all():
            recipe_ingredients = set(ast.literal_eval(recipe.recipe))
            if selected_items_set == recipe_ingredients:
                found_recipe = recipe
                break

        # --- 재료 및 토큰 차감 (성공/실패 공통) ---
        char_info.exp -= 100
        char_info.save()

        for item_name in selected_items:
            inv = Inventory_ingredient.objects.get(user=user, itemInfo__itemName=item_name)
            inv.itemCount -= 1

            if inv.itemCount == 0:
                inv.delete()
            else:
                inv.save()

        # 3. 결과 처리
        if found_recipe:
            # 성공 로직
            is_first_discovery = not found_recipe.discovered
            if is_first_discovery:
                message = f"'{found_recipe.itemName}' 조합에 최초로 성공했습니다!"
                found_recipe.discovered = True
                found_recipe.discoverer = user.username
                found_recipe.save()
            else:
                message = f"'{found_recipe.itemName}' 조합에 성공했습니다!"
            
            # 성공 아이템 지급
            inv_slot, created = Inventory_recipe.objects.get_or_create(user=user, itemInfo=found_recipe, defaults={'itemCount': 0})
            inv_slot.itemCount += 1
            inv_slot.save()
            
            result_image = f"{found_recipe.itemName}.png"
            result_status = "success"
        else:
            # 실패 로직 (실패 시 아이템 지급은 제거)
            message = "아무 일도 일어나지 않았습니다..."
            result_image = "망한 아이템.png" # 실패 시 보여줄 기본 이미지
            result_status = "failure"

            failed_item_recipe = Recipe.objects.get(itemName="망한 아이템")
            inv_slot, created = Inventory_recipe.objects.get_or_create(user=user, itemInfo=failed_item_recipe, defaults={'itemCount': 0})
            inv_slot.itemCount += 1
            inv_slot.save()

        return JsonResponse({'result': result_status, 'image': result_image, 'message': message})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)