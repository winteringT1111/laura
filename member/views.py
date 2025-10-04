from django.shortcuts import render,redirect
from member.models import *
from users.models import CharInfo
from store.models import *
import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator


def member_profile(request, charName):
    getUser = request.user
    # 1학년 캐릭터
    if charName == 'Werner' or charName == 'Tillman':
        char01 = Characters.objects.get(charFirstName=charName.capitalize(), charGrade=1)
        char04= ''
    else:
        char01 = Characters.objects.get(charFirstName=charName.capitalize(), charGrade=1)
        char04 = Characters.objects.get(charFirstName=charName.capitalize(), charGrade=4)
    char07 = Characters.objects.get(charFirstName=charName.capitalize(), charGrade=7)
    characinfo = CharInfo.objects.get(char=char01)
    
    if request.method == 'POST':       
        box = request.POST['boxtype']
        
        # 가챠 인형
        if box == "gacha":
            gachaname = request.POST['gachaName']
            target = Gacha.objects.get(itemName=gachaname)
            all_items = Inventory_gacha.objects.filter(user_id=getUser).values_list('itemInfo', flat=True)
                
            if target.itemID in all_items:
                update_item = Inventory_gacha.objects.get(itemInfo=target, user=getUser)
                update_item.itemCount += 1
                update_item.save()
            else:
                inven = Inventory_gacha(itemCount=1,
                                itemInfo=target,
                                user=getUser)
                inven.save()
                
            gachaitem = Item.objects.get(itemName="가챠")
            
            try:
                inven = Inventory.objects.get(itemInfo=gachaitem, user=getUser)
                
                if inven.itemCount == 1:
                    inven.delete()
                else:
                    inven.itemCount -= 1
                    inven.save()
            except:
                pass
                        
        else:
            magic_item_names = request.POST.getlist('magic_item_names')
            print(magic_item_names)
            
            for itemname in magic_item_names:
                target = Item_magic.objects.get(itemName=itemname)

                all_items = Inventory_magic.objects.filter(user_id=getUser).values_list('itemInfo', flat=True)
                
                if target.itemID in all_items:
                    update_item = Inventory_magic.objects.get(itemInfo=target, user=getUser)
                    update_item.itemCount += 1
                    update_item.save()
                else:
                    inven = Inventory_magic(itemCount=1,
                                    itemInfo=target,
                                    user=getUser)
                    inven.save()
                
            if box == "magic":
                testitem = Item.objects.get(itemName="마법 주머니")
                try:
                    inven = Inventory.objects.get(itemInfo=testitem, user=getUser)
                    
                    if inven.itemCount == 1:
                        inven.delete()
                    else:
                        inven.itemCount -= 1
                        inven.save()
                except:
                    pass
            else:
                testitem = Item.objects.get(itemName="고급 마법 주머니")
                try:
                    inven = Inventory.objects.get(itemInfo=testitem, user=getUser)
                    
                    if inven.itemCount == 1:
                        inven.delete()
                    else:
                        inven.itemCount -= 1
                        inven.save()
                except:
                    pass
            
    random_fortune = random.choice(Cookie.objects.all()).itemInfo
    random_scroll = random.choice(Scroll.objects.all()).itemInfo

    inven = Inventory.objects.filter(user_id=characinfo.user)    
    inven2 = Inventory_ring.objects.filter(user_id=characinfo.user)    
    inven3 = Inventory_magic.objects.filter(user_id=characinfo.user)
    inven4 = Inventory_potion.objects.filter(user_id=characinfo.user)
    inven5 = Inventory_gacha.objects.filter(user_id=characinfo.user)
    combined = list(inven) + list(inven2) + list(inven4) + list(inven5) + list(inven3) 
    
    # 마법 주머니
    items = Item_magic.objects.filter(itemDegree__in=[2, 3], itemCategory='마법 재료')
    num_items_to_pick = random.randint(3, 5)
    selected_items = random.sample(list(items), num_items_to_pick)
    
    # 고급 마법 주머니
    items2 = Item_magic.objects.filter(itemDegree__in=[1, 2], itemCategory='마법 재료')
    selected_items2 = random.sample(list(items2), num_items_to_pick)
    
    # 가챠
    selected_items3 = Gacha.objects.filter(itemCategory='가챠').exclude(itemName="사라 인형").order_by('?').first()
        
    paginator = Paginator(combined, 25) 
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    pages_items = [paginator.page(i).object_list for i in paginator.page_range]
    charnames = Characters.objects.filter(charGrade=7).values_list('charName', flat=True)
    
    context = {
        'charname': charName,
        'char': char01,
        'char04': char04,
        'char07': char07,
        'inven':combined,
        "page_obj": page_obj, 
        "pages_items": pages_items,
        "characinfo":characinfo,
        "random_fortune":random_fortune,
        "random_scroll":random_scroll,
        "magicItem":selected_items,
        "magicItem2":selected_items2,
        "gachaItem":selected_items3,
        'charnames': charnames
    }
    
    return render(request, "profile/member_profile.html", context)


            
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

def member_main(request):
    chars = Characters.objects.filter(charGrade=7).order_by('charFirstName')
    context = {
        'chars': chars
    }
    
    return render(request, "profile/member_main.html",context)


@login_required(login_url='/')
def giftbox(request):
    getUser = request.user
    gachagift_list = GachaGift.objects.filter(receiver_user=request.user).order_by('orderDate')
    gift_list = Gift.objects.filter(receiver_user=request.user).order_by('orderDate')
    magicgift_list = MagicGift.objects.filter(receiver_user=request.user).order_by('orderDate')

    combined_gifts = list(gachagift_list) + list(gift_list) + list(magicgift_list)
    combined_gifts.sort(key=lambda x: x.orderDate, reverse=True)
    
    if request.method == "POST":
        gift_id = request.POST['giftidnum']
        gift_category = request.POST['giftcategory']
        
        if gift_category == "마법 재료":
            target = MagicGift.objects.get(giftID=gift_id)
                
            if not target.accepted:

                all_items = Inventory_magic.objects.filter(user_id=getUser).values_list('itemInfo', flat=True)
                item = target.itemInfo
                        
                if item.itemID in all_items:
                    update_item = Inventory_magic.objects.get(itemInfo=item, user=getUser)
                    update_item.itemCount += target.itemCount
                    update_item.save()
                else:
                    inven = Inventory_magic(itemCount=target.itemCount,
                                        itemInfo=item,
                                        user=getUser)
                    inven.save()        

                target.accepted = True
                target.save()
        
        elif gift_category == "가챠":
            target = GachaGift.objects.get(giftID=gift_id)
                
            if not target.accepted:

                all_items = Inventory_gacha.objects.filter(user_id=getUser).values_list('itemInfo', flat=True)
                item = target.itemInfo
                        
                if item.itemID in all_items:
                    update_item = Inventory_gacha.objects.get(itemInfo=item, user=getUser)
                    update_item.itemCount += target.itemCount
                    update_item.save()
                else:
                    inven = Inventory_gacha(itemCount=target.itemCount,
                                    itemInfo=item,
                                    user=getUser)
                    inven.save()        

                target.accepted = True
                target.save()
                
        else:
            target = Gift.objects.get(giftID=gift_id)
            
            if not target.accepted:
                
                if target.itemInfo.itemName == "우정 반지":
                    inven = Inventory_ring(itemCount=1,
                                        itemInfo=Item.objects.get(itemName="우정 반지"),
                                        user=getUser,
                                        user2=target.giver_user)
                    inven.save()        

                    target.accepted = True
                    target.save()
                
                else:
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
                
                

    context = {
        'gifts':combined_gifts
    }
    
    return render(request, "gift/giftbox.html",context)
