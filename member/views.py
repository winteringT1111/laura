from django.shortcuts import render
from member.models import *
from users.models import CharInfo
from django.http import JsonResponse
from store.models import *
import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from itertools import chain
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from django.db import transaction, IntegrityError
from django.utils import timezone


@login_required
def member_profile(request, charEngName):
    target_char = get_object_or_404(Characters, charEngName=charEngName)
    char_info = None
    user = None
    inven = []
    is_own_profile = False # 기본값은 False
    recipient_list = []    # 양도 대상 목록

    try:

        char_info = CharInfo.objects.get(char=target_char)
        user = char_info.user
        inven_items = Inventory.objects.filter(user=user)
        ingred_items = Inventory_ingredient.objects.filter(user=user)
        recipe_items = Inventory_recipe.objects.filter(user=user)

        inven = list(chain(inven_items, ingred_items, recipe_items))  # 안전하게 합침

        # ✨ 자신의 프로필인지 확인
        if request.user == user:
            is_own_profile = True
            recipient_list = Characters.objects.all().order_by('charName')

        context = {
            'charname': charEngName,
            'charinfo': char_info,
            'char': target_char,
            'items': inven,
            'is_own_profile': is_own_profile, 
            'recipient_list': recipient_list, 
        }

    except:

        context = {
            'charname': charEngName,
            'char': target_char,
        }

    return render(request, "profile/member_profile.html", context)

@login_required
def member_main(request):
    all_characters = Characters.objects.all().order_by('charName')  # 이름 오름차순
    print(len(all_characters))
    context = {
        'chars': all_characters
    }
    return render(request, "profile/member_main.html", context)


@require_POST
@login_required
@transaction.atomic 
def transfer_item(request):
    try:
        data = json.loads(request.body)
        item_name = data.get('item_name')
        character_name = data.get('character_id')
        quantity = int(data.get('quantity', 1))

        if not item_name or not character_name or quantity < 1:
            return JsonResponse({'success': False, 'error': '필수 정보가 누락되었거나 수량이 잘못되었습니다.'}, status=400)

        sender_user = request.user
        sender_char_info = get_object_or_404(CharInfo, user=sender_user)
        
        # 받는 사람 정보 조회
        receiver_char = get_object_or_404(Characters, charName=character_name)
        receiver_info = get_object_or_404(CharInfo, char=receiver_char)
        receiver_user = receiver_info.user

        # --- ✨ 아이템 타입별 처리 로직 개선 ✨ ---
        
        # 1. 처리할 아이템 타입과 관련 모델들을 설정합니다.
        #    (아이템 모델, 인벤토리 모델, 선물 모델, 조회할 필드 이름)
        ITEM_TYPE_CONFIG = [
            (Ingredient, Inventory_ingredient, IngredientGift, 'itemName'),
            (Item, Inventory, Gift, 'itemName'),
            (Recipe, Inventory_recipe, RecipeGift, 'itemName'),
        ]

        item_instance = None
        inventory_model = None
        gift_model = None

        # 2. 설정된 순서대로 아이템을 찾습니다.
        for ItemModel, InvModel, GiftModel, field_name in ITEM_TYPE_CONFIG:
            try:
                # 각 모델의 필드 이름에 맞게 조회
                item_instance = ItemModel.objects.get(**{field_name: item_name})
                
                # 아이템을 찾으면, 관련된 모델들을 변수에 할당하고 루프를 빠져나옵니다.
                inventory_model = InvModel
                gift_model = GiftModel
                break
            except ItemModel.DoesNotExist:
                continue # 못 찾으면 다음 타입으로 넘어감

        # 3. 어떤 아이템도 찾지 못한 경우 에러 처리
        if not item_instance:
            return JsonResponse({'success': False, 'error': f"'{item_name}' 아이템을 찾을 수 없습니다."}, status=404)

        # 4. 보내는 사람의 인벤토리 확인
        try:
            sender_inven = inventory_model.objects.get(itemInfo=item_instance, user=sender_user)
            if sender_inven.itemCount < quantity:
                # 수량이 부족한 경우
                return JsonResponse({'success': False, 'error': f"'{item_name}' 아이템 수량이 부족합니다. ({quantity}개 필요)"}, status=400)
        except inventory_model.DoesNotExist:
            # 아이템을 아예 가지고 있지 않은 경우
            return JsonResponse({'success': False, 'error': f"'{item_name}' 아이템을 가지고 있지 않습니다."}, status=400)
        
        # 5. 모든 확인이 끝나면, 양도 내역 저장 및 아이템 차감
        item_message = "캐릭터 인벤토리에서 양도된 물품입니다."
        today = timezone.now()

        gift_model.objects.create(
            anonymous=False, message=item_message, orderDate=today,
            itemCount=quantity, itemInfo=item_instance,
            giver_user=sender_char_info, 
            receiver_user=receiver_info
        )

        if sender_inven.itemCount == quantity:
            sender_inven.delete()
        else:
            sender_inven.itemCount -= quantity
            sender_inven.save()

        return JsonResponse({'success': True, 'message': f"'{item_name}' {quantity}개를 성공적으로 양도했습니다."})

    # --- ✨ 에러 처리 개선 ✨ ---
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '잘못된 요청 형식입니다.'}, status=400)
    except Characters.DoesNotExist:
        return JsonResponse({'success': False, 'error': '받는 캐릭터를 찾을 수 없습니다.'}, status=404)
    except CharInfo.DoesNotExist:
        return JsonResponse({'success': False, 'error': '캐릭터 정보를 찾을 수 없습니다.'}, status=404)
    except IntegrityError:
        return JsonResponse({'success': False, 'error': '데이터 저장 중 오류가 발생했습니다.'}, status=500)
    except Exception as e:
        print(f"Unexpected error in transfer_item: {e}") # 디버깅을 위해 에러 로그 출력
        return JsonResponse({'success': False, 'error': '알 수 없는 오류가 발생했습니다.'}, status=500)

@login_required(login_url='/')
def giftbox(request):
    getUser = request.user
    getChar = CharInfo.objects.filter(user=request.user)[0]
    gift_list = Gift.objects.filter(receiver_user=getChar).order_by('orderDate')
    ingredientgift_list = IngredientGift.objects.filter(receiver_user=getChar).order_by('orderDate')
    recipegift_list = RecipeGift.objects.filter(receiver_user=getChar).order_by('orderDate')

    combined_gifts = list(gift_list) + list(ingredientgift_list) + list(recipegift_list)
    combined_gifts.sort(key=lambda x: x.orderDate, reverse=True)
    
    if request.method == "POST":
        gift_id = request.POST['giftidnum']
        gift_category = request.POST['giftcategory']
        
        if gift_category == "재료":
            target = IngredientGift.objects.get(giftID=gift_id)
                
            if not target.accepted:

                all_items = Inventory_ingredient.objects.filter(user_id=getUser).values_list('itemInfo', flat=True)
                item = target.itemInfo
                        
                if item.itemID in all_items:
                    update_item = Inventory_ingredient.objects.get(itemInfo=item, user=getUser)
                    update_item.itemCount += target.itemCount
                    update_item.save()
                else:
                    inven = Inventory_ingredient(itemCount=target.itemCount,
                                        itemInfo=item,
                                        user=getUser)
                    inven.save()        

                target.accepted = True
                target.save()

        elif gift_category == "조합 아이템":
            target = RecipeGift.objects.get(giftID=gift_id)
                
            if not target.accepted:

                all_items = Inventory_recipe.objects.filter(user_id=getUser).values_list('itemInfo', flat=True)
                item = target.itemInfo
                        
                if item.itemID in all_items:
                    update_item = Inventory_recipe.objects.get(itemInfo=item, user=getUser)
                    update_item.itemCount += target.itemCount
                    update_item.save()
                else:
                    inven = Inventory_recipe(itemCount=target.itemCount,
                                        itemInfo=item,
                                        user=getUser)
                    inven.save()        

                target.accepted = True
                target.save()
         
        else:
            target = Gift.objects.get(giftID=gift_id)
            
            if not target.accepted:
                
                all_items = Inventory.objects.filter(user_id=getUser).values_list('itemInfo', flat=True)
                item = target.itemInfo
                        
                if item.itemID in all_items:
                    update_item = Inventory.objects.get(itemInfo=item, user=getUser)
                    update_item.itemCount += target.itemCount
                    update_item.save()
                else:
                    inven = Inventory(itemCount=target.itemCount,
                                        itemInfo=item,
                                        user=getUser)
                    inven.save()        

                target.accepted = True
                target.save()
                
        return JsonResponse({'status': 'success', 'message': '선물이 수락되었습니다.'})

    context = {
        'gifts':combined_gifts
    }
    
    return render(request, "gift/giftbox.html",context)



@require_POST
@login_required
@transaction.atomic
def use_item(request):
    try:
        data = json.loads(request.body)
        item_name = data.get('item_name')
        user = request.user

        if not item_name:
            return JsonResponse({'success': False, 'error': '아이템 이름이 필요합니다.'}, status=400)

        char_info = get_object_or_404(CharInfo, user=user)
        message = ""
        obtained_items_details = [] # 포춘쿠키 결과 저장용

        # --- 아이템 찾기 및 수량 확인 (여러 인벤토리 모델 검색) ---
        item_instance = None
        inventory_instance = None
        
        # 1. 일반 아이템 인벤토리(Inventory) 확인
        try:
            item_instance = Item.objects.get(itemName=item_name)
            inventory_instance = Inventory.objects.get(user=user, itemInfo=item_instance)
            if inventory_instance.itemCount < 1:
                 return JsonResponse({'success': False, 'error': f"'{item_name}' 아이템이 부족합니다."}, status=400)
        except (Item.DoesNotExist, Inventory.DoesNotExist):
            return JsonResponse({'success': False, 'error': f"'{item_name}' 아이템을 찾을 수 없거나 보유하고 있지 않습니다."}, status=404)


        # --- 아이템 종류별 로직 실행 ---

        # 스테미나 사용 로직
        if item_name == "스테미나": # 실제 아이템 이름 확인
            if char_info.quest == 0:
                char_info.quest = 1
                message = "퀘스트 수행 가능 횟수가 1회 충전되었습니다."
            elif char_info.quest == 1:
                char_info.quest = 2
                message = "퀘스트 수행 가능 횟수가 최대로 충전되었습니다. (2회)"
            else: # 이미 2회 이상이면
                 return JsonResponse({'success': False, 'error': '이미 퀘스트 수행 가능 횟수가 최대입니다.'}, status=400)
            char_info.save()

        # 수정구 사용 로직
        elif item_name == "수정구": # 실제 아이템 이름 확인
            all_scrolls = Scroll.objects.all()
            if all_scrolls.exists():
                random_scroll = random.choice(all_scrolls)
                message = random_scroll.itemInfo # 스크롤 내용을 메시지로 전달
            else:
                message = "수정구가 희미하게 빛나지만 아무것도 보이지 않습니다..."

        # 포춘쿠키 사용 로직
        elif item_name == "포춘쿠키": # 실제 아이템 이름 확인
            message = "포춘쿠키를 열어 아이템을 획득했습니다!"
            is_rare_item = random.random() < 0.5 # 10% 확률로 Item
            
            if is_rare_item:
                item_pool = Item.objects.exclude(itemName__in=["포춘쿠키", "수정구", "스테미나"]) # 자신 및 사용 아이템 제외
                InventoryModel = Inventory
            else:
                item_pool = Ingredient.objects.all()
                InventoryModel = Inventory_ingredient
            
            if item_pool.count() >= 3:
                selected_items = random.sample(list(item_pool), 3)
                
                for item in selected_items:
                    quantity = random.randint(1, 3)
                    inv_slot, created = InventoryModel.objects.get_or_create(
                        user=user, itemInfo=item, defaults={'itemCount': 0}
                    )
                    inv_slot.itemCount += quantity
                    inv_slot.save()
                    
                    # 결과를 프론트에 전달하기 위한 데이터 구성
                    obtained_items_details.append({
                        'name': item.itemName if hasattr(item, 'itemName') else item.name,
                        'quantity': quantity,
                        'icon_url': f"/static/img/store/{item.itemName if hasattr(item, 'itemName') else item.name}.png" # 아이콘 경로 생성 (필요시 모델 필드 사용)
                    })
            else:
                # 아이템 풀이 부족할 경우 처리
                 message += "\n하지만 아무것도 나오지 않았습니다..."


        # --- 아이템 소모 ---
        inventory_instance.itemCount -= 1
        if inventory_instance.itemCount == 0:
            inventory_instance.delete()
        else:
            inventory_instance.save()
            
        return JsonResponse({
            'success': True, 
            'message': message,
            'obtained_items': obtained_items_details # 포춘쿠키 결과 전달
        })

    except Exception as e:
        print(f"Error in use_item: {e}") # 디버깅용 로그
        return JsonResponse({'success': False, 'error': '아이템 사용 중 오류가 발생했습니다.'}, status=500)