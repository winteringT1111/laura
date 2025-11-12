from django.shortcuts import render, redirect, get_object_or_404
from store.models import *
from users.models import CharInfo
from member.models import *
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages
from django.db import transaction 
import random
from django.http import JsonResponse

# Create your views here.

@login_required(login_url='/')
@transaction.atomic
def store_main(request):
    try:
        userinfo = CharInfo.objects.select_for_update().get(user=request.user)
    except CharInfo.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': '캐릭터 정보를 찾을 수 없습니다.'}, status=404)
        return redirect('main:main_page') # 👈 메인 페이지 URL 이름
        
    # --- POST 요청 (AJAX) 처리 ---
    if request.method == "POST":
        # ❗️ AJAX 요청이 아니면 거부 (보안 강화)
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'}, status=400)
            
        assort = request.POST.get('assort')
        
        try:
            if assort == "purchase":
                # --- 아이템 직접 구매 로직 ---
                item_name = request.POST.get('itemName')
                category = request.POST.get('category')
                currency = request.POST.get('currency', 'gold') # 👈 템플릿에서 보낸 화폐 종류
                count = int(request.POST.get('quantity', 1))
                if count < 1: raise ValueError("수량이 1보다 작습니다.")

                item_to_buy, InventoryModel = None, None
                
                if category == '재료':
                    item_to_buy = get_object_or_404(Ingredient, itemName=item_name)
                    InventoryModel = Inventory_ingredient
                else:
                    item_to_buy = get_object_or_404(Item, itemName=item_name)
                    InventoryModel = Inventory
                
                total_cost = item_to_buy.itemPrice * count
                
                # --- 화폐 종류 확인 및 차감 ---
                if currency == 'exp':
                    if userinfo.exp < total_cost:
                        return JsonResponse({'success': False, 'error': '경험치(EXP)가 부족합니다.'}, status=400)
                    userinfo.exp -= total_cost
                else:
                    if userinfo.gold < total_cost:
                        return JsonResponse({'success': False, 'error': '골드(G)가 부족합니다.'}, status=400)
                    userinfo.gold -= total_cost
                
                userinfo.save() # 변경사항 저장

                inv_slot, created = InventoryModel.objects.get_or_create(
                    user=request.user, itemInfo=item_to_buy, defaults={'itemCount': 0}
                )
                inv_slot.itemCount += count
                inv_slot.save()
                
                # ❗️ 성공 시 JSON 반환
                return JsonResponse({'success': True, 'message': '구매가 완료되었습니다.'})

            elif assort == "gift":
                # --- 아이템 선물 로직 ---
                item_name = request.POST.get('itemName2')
                category = request.POST.get('category2')
                currency = request.POST.get('currency', 'gold') # 👈 템플릿에서 보낸 화폐 종류
                receiver_name = request.POST.get('receiver')
                count = int(request.POST.get('quantity2', 1))
                if count < 1: raise ValueError("수량이 1보다 작습니다.")
                
                item_to_gift, GiftModel = None, None
                
                if category == '재료':
                    item_to_gift = get_object_or_404(Ingredient, itemName=item_name)
                    GiftModel = IngredientGift
                else:
                    item_to_gift = get_object_or_404(Item, itemName=item_name)
                    GiftModel = Gift
                
                receiver_char = get_object_or_404(Characters, charName=receiver_name)
                receiver_info = get_object_or_404(CharInfo, char=receiver_char)
                
                total_cost = item_to_gift.itemPrice * count
                
                # --- 화폐 종류 확인 및 차감 (선물) ---
                if currency == 'exp':
                    if userinfo.exp < total_cost:
                        return JsonResponse({'success': False, 'error': '경험치(EXP)가 부족합니다.'}, status=400)
                    userinfo.exp -= total_cost
                else:
                    if userinfo.gold < total_cost:
                        return JsonResponse({'success': False, 'error': '골드(G)가 부족합니다.'}, status=400)
                    
                userinfo.save()
                
                GiftModel.objects.create(
                    anonymous=(request.POST.get('anonymous') == 'on'),
                    message=request.POST.get('message'),
                    orderDate=datetime.today(),
                    itemCount=count,
                    itemInfo=item_to_gift,
                    giver_user=userinfo,
                    receiver_user=receiver_info
                )
                
                # ❗️ 성공 시 JSON 반환
                return JsonResponse({'success': True, 'message': '선물이 전달되었습니다.'})
            
            else:
                return JsonResponse({'success': False, 'error': '알 수 없는 요청입니다.'}, status=400)

        # ❗️ 실패 시 JSON 반환
        except (Item.DoesNotExist, Ingredient.DoesNotExist, Characters.DoesNotExist, CharInfo.DoesNotExist):
            return JsonResponse({'success': False, 'error': '데이터를 찾을 수 없습니다.'}, status=404)
        except ValueError:
             return JsonResponse({'success': False, 'error': '잘못된 수량입니다.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"알 수 없는 오류가 발생했습니다: {e}"}, status=500)

    # --- GET 요청 처리 (페이지 첫 로드) ---
    items_to_exclude = [
        "트로피", "행운의 편지", "장미 향수", "마녀 묘약", "초콜릿 세트"
    ]
    items = Item.objects.exclude(itemName__in=items_to_exclude)
    ingredients = Ingredient.objects.filter(itemShow=1)
    charnames = Characters.objects.all().values_list('charName', flat=True)  
        
    context = {
        'items': items,
        'ingredients': ingredients,
        'user2': userinfo,
        'charnames': charnames
    }
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
            caught_item_instance = Fish.objects.get(name="황금 연어")
            catch_description = f"엄청난 월척! [{caught_item_instance.name}]을(를) 낚았다!"
            score_gain = 10000
            caught_item_image_name = f"{caught_item_instance.name}.png"
        except Fish.DoesNotExist:
            catch_description = "거대한 무언가를 놓친 것 같다..."
            caught_item_image_name = "놓친 아이템.png"

    elif outcome < PROB_SALMON + PROB_GRADE1:
        fish_list = Fish.objects.filter(grade=1).exclude(name='황금 연어')
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
