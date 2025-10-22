from django.shortcuts import render, redirect
from store.models import *
from users.models import CharInfo
from member.models import *
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages
from django.db import transaction 
import random

# Create your views here.

@login_required(login_url='/')
def store_main(request):
    getUser = request.user
    userinfo = CharInfo.objects.get(user=getUser)
    
    items = Item.objects.all()
    ingredients = Ingredient.objects.filter(itemShow=1)
    
    if request.method == "POST":
        assort = request.POST['assort']
        
        if assort == "purchase":
            name = request.POST['itemName']
            category = request.POST['category']
            itemPrice = request.POST['totalPrice']
            count = int(request.POST['quantity'])
            
            # 갈레온 차감
            userinfo.gold = int(userinfo.gold) - int(itemPrice.split(' ')[0]) 
            userinfo.save()
            
            if category == '재료':
                # 인벤토리 저장
                all_items = Inventory_ingredient.objects.filter(user_id=getUser).values_list('itemInfo', flat=True)
                item = Ingredient.objects.get(itemName=name)
                
                if item.itemID in all_items:
                    update_item = Inventory_ingredient.objects.get(itemInfo=item, user=getUser)
                    update_item.itemCount += count
                    update_item.save()
                else:
                    inven = Inventory_ingredient(itemCount=count,
                                    itemInfo=item,
                                    user=getUser)
                    inven.save()

            else:
                # 구매내역 저장
                char = Purchase(itemCount=count,
                                orderDate=datetime.today(),
                                itemInfo=Item.objects.get(itemName=name),
                                user=getUser)
                char.save()
                
                # 인벤토리 저장
                all_items = Inventory.objects.filter(user_id=getUser).values_list('itemInfo', flat=True)
                item = Item.objects.get(itemName=name)
                
                if item.itemID in all_items:
                    update_item = Inventory.objects.get(itemInfo=item, user=getUser)
                    update_item.itemCount += count
                    update_item.save()
                else:
                    inven = Inventory(itemCount=count,
                                    itemInfo=item,
                                    user=getUser)
                    inven.save()
                    
                
        elif assort == "gift":
            item_name = request.POST['itemName2']   
            itemPrice = request.POST['totalPrice2']
            count = int(request.POST['quantity2'])
            category = request.POST['category2']
            
            if_anonymous = request.POST.get('anonymous') == 'on'
            receiver = request.POST['receiver']
            receiver_char = Characters.objects.get(charName=receiver)
            item_message = request.POST.get('message')
            
            if category == '재료':
                char = IngredientGift(anonymous=if_anonymous,
                        message=item_message,
                        orderDate=datetime.today(),
                        itemCount=count,
                        itemInfo=Ingredient.objects.get(itemName=item_name),
                        giver_user=CharInfo.objects.get(user=getUser),
                        receiver_user=CharInfo.objects.get(char=receiver_char))
                char.save()
            
            else:
                char = Gift(anonymous=if_anonymous,
                            message=item_message,
                            orderDate=datetime.today(),
                            itemCount=count,
                            itemInfo=Item.objects.get(itemName=item_name),
                            giver_user=CharInfo.objects.get(user=getUser),
                            receiver_user=CharInfo.objects.get(char=receiver_char))
                char.save()
            
            # 갈레온 차감
            userinfo.gold = int(userinfo.gold) - int(itemPrice.split(' ')[0]) 
            userinfo.save()            
            
    charnames = Characters.objects.all().values_list('charName', flat=True)   
        
    context = {'items':items,
               'ingredients':ingredients,
               'user2':userinfo,
               'charnames': charnames}

    return render(request, "store/store_main.html", context)




@login_required
def fishing_spot(request):
    """낚시터 메인 페이지 뷰"""
    try:
        char_info = CharInfo.objects.get(user=request.user)
    except CharInfo.DoesNotExist:
        # 캐릭터 정보가 없는 경우 처리 (예: 에러 페이지 또는 리다이렉트)
        return redirect('some_error_page') 

    # 리더보드: 낚시 점수가 높은 상위 3명 조회
    leaderboard = CharInfo.objects.order_by('-fishing_score')[:3]

    
    fishing_logs_raw = FishingLog.objects.all().select_related('author').prefetch_related('comments')
    
    processed_logs = []
    for log in fishing_logs_raw:
        processed_comments = []
        for comment in log.comments.all():
            parts = comment.comment_text.split('|')
            text = parts[0]
            icon_name = parts[1] if len(parts) > 1 else None
            processed_comments.append({'text': text, 'icon_name': icon_name})
            
        processed_logs.append({
            'log': log,
            'processed_comments': processed_comments
        })

    print(processed_logs)
    context = {
        'fishing_logs': processed_logs, # Pass the processed list
        'user_score': char_info.fishing_score,
        'leaderboard': leaderboard,
        'user_exp': char_info.exp,
    }
    return render(request, 'fishing/fishing_spot.html', context)



@login_required
@transaction.atomic
def cast_rod(request): # Add request parameter
    """Handles the logic when a user casts their fishing rod."""
    try:
        char_info = CharInfo.objects.get(user=request.user)
    except CharInfo.DoesNotExist:
        messages.error(request, "캐릭터 정보를 찾을 수 없습니다.")
        return redirect('store:fishing_spot') # Use your app name

    # 1. Check if user has enough EXP
    if char_info.exp < 10:
        messages.error(request, "경험치가 부족하여 낚시를 할 수 없습니다. (최소 10 EXP 필요)")
        return redirect('store:fishing_spot')

    # 2. Deduct EXP
    char_info.exp -= 10

    # Get action description from the form
    action_desc = request.POST.get('action_description', '')

    # 3. Determine the catch randomly
    outcome = random.random() * 100
    caught_item_instance = None
    catch_description = ""
    score_gain = 0
    caught_item_image_name = ""

    # Define catch probabilities
    PROB_SALMON = 0.3       # 0.3%
    PROB_GRADE1 = 8         # 8%
    PROB_GRADE2 = 15        # 15%
    PROB_GRADE3 = 30        # 30%
    PROB_INGREDIENT = 30    # 30%

    if outcome < PROB_SALMON:
        try:
            caught_item_instance = Fish.objects.get(name="2M 연어")
            catch_description = f"엄청난 월척! [{caught_item_instance.name}]을(를) 낚았다!"
            score_gain = 10000
            caught_item_image_name = f"{caught_item_instance.name}.png"
        except Fish.DoesNotExist:
            catch_description = "거대한 무언가를 놓친 것 같다..."
            caught_item_image_name = "놓친 아이템.png"

    elif outcome < PROB_SALMON + PROB_GRADE1:
        fish_list = Fish.objects.filter(grade=1)
        if fish_list.exists():
            caught_item_instance = random.choice(fish_list)
            catch_description = f"강한 손맛! [{caught_item_instance.name}(1등급)]을(를) 낚았다!"
            score_gain = 100
            caught_item_image_name = f"{caught_item_instance.name}.png"
        else:
            catch_description = "입질이 왔지만 놓쳤다..."
            caught_item_image_name = "놓친 아이템.png"

    elif outcome < PROB_SALMON + PROB_GRADE1 + PROB_GRADE2:
        fish_list = Fish.objects.filter(grade=2)
        if fish_list.exists():
            caught_item_instance = random.choice(fish_list)
            catch_description = f"꽤 힘이 센 [{caught_item_instance.name}(2등급)]을(를) 낚았다!"
            score_gain = 50
            caught_item_image_name = f"{caught_item_instance.name}.png"
        else:
            catch_description = "입질이 왔지만 놓쳤다..."
            caught_item_image_name = "놓친 아이템.png"

    elif outcome < PROB_SALMON + PROB_GRADE1 + PROB_GRADE2 + PROB_GRADE3:
        fish_list = Fish.objects.filter(grade=3)
        if fish_list.exists():
            caught_item_instance = random.choice(fish_list)
            catch_description = f"[{caught_item_instance.name}(3등급)]을(를) 낚았다."
            score_gain = 30
            caught_item_image_name = f"{caught_item_instance.name}.png"
        else:
            catch_description = "입질이 왔지만 놓쳤다..."
            caught_item_image_name = "놓친 아이템.png"

    elif outcome < PROB_SALMON + PROB_GRADE1 + PROB_GRADE2 + PROB_GRADE3 + PROB_INGREDIENT:
        ingredient_list = Ingredient.objects.all()
        if ingredient_list.exists():
            caught_item_instance = random.choice(ingredient_list)
            # ⬇️ Use .name instead of .itemName for Ingredient
            catch_description = f"[{caught_item_instance.itemName}] 재료를 낚았다."
            caught_item_image_name = f"{caught_item_instance.itemName}.png"
        else:
            catch_description = "무언가 반짝였지만 사라졌다..."
            caught_item_image_name = "놓친 아이템.png"

    else: # Trash
        trash_list = Trash.objects.all()
        if trash_list.exists():
            caught_item_instance = random.choice(trash_list)
            catch_description = f"이런... [{caught_item_instance.name}] 쓰레기를 낚았다."
            caught_item_image_name = f"{caught_item_instance.name}.png"
        else:
            catch_description = "낚싯줄이 텅 비어있다."
            caught_item_image_name = "빈 낚싯대.png"

    # 4. Update Inventory
    if caught_item_instance:
        item_model = type(caught_item_instance)

        if item_model == Ingredient:
            inv_slot, created = Inventory_ingredient.objects.get_or_create(
                user=request.user, itemInfo=caught_item_instance, defaults={'itemCount': 0}
            )
            inv_slot.itemCount += 1
            inv_slot.save()
        

    # 5. Update Fishing Score
    char_info.fishing_score += score_gain
    char_info.save() # Save EXP deduction and score gain

    # 6. Create Fishing Log
    new_log = FishingLog.objects.create(
        author=char_info.char,
        catch_description=catch_description,
        action_description=action_desc
    )

    # 7. Create Automatic Comment with image info
    comment_text = f"🎣 낚시 결과: {catch_description}"
    if score_gain > 0:
        comment_text += f" (점수 +{score_gain})"

    if caught_item_image_name:
        comment_text += f"|{caught_item_image_name}"

    FishingComment.objects.create(log=new_log, comment_text=comment_text)

    messages.success(request, catch_description)
    return redirect('store:fishing_spot') # Use your app name





# 간단한 낚시 게시글 등록 페이지 뷰 (폼 없이 버튼만)
@login_required
def create_fishing_log_page(request):
    try:
        char_info = CharInfo.objects.get(user=request.user)
    except CharInfo.DoesNotExist:
        return redirect('some_error_page')

    if char_info.exp < 10:
        messages.error(request, "경험치가 부족합니다.")
        return redirect('store:fishing_spot')
        
    return render(request, 'fishing/create_fishing_log.html')