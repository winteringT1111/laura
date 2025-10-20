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

@login_required
def member_profile(request, charEngName):
    target_char = get_object_or_404(Characters, charEngName=charEngName)

    try:

        char_info = CharInfo.objects.get(char=target_char)
        user = char_info.user
        inven_items = Inventory.objects.filter(user=user)
        ingred_items = Inventory_ingredient.objects.filter(user=user)
        recipe_items = Inventory_recipe.objects.filter(user=user)

        inven = list(chain(inven_items, ingred_items, recipe_items))  # 안전하게 합침
        context = {
            'charname': charEngName,
            'charinfo':char_info,
            'char': target_char,
            'items':inven
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


            
from django.http import JsonResponse
import json

def use_fortune_cookie(request):
    if request.method == 'POST':
        getUser = request.user
        data = json.loads(request.body)
        item_name = data.get('item_name')

        if item_name == 'fortune_cookie':
            item = Item.objects.get(itemName="포춘쿠키")
            try:
                inven = Inventory.objects.get(itemInfo=item, user=getUser)
                if inven.itemCount == 1:
                    inven.delete()
                else:
                    inven.itemCount -= 1
                    inven.save()
            except Inventory.DoesNotExist:
                return JsonResponse({'error': 'Item not found in inventory'}, status=404)

        elif item_name == 'time_turner':
            item = Item.objects.get(itemName="타임터너")
            char = CharInfo.objects.get(user=getUser)
            try:
                inven = Inventory.objects.get(itemInfo=item, user=getUser)
                if inven.itemCount == 1:
                    inven.delete()
                else:
                    inven.itemCount -= 1
                    inven.save()
                char.classToken += 1
                char.save()
            except Inventory.DoesNotExist:
                return JsonResponse({'error': 'Item not found in inventory'}, status=404)
        elif item_name == 'gown':
            item = Item.objects.get(itemName="투명 망토")
            char = CharInfo.objects.get(user=getUser)
            try:
                inven = Inventory.objects.get(itemInfo=item, user=getUser)
                if inven.itemCount == 1:
                    inven.delete()
                else:
                    inven.itemCount -= 1
                    inven.save()

            except Inventory.DoesNotExist:
                return JsonResponse({'error': 'Item not found in inventory'}, status=404)
            
        elif item_name == 'potion':
            potionName = data.get('potionName')
            price = data.get('price')
            item = Potion.objects.get(itemName=potionName)
            char = CharInfo.objects.get(user=getUser)
            try:
                inven = Inventory_potion.objects.get(itemInfo=item, user=getUser)
                if inven.itemCount == 1:
                    inven.delete()
                else:
                    inven.itemCount -= 1
                    inven.save()
                char.galeon += int(price)
                char.save()
            except Inventory_potion.DoesNotExist:
                return JsonResponse({'error': 'Potion not found in inventory'}, status=404)

        elif item_name == 'scroll':
            item = Item.objects.get(itemName="스크롤")
            try:
                inven = Inventory.objects.get(itemInfo=item, user=getUser)
                if inven.itemCount == 1:
                    inven.delete()
                else:
                    inven.itemCount -= 1
                    inven.save()
            except Inventory.DoesNotExist:
                return JsonResponse({'error': 'Item not found in inventory'}, status=404)

        return JsonResponse({'success': 'Item used successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


from django.http import JsonResponse
from datetime import datetime
def transfer_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_name = data.get('item_name')  # 양도할 아이템 이름
        character_name = data.get('character_id')  # 양도할 캐릭터 ID
        print(item_name,character_name)
        
        if item_name == "우정 반지(상자)":
            receiver_char = Characters.objects.get(charName=character_name, charGrade=1)
            count = 1
            item_message = "캐릭터 인벤토리에서 양도된 물품입니다."
                
            print(item_name,receiver_char.charName,item_message,datetime.today())
                
            # 양도내역 저장
            char = Gift(anonymous=False,
                        message=item_message,
                        orderDate=datetime.today(),
                        itemCount=count,
                        itemInfo=Item.objects.get(itemName="우정 반지"),
                        giver_user=request.user,
                        receiver_user=CharInfo.objects.get(char=receiver_char).user)
            char.save()
            
            # 자기도 가짐
            getinven = Inventory_ring(itemCount=1,
                                        itemInfo=Item.objects.get(itemName="우정 반지"),
                                        user=request.user,
                                        user2=CharInfo.objects.get(char=receiver_char).user)
            getinven.save()        
            
            # 물품 차감
            item = Item.objects.get(itemName=item_name)
            
            try:
                inven = Inventory.objects.get(itemInfo=item, user=request.user)
                    
                if inven.itemCount == 1:
                    inven.delete()
                else:
                    inven.itemCount -= 1
                    inven.save()
            except:
                pass
            return JsonResponse({'success': True})
        else:
            try:
                # 양도할 아이템과 캐릭터 가져오기
                receiver_char = Characters.objects.get(charName=character_name, charGrade=1)
                count = 1
                item_message = "캐릭터 인벤토리에서 양도된 물품입니다."
                
                print(item_name,receiver_char.charName,item_message,datetime.today())
                
                # 양도내역 저장
                char = MagicGift(anonymous=False,
                            message=item_message,
                            orderDate=datetime.today(),
                            itemCount=count,
                            itemInfo=Item_magic.objects.get(itemName=item_name),
                            giver_user=request.user,
                            receiver_user=CharInfo.objects.get(char=receiver_char).user)
                char.save()
                
                # 물품 차감
                item = Item_magic.objects.get(itemName=item_name)
                try:
                    inven = Inventory_magic.objects.get(itemInfo=item, user=request.user)
                    
                    if inven.itemCount == 1:
                        inven.delete()
                    else:
                        inven.itemCount -= 1
                        inven.save()
                except:
                    pass
                return JsonResponse({'success': True})

            except:
                # 양도할 아이템과 캐릭터 가져오기
                receiver_char = Characters.objects.get(charName=character_name, charGrade=1)
                count = 1
                item_message = "캐릭터 인벤토리에서 양도된 물품입니다."
                
                print(item_name,receiver_char.charName,item_message,datetime.today())
                
                # 양도내역 저장
                char = GachaGift(anonymous=False,
                            message=item_message,
                            orderDate=datetime.today(),
                            itemCount=count,
                            itemInfo=Gacha.objects.get(itemName=item_name),
                            giver_user=request.user,
                            receiver_user=CharInfo.objects.get(char=receiver_char).user)
                char.save()
                
                # 물품 차감
                item = Gacha.objects.get(itemName=item_name)
                try:
                    inven = Inventory_gacha.objects.get(itemInfo=item, user=request.user)
                    print("-------------111111111")
                    
                    if inven.itemCount == 1:
                        inven.delete()
                        print("-------------22222222222")
                    else:
                        inven.itemCount -= 1
                        inven.save()
                        print("-------------33333333333")
                except:
                    pass
                return JsonResponse({'success': True})
                

    return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'})


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

        elif gift_category == "조합":
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
