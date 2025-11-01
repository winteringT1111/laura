from django.shortcuts import render,redirect
from django.contrib import auth
from django.contrib.auth.models import User
from member.models import Characters
from users.models import CharInfo
from django.contrib.auth.decorators import login_required
from .models import Dungeon, DungeonLog, CharInfo, TrapMessage
from .forms import DungeonLogFormB3 # B3 폼 임포트
import random

# Create your views here.



def signup(request):
    all_charac = Characters.objects.values_list('charEngName', flat=True)
    print(all_charac)
    
    if request.method == "POST":
        commucode = request.POST['commucode']
        print(request.POST['username'])

        if request.POST['password1']==request.POST['password2'] and commucode == "yggdrasil" and request.POST['username'] in all_charac:
            Newuser = User.objects.create_user(request.POST['username'], password=request.POST['password1'])            
            auth.login(request,Newuser)

            user = request.user
            char = CharInfo(char=Characters.objects.get(charEngName=request.POST['username']),
                            user=user,
                            gold=0,
                            exp=0,
                            quest=1,)
            char.save()
            
            return redirect('main:main_page')
    return render(request,'registration/signup.html')



def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('main:main_page')
        else:
            return render(request,'main.html', {'error':'오류입니다'})
    else:
        return render(request,'main.html')
    






# your_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.contrib import messages
from .models import Dungeon, DungeonLog, CharInfo
from .forms import DungeonLogForm

@login_required
def dungeon_b1_view(request):
    """던전 B1 메인 페이지"""
    dungeon = get_object_or_404(Dungeon, name="엘리시온 던전 B1") # B1 던전 정보 가져오기
    
    # 던전 진행률 최신화 (성능 고려: 자주 호출되지 않도록 캐싱 등 고려 가능)
    # dungeon.update_progress() 
    
    try:
        char_info = CharInfo.objects.get(user=request.user)
    except CharInfo.DoesNotExist:
        messages.error(request, "캐릭터 정보가 없습니다.")
        return redirect('main_page_or_error') # 적절한 URL로 변경

    # 리더보드: 던전 B1 기여도가 높은 상위 3명
    leaderboard = CharInfo.objects.filter(dungeon_b1_contribution__gt=0).order_by('-dungeon_b1_contribution')[:3]

    # 로그 피드
    dungeon_logs = DungeonLog.objects.filter(dungeon=dungeon).select_related('author_char')

    context = {
        'dungeon': dungeon,
        'user_contribution': char_info.dungeon_b1_contribution,
        'leaderboard': leaderboard,
        'dungeon_logs': dungeon_logs,
    }
    return render(request, 'dungeon1/dungeon_b1.html', context)


@login_required
def create_dungeon_log_view(request):
    """던전 로그 생성 페이지 및 처리"""
    dungeon_name = "엘리시온 던전 B1" # 던전 이름을 변수로 저장하여 일관성 유지
    dungeon = get_object_or_404(Dungeon, name=dungeon_name)
    
    if request.method == 'POST':
        form = DungeonLogForm(request.POST, request.FILES)
        if form.is_valid():
            # --- 유효성 검사 통과 시 ---
            try:
                with transaction.atomic(): 
                    # select_for_update()는 동시 요청 시 데이터 충돌 방지에 도움
                    char_info = CharInfo.objects.select_for_update().get(user=request.user) 

                    new_log = form.save(commit=False)
                    new_log.dungeon = dungeon
                    # CharInfo 모델에 'char' ForeignKey가 있다고 가정
                    new_log.author_char = char_info.char 
                    new_log.save()

                    # 사용자 기여도 및 전체 진행도 업데이트
                    char_info.update_dungeon_contribution(dungeon_name=dungeon_name)
                    dungeon.update_progress() 

                    messages.success(request, f"{new_log.distance_walked}m 탐험 기록을 남겼습니다!")
                    # ❗️ 리다이렉트할 URL 이름 확인 ('dungeon_b1_view' 또는 다른 이름)
                    return redirect('users:dungeon1_b1_view') 
            except CharInfo.DoesNotExist:
                 messages.error(request, "캐릭터 정보를 찾을 수 없습니다.")
            except Exception as e:
                # 예상치 못한 DB 저장 오류 등
                messages.error(request, f"기록 저장 중 오류가 발생했습니다: {e}")
                # 오류 발생 시 폼 페이지를 다시 보여주기 위해 아래로 이동
        
        else:
            # --- ❗️ 유효성 검사 실패 시 ---
            # 1. 터미널에 정확한 에러 내용 출력 (디버깅용)
            print(">>> Dungeon Log Form Validation Failed! Errors:")
            print(form.errors.as_json()) 
            
            # 2. 사용자에게 일반적인 에러 메시지 표시
            messages.error(request, "입력 내용을 확인해주세요. 오류가 있습니다.")
            # 실패 시 폼과 함께 현재 페이지를 다시 렌더링 (아래 return 문에서 처리)

    else: # GET 요청 시 (페이지 처음 로드)
        form = DungeonLogForm()

    # GET 요청이거나 POST 요청 실패 시 폼 페이지를 렌더링
    return render(request, 'dungeon1/create_dungeon_log.html', {'form': form})



@login_required
def dungeon_b3_view(request):
    """던전 B3 메인 페이지"""
    dungeon_name = "엘리시온 던전 B3"
    dungeon = get_object_or_404(Dungeon, name=dungeon_name)
    
    try:
        char_info = CharInfo.objects.get(user=request.user)
    except CharInfo.DoesNotExist:
        messages.error(request, "캐릭터 정보가 없습니다.")
        return redirect('main_page_or_error')

    # B3 기여도 랭킹
    leaderboard = CharInfo.objects.filter(dungeon_b3_contribution__gt=0).order_by('-dungeon_b3_contribution')[:3]

    dungeon_logs = DungeonLog.objects.filter(dungeon=dungeon).select_related('author_char')

    context = {
        'dungeon': dungeon,
        'user_contribution': char_info.dungeon_b3_contribution,
        'leaderboard': leaderboard,
        'dungeon_logs': dungeon_logs,
    }
    return render(request, 'dungeon1/dungeon_b3.html', context)


@login_required
def create_dungeon_log_b3_view(request):
    """B3 던전 로그 생성 및 함정 판정"""
    dungeon_name = "엘리시온 던전 B3"
    dungeon = get_object_or_404(Dungeon, name=dungeon_name)
    
    if request.method == 'POST':
        form = DungeonLogFormB3(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    char_info = CharInfo.objects.select_for_update().get(user=request.user)
                    character = char_info.char # 'Characters' 모델 인스턴스

                    # --- 함정 판정 로직 ---
                    base_success_rate = 40.0  # 기본 성공률 50%
                    luk_stat = character.charLUK if hasattr(character, 'charLUK') else 0 # 캐릭터의 LUK 스탯
                    bonus_rate = luk_stat * 4.0   # 1 LUK 당 4%
                    final_success_rate = min(base_success_rate + bonus_rate, 95.0) # 최대 95%
                    
                    roll = random.random() * 100
                    is_success = roll < final_success_rate
                    # --- 판정 끝 ---

                    print(bonus_rate, final_success_rate, roll)

                    new_log = form.save(commit=False)
                    new_log.dungeon = dungeon
                    new_log.author_char = character
                    new_log.was_successful = is_success

                    if is_success:
                        # 성공
                        messages.success(request, f"함정을 무사히 통과해 앞으로 나아갔습니다. (성공률: {final_success_rate}%)")
                    else:
                        # 실패
                        trap_message = TrapMessage.objects.order_by('?').first()
                        fail_text = trap_message.text if trap_message else "함정에 걸려 부상을 입었습니다."
                        # 실패 시, 사용자가 작성한 행동 지문 대신 함정 메시지를 기록
                        new_log.action_description = fail_text
                        messages.error(request, fail_text)
                    
                    new_log.save()

                    # 기여도 및 진행도 업데이트
                    char_info.update_dungeon_contribution(dungeon_name=dungeon_name)
                    dungeon.update_progress() 

                    return redirect('users:dungeon_b3_view')
            except Exception as e:
                messages.error(request, f"기록 저장 중 오류 발생: {e}")
        else:
            messages.error(request, "입력 내용을 확인해주세요.")
    else: # GET 요청
        form = DungeonLogFormB3()

    return render(request, 'dungeon1/create_dungeon_log_b3.html', {'form': form})