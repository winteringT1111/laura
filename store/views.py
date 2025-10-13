from django.shortcuts import render,redirect
from store.models import Item, Ingredient
from users.models import CharInfo
from member.models import Characters, Purchase, Inventory, Gift
from django.contrib.auth.decorators import login_required
from datetime import datetime

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
            itemPrice = request.POST['totalPrice']
            count = int(request.POST['quantity'])
            
            # 갈레온 차감
            userinfo.gold = int(userinfo.gold) - int(itemPrice.split(' ')[0]) 
            userinfo.save()
            
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
            
            if_anonymous = request.POST.get('anonymous') == 'on'
            receiver = request.POST['receiver']
            receiver_char = Characters.objects.get(charName=receiver)
            item_message = request.POST.get('message')
            
            print(item_name,itemPrice,count,if_anonymous,receiver,item_message,datetime.today())
            
            # 구매내역 저장
            char = Gift(anonymous=if_anonymous,
                        message=item_message,
                        orderDate=datetime.today(),
                        itemCount=count,
                        itemInfo=Item.objects.get(itemName=item_name),
                        giver_user=getUser,
                        receiver_user=CharInfo.objects.get(char=receiver_char).user)
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

