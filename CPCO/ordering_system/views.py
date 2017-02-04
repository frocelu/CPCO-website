from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from ordering_system.models import  *
from user_management.models import User_info
from datetime import date, datetime, timedelta, time
from holidays.views import Holiday
from django.core.exceptions import ObjectDoesNotExist
from collections import OrderedDict
from django.db.models import Sum, Case, When, Count
from time import sleep
import re



def check_disabled(a):
    if a:
        return ""
    else:
        return "disabled"

def last_month_start(d):
    month = d.month
    year = d.year
    if month == 1:
        last_month_m = 12
        last_month_y = year -1
    else:
        last_month_m = month -1
        last_month_y = year
    return date(last_month_y, last_month_m, 1)

def is_member(user):
    return user.groups.filter(name='訂餐系統使用者').exists()

def is_admin(user):
    return user.groups.filter(name='訂餐系統管理者').exists()

def date_to_dateobject(s):
    dateobject = s.split("-")
    return date(int(dateobject[0]), int(dateobject[1]), int(dateobject[2]))

def convert_date_format(s):
    return s.replace("/", "-")

def is_checked(b):
    if (b is True) or (b == 1):
        return "checked"
    else:
        return ""

def find_next_workday(d):
    t = d + timedelta(days=1)
    if Holiday.objects.filter(holidays=t):
        return find_next_workday(t)
    else:
        return t

def check_d_state_before_holiday(d):
    t = d + timedelta(days=1)
    if Holiday.objects.filter(holidays=t):
        return False
    else:
        return True

def check_b_state_after_holiday(d):
    t = d + timedelta(days=-1)
    if Holiday.objects.filter(holidays=t):
        return False
    else:
        return True


# 使用者界面「輸入預設設定」 使用者輸入預設狀態 須為伙食團成員
@login_required(login_url='/login/')
@user_passes_test(is_member, login_url='/login/')
def user_default_order_state(request):
    user = User.objects.get(username=request.user.username)
    # user = User.objects.get(username='u402685') # for test
    member = is_member(user)
    admin = is_admin(user)
    user_info = User_info.objects.get(user_id=user)
    breakfast = ""
    lunch = ""
    dinner = ""
    vegetarian = ""
    if not User_default_order_state.objects.filter(user_id=user):
        msg = "您尚未設定預設之訂餐狀態，請先設定"
        if 'csrfmiddlewaretoken' in request.POST:
            order_state = request.POST.getlist('order_state')
            order_state_list = [False, False, False, False]
            for i in order_state:
                if i == "breakfast":
                    breakfast = "checked"
                    order_state_list[0] = True
                elif i == "lunch":
                    lunch = "checked"
                    order_state_list[1] = True
                elif i == "dinner":
                    dinner = "checked"
                    order_state_list[2] = True
                elif i == "vegetarian":
                    vegetarian = "checked"
                    order_state_list[3] = True
            User_default_order_state.objects.create(
                user_id=user,
                b_state=order_state_list[0],
                l_state=order_state_list[1],
                d_state=order_state_list[2],
                v_state=order_state_list[3])
            msg = '已完成初次設定'
            return render(
                request,
                "user_default_order_state.html",
                {
                    'username': user_info.name,
                    'breakfast': breakfast,
                    'lunch': lunch,
                    'dinner': dinner,
                    'vegetarian': vegetarian,
                    'msg':msg,
                    'member': member,
                    'admin': admin})
        return render(
            request,
            "user_default_order_state.html",
            {
                'username': user_info.name,
                'breakfast': breakfast,
                'lunch': lunch,
                'dinner': dinner,
                'vegetarian': vegetarian,
                'msg':msg,
                'member': member,
                'admin': admin})
    else:
        default_state = User_default_order_state.objects.get(user_id=user)
        breakfast = is_checked(default_state.b_state)
        lunch = is_checked(default_state.l_state)
        dinner = is_checked(default_state.d_state)
        vegetarian = is_checked(default_state.v_state)
        if 'csrfmiddlewaretoken' in request.POST:
            order_state = request.POST.getlist('order_state')
            order_state_list = [False, False, False, False]
            for i in order_state:
                if i == "breakfast":
                    breakfast = "checked"
                    order_state_list[0] = True
                elif i == "lunch":
                    lunch = "checked"
                    order_state_list[1] = True
                elif i == "dinner":
                    dinner = "checked"
                    order_state_list[2] = True
                elif i == "vegetarian":
                    vegetarian = "checked"
                    order_state_list[3] = True
            default_state.b_state = order_state_list[0]
            default_state.l_state = order_state_list[1]
            default_state.d_state = order_state_list[2]
            default_state.v_state = order_state_list[3]
            default_state.save()
            msg = "已更新設定"
            return render(
                request,
                "user_default_order_state.html",
                {
                    'username': user_info.name,
                    'breakfast': breakfast,
                    'lunch': lunch,
                    'dinner': dinner,
                    'vegetarian': vegetarian,
                    'member': member,
                    'admin': admin,
                    'msg':msg})
        return render(
            request,
            "user_default_order_state.html",
            {
                'username': user_info.name,
                'breakfast': breakfast,
                'lunch': lunch,
                'dinner': dinner,
                'vegetarian': vegetarian,
                'member': member,
                'admin': admin})


# 使用者界面「輸入訂單」 使用者輸入訂單 有AD帳號即可操作
@login_required(login_url='/login/')
def user_input_order(request):
    user = User.objects.get(username=request.user.username)
    # user = User.objects.get(username='u402685') # for test
    member = is_member(user)
    admin = is_admin(user)
    startdate = date.today()
    enddate = startdate + timedelta(days=63)
    holiday = Holiday.objects.filter(holidays__range=[startdate, enddate])
    holidays = "addDisabledDates: ["
    for i in holiday:
        holidays += "'" + str(i) + "',"
    holidays = holidays[:-1]
    holidays += "]"

    # 可代替訂餐
    user_info = User_info.objects.get(user_id=user)
    user_name = user_info.name
    section_member = User_info.objects.filter(section=user_info.section)
    section = {}
    for i in section_member:
        if i.user_id != user:
            section[str(i.user_id)] = i.name
    if 'form-input-hidden' in request.POST:
        if request.POST['order_id'] != '':
            order_id = User.objects.get(username=request.POST['order_id'])
            order_hid = request.POST['order_id']
        else:
            order_id = user
            order_hid = request.user.username
        dates = date_to_dateobject(request.POST['form-input-hidden'])
        temp_order = Temp_order.objects.filter(user_id=order_id, order_date=dates)
        default_order = User_default_order_state.objects.filter(user_id=order_id)
        converted_date = "addDates:'" + request.POST['form-input-hidden'] + "',	disabled: true," \
            + "defaultDate:'" + request.POST['form-input-hidden'] +"'"
        b = check_b_state_after_holiday(dates)
        d = check_d_state_before_holiday(dates)
        b_after_holiday = check_disabled(b)
        d_before_holiday = check_disabled(d)
        if temp_order:
            breakfast = is_checked(temp_order.last().b_state * b)
            lunch = is_checked(temp_order.last().l_state)
            dinner = is_checked(temp_order.last().d_state * d)
            vegetarian = is_checked(temp_order.last().v_state)
        elif default_order:
            breakfast = is_checked(default_order[0].b_state * b)
            lunch = is_checked(default_order[0].l_state)
            dinner = is_checked(default_order[0].d_state * d)
            vegetarian = is_checked(default_order[0].v_state)
        else:
            if order_id == user:
                if user.groups.filter(name='訂餐系統使用者').exists():
                    return redirect('/order/set_user_default_state/')
                else:
                    return render(
                        request,
                        'user_input_order.html',
                        {
                            'error': "您未加入伙食團，請洽供應組負責人",
                            '組員': section,
                            'username': user_name,
                            'member': member,
                            'admin': admin})
            else:
                return render(
                    request,
                    'user_input_order.html',
                    {
                        'error': "被代理人未加入伙食團",
                        '組員': section,
                        'username':user_name,
                        'member': member,
                        'admin': admin})
        return render(
            request,
            'user_input_order.html',
            {
                'date': converted_date,
                'breakfast': breakfast,
                'lunch': lunch,
                'dinner': dinner,
                'vegetarian': vegetarian,
                '組員': section,
                'disabled':'disabled',
                'order_hid':order_hid,
                'username':user_name,
                '假期後早餐':b_after_holiday,
                '假期前晚餐':d_before_holiday,
                'member': member,
                'admin': admin
                }
            )
    elif 'step2' in request.POST:
        if request.POST['step2-order_id'] != "":
            order_id = User.objects.get(username=request.POST['step2-order_id'])
        else:
            order_id = user
        dates = date_to_dateobject(request.POST['step2'])
        state = [False, False, False, False]
        b = check_b_state_after_holiday(dates)
        d = check_d_state_before_holiday(dates)
        b_after_holiday = check_disabled(b)
        d_before_holiday = check_disabled(d)
        if 'breakfast' in request.POST.getlist('order'):
            state[0] = True
        if 'lunch' in request.POST.getlist('order'):
            state[1] = True
        if 'dinner' in request.POST.getlist('order'):
            state[2] = True
        if 'vegetarian' in request.POST.getlist('order'):
            state[3] = True

        # 利用送出時間檢查是否符合訂餐規定。
        timestamp = datetime.strptime(request.POST['step2-timestamp'], '%Y-%m-%d %H:%M:%S')
        datestamp = timestamp.date()
        if timestamp.hour >= 15 and (dates - datestamp) <= timedelta(days=2) and state[0] is True:
            return render(
                request,
                'user_input_order.html',
                {
                    'error': "早餐須在前天之15時前增訂/取消",
                    '組員': section,
                    'username':user_name,
                    'member': member,
                    'admin': admin})
        if timestamp.hour >= 15 and\
         (dates - datestamp) <= timedelta(days=1) and\
         (state[1] is True or state[2] is True):
            return render(
                request,
                'user_input_order.html',
                {
                    'error': "午、晚餐須在昨天之15時前增訂/取消",
                    '組員': section,
                    'username':user_name,
                    'member': member,
                    'admin': admin})
        Temp_order.objects.create(
            user_id=order_id,
            b_state=bool(state[0] * b),
            l_state=state[1],
            d_state=bool(state[2] * d),
            order_date=dates,
            v_state=state[3],
            make_order_user=user.username)
        return redirect('/order/input_order/')
    else:
        return render(
            request,
            'user_input_order.html',
            {
                '假日': holidays,
                '組員': section,
                'username':user_name,
                'member': member,
                'admin': admin})

# 使用者界面「查詢訂餐狀況」，有AD帳號即可查詢組內其他人之訂餐情形 記得要改上線日
@login_required(login_url='/login/')
def check_order(request):
    user = User.objects.get(username=request.user.username)
    # user = User.objects.get(username="u402685") # for test
    member = is_member(user)
    admin = is_admin(user)        
    user_info = User_info.objects.get(user_id=user)
    user_name = user_info.name
    section_member = User_info.objects.filter(section=user_info.section)
    section = {}
    online_date = 'minDate:"2017/1/18"' # 上線日
    for i in section_member:
        if i.user_id != user:
            section[str(i.user_id)] = i.name
    if 'user_id' in request.GET:
        if request.GET['user_id'] != "":
            try:
                user = User.objects.get(username=request.GET['user_id'])
            except ObjectDoesNotExist:
                error = "請輸入正確之開機帳號"
                return render(
                    request,
                    "user_check_order.html",
                    {
                        '組員': section,
                        'username':user_name,
                        'error':error,
                        'member': member,
                        'admin': admin})
        if request.GET['from'] == "" and request.GET['to'] == "":
            error = "請輸入查詢時間"
            return render(
                request,
                "user_check_order.html",
                {
                    '組員': section,
                    'username':user_name,
                    'error':error,
                    'member': member,
                    'admin': admin})
        elif request.GET['from'] == "" and request.GET['to'] != "":
            date_from = request.GET['to']
            date_to = request.GET['to']
        elif request.GET['from'] != "" and request.GET['to'] == "":
            date_from = request.GET['from']
            date_to = request.GET['from']
        else:
            date_from = request.GET['from']
            date_to = request.GET['to']
        # 查詢之code
        date_from = date_to_dateobject(convert_date_format(date_from))
        date_to = date_to_dateobject(convert_date_format(date_to))
        temp_result = {}
        diff_days = (date_to-date_from).days
        try:
            last_order_date = Order.objects.all().order_by('order_date').last().order_date
        except:
            last_order_date = datetime.strptime(online_date.split('"')[1], '%Y/%m/%d').date()
        holidays = []
        subscriber = User_info.objects.get(user_id=user).name
        for i in Holiday.objects.filter(holidays__range=[date_from, date_to]):
            holidays.append(i.holidays)
        for i in range(0, diff_days + 1):
            temp_date = date_from + timedelta(days=i)
            b = check_b_state_after_holiday(temp_date)
            d = check_d_state_before_holiday(temp_date)
            if temp_date not in holidays:
                if temp_date > last_order_date:
                    if Temp_order.objects.filter(user_id=user, order_date=temp_date):
                        temp = Temp_order.objects.filter(user_id=user, order_date=temp_date).last()
                    else:
                        try:
                            temp = User_default_order_state.objects.get(user_id=user)
                            temp.b_state = bool(temp.b_state * b)
                            temp.d_state = bool(temp.d_state * d)
                        except ObjectDoesNotExist:
                            return render(
                                request,
                                "user_check_order.html",
                                {
                                    '組員': section,
                                    'username':user_name,
                                    '上線日':online_date,
                                    'error':'您未加入伙食團或尚未設定預設狀態',
                                    'member': member,
                                    'admin': admin})
                else:
                    temp = Order.objects.filter(user_id=user, order_date=temp_date).last()
                if temp:
                    temp_result[str(temp_date)] = temp
                    temp_result = OrderedDict(sorted(temp_result.items()))
        return render(
            request,
            "user_check_order.html",
            {
                '組員': section,
                '被查詢人':subscriber,
                'data':temp_result,
                '上線日':online_date, 
                'username':user_name,
                'member': member,
                'admin': admin})
    return render(
        request,
        "user_check_order.html",
        {
            '組員': section,
            'username':user_name,
            '上線日':online_date,
            'member': member,
            'admin': admin})

# 管理界面「產生本日統計」 將暫存之訂單存入實際之資料庫
@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def temp_to_order(request):
    user = User.objects.all()
    now = datetime.now()
    # now = datetime(2017, 1, 26, 9, 0, 0) # for test
    today = date.today()
    # today = date(2017, 1 , 26) # for test
    next_workday = find_next_workday(today)
    next_workday_b = find_next_workday(next_workday)
    if now >= datetime.combine(today, time(15, 10, 0, 0)):
    # if now >= datetime.combine(today, time(8, 10, 0, 0)): # for test
        # 產生明天全日訂單
        for u in user:
            dinner_before_holiday = check_d_state_before_holiday(next_workday)
            breakfast_after_holiday = check_b_state_after_holiday(next_workday)
            temp = Temp_order.objects.filter(user_id=u, order_date=next_workday).last()
            default_order = User_default_order_state.objects.filter(user_id=u).last()
            if temp:
                name = User_info.objects.get(user_id=u).name
                identity = User_info.objects.get(user_id=u).identity
                section = User_info.objects.get(user_id=u).section
                cost = 0
                if not Order.objects.filter(user_id=u, user_name=name, order_date=temp.order_date):
                    if identity == "正式員工":
                        cost = 25 * temp.b_state * breakfast_after_holiday + 50 * temp.l_state \
                                    + 50 * temp.d_state * dinner_before_holiday
                    elif identity == "AE人員":
                        cost = 30 * temp.b_state * breakfast_after_holiday + 55 * temp.l_state \
                                    + 55 * temp.d_state * dinner_before_holiday
                    elif identity == "勞務人員":
                        cost = 30 * temp.b_state * breakfast_after_holiday + 55 * temp.l_state \
                                    + 55 * temp.d_state * dinner_before_holiday
                    Order.objects.create(
                        user_id=u,
                        user_name=name,
                        order_date=temp.order_date,
                        b_state=temp.b_state * breakfast_after_holiday,
                        l_state=temp.l_state,
                        d_state=temp.d_state * dinner_before_holiday,
                        v_state=temp.v_state,
                        cost=cost,
                        section=section)
            elif default_order:
                name = User_info.objects.get(user_id=u).name
                identity = User_info.objects.get(user_id=u).identity
                section = User_info.objects.get(user_id=u).section
                cost = 0
                if not Order.objects.filter(user_id=u, user_name=name, order_date=next_workday):
                    if identity == "正式員工":
                        cost = 25 * default_order.b_state * breakfast_after_holiday + 50 * default_order.l_state \
                                    + 50 * default_order.d_state * dinner_before_holiday
                    elif identity == "AE人員":
                        cost = 30 * default_order.b_state * breakfast_after_holiday + 55 * default_order.l_state \
                                    + 55 * default_order.d_state * dinner_before_holiday
                    elif identity == "勞務人員":
                        cost = 30 * default_order.b_state * breakfast_after_holiday + 55 * default_order.l_state \
                                    + 55 * default_order.d_state * dinner_before_holiday
                    Order.objects.create(
                        user_id=u, user_name=name, order_date=next_workday,
                        b_state=default_order.b_state * breakfast_after_holiday,
                        l_state=default_order.l_state,
                        d_state=default_order.d_state * dinner_before_holiday,
                        v_state=default_order.v_state,
                        cost=cost, section=section)
        # 產生後天早餐訂單
        for u in user:
            breakfast_after_holiday = check_b_state_after_holiday(next_workday_b)
            temp = Temp_order.objects.filter(user_id=u, order_date=next_workday_b).last()
            default_order = User_default_order_state.objects.filter(user_id=u).last()
            if temp:
                name = User_info.objects.get(user_id=u).name
                if not Order_b.objects.filter(user_id=u, user_name=name, order_date=temp.order_date):
                    Order_b.objects.create(
                        user_id=u,
                        user_name=name,
                        order_date=temp.order_date,
                        b_state=temp.b_state * breakfast_after_holiday)
            elif default_order:
                name = User_info.objects.get(user_id=u).name
                if not Order_b.objects.filter(user_id=u, user_name=name, order_date=next_workday_b):
                    Order_b.objects.create(
                        user_id=u,
                        user_name=name,
                        order_date=next_workday_b,
                        b_state=default_order.b_state * breakfast_after_holiday)
        sleep(1)
        return redirect('/order/check_daily_quantity/')
    else:
        sleep(5)
        return redirect('/order/') # 改掉

# 管理界面「管理使用者」 新增/移除 使用者/管理者 並列出目前所有名單
@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def modify_user(request):
    username = User.objects.get(username=request.user.username).user_info_set.last().name
    member = is_member(User.objects.get(username=request.user.username))
    admin = is_admin(User.objects.get(username=request.user.username))
    
    pat1 = re.compile(r'^u\d{6}$')
    pat2 = re.compile(r'^uas\d{4}$')
    pat3 = re.compile(r'^w\d{6}$')
    all_users = User.objects.filter(groups__name='訂餐系統使用者').order_by('user_info__section', 'username') # 透過外鍵查詢
    all_managers = User.objects.filter(groups__name='訂餐系統管理者').order_by('user_info__section', 'username')

    if 'action' in request.POST:
        userid = request.POST['username'].lower()
        action = request.POST['action']
        error = ""
        msg = ""
        if pat1.match(userid) or pat2.match(userid) or pat3.match(userid):
            if action == 'add':
                group = Group.objects.get(name='訂餐系統使用者')
                try:
                    user = User.objects.get(username=userid)
                except ObjectDoesNotExist:
                    error = "使用者尚未建立帳號資訊，請先讓使用者登入建立帳號資訊"
                    return render(
                        request,
                        'modify_user.html',
                        {
                            'error': error,
                            'all_managers': all_managers,
                            'all_users': all_users,
                            'username': username,
                            'admin': admin,
                            'member': member})
                user.groups.add(group)
                user_name = User_info.objects.get(user_id=user).name
                msg = "已將" + user_name + "加入伙食團"
                return render(
                    request,
                    'modify_user.html',
                    {
                        'msg':msg,
                        'all_managers':all_managers,
                        'all_users':all_users,
                        'username': username,
                        'admin': admin,
                        'member': member})
            elif action == 'del':
                group = Group.objects.get(name='訂餐系統使用者')
                try:
                    user = User.objects.get(username=userid)
                except ObjectDoesNotExist:
                    error = "使用者尚未建立帳號資訊，請先讓使用者登入建立帳號資訊"
                    return render(
                        request,
                        'modify_user.html',
                        {
                            'error':error,
                            'all_managers':all_managers,
                            'all_users':all_users,
                            'username': username,
                            'admin': admin,
                            'member': member})
                user.groups.remove(group)
                user_name = User_info.objects.get(user_id=user).name
                msg = "已將" + user_name + "移出伙食團"
                return render(
                    request,
                    'modify_user.html',
                    {
                        'msg':msg,
                        'all_managers':all_managers,
                        'all_users':all_users,
                        'username': username,
                        'admin': admin,
                        'member': member})
            elif action == 'add-m':
                group = Group.objects.get(name='訂餐系統管理者')
                try:
                    user = User.objects.get(username=userid)
                except ObjectDoesNotExist:
                    error = "使用者尚未建立帳號資訊，請先讓使用者登入建立帳號資訊"
                    return render(
                        request,
                        'modify_user.html',
                        {
                            'error':error,
                            'all_managers':all_managers,
                            'all_users':all_users,
                            'username': username,
                            'admin': admin,
                            'member': member})
                user.groups.add(group)
                user_name = User_info.objects.get(user_id=user).name
                msg = "已將" + user_name + "加入伙食團管理者"
                return render(
                    request,
                    'modify_user.html',
                    {
                        'msg':msg,
                        'all_managers':all_managers,
                        'all_users':all_users,
                        'username': username,
                        'admin': admin,
                        'member': member})
            elif action == 'del-m':
                group = Group.objects.get(name='訂餐系統使用者')
                try:
                    user = User.objects.get(username=userid)
                except ObjectDoesNotExist:
                    error = "使用者尚未建立帳號資訊，請先讓使用者登入建立帳號資訊"
                    return render(
                        request,
                        'modify_user.html',
                        {
                            'error':error,
                            'all_managers':all_managers,
                            'all_users':all_users,
                            'username': username,
                            'admin': admin,
                            'member': member})
                user.groups.remove(group)
                user_name = User_info.objects.get(user_id=user).name
                msg = "已將" + user_name + "移出伙食團管理者"
                return render(
                    request,
                    'modify_user.html',
                    {
                        'msg':msg,
                        'all_managers':all_managers,
                        'all_users':all_users,
                        'username': username,
                        'admin': admin,
                        'member': member})
        else:
            error = '請輸入正確之代號，如"u+姓名代號"、"uas+外包人員代號"、"w+AE人員代號"'
            return render(
                request,
                'modify_user.html',
                {
                    'error':error,
                    'all_managers':all_managers,
                    'all_users':all_users,
                    'username': username,
                    'admin': admin,
                    'member': member})
    return render(
        request,
        'modify_user.html',
        {
            'all_managers':all_managers,
            'all_users':all_users,
            'username': username,
            'admin': admin,
            'member': member})

# 管理界面「每日訂餐數統計」  查詢每天個數
@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def check_daily_quantity(request):
    today = date.today()
    # today = date(2017,1,20) # for test
    next_workday = find_next_workday(today)
    next_workday_b = find_next_workday(next_workday)
    username = User.objects.get(username=request.user.username).user_info_set.last().name
    member = is_member(User.objects.get(username=request.user.username))
    admin = is_admin(User.objects.get(username=request.user.username))
    error = ''
    order = Order.objects.filter(order_date=next_workday)
    order_b = Order_b.objects.filter(order_date=next_workday_b)
    breakfast_count = 0
    lunch_count = 0
    dinner_count = 0
    v_count = 0
    if order:
        for i in order:
            if i.l_state:
                lunch_count = lunch_count + 1
            if i.d_state:
                dinner_count = dinner_count + 1
            if i.v_state:
                v_count = v_count + 1
        for i in order_b:
            if i.b_state:
                breakfast_count = breakfast_count + 1
        none_v_count = lunch_count - v_count
        return render(request, 'check_daily_quantity.html', {
            '早餐計數':breakfast_count, '午餐計數':lunch_count, '晚餐計數':dinner_count,
            '素食計數':v_count, '葷食計數':none_v_count,
            '下個工作天':next_workday, '下個工作天_b':next_workday_b,
            'username': username, 'admin': admin, 'member': member})
    else:
        error = '今日尚未統計，請先至「產生本日統計」功能產生統計報表'
        return render(
            request,
            'check_daily_quantity.html',
            {
                'error':error,
                'username': username,
                'admin': admin,
                'member': member})

# 管理者界面「每月訂餐數統計」 列出上月的便當統計
@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def check_monthly_quantity(request):
    today = date.today()
    # today = date(2017, 2, 1) # for test
    last_month = last_month_start(today)
    this_month = date(today.year, today.month, 1)
    username = User.objects.get(username=request.user.username).user_info_set.last().name
    member = is_member(User.objects.get(username=request.user.username))
    admin = is_admin(User.objects.get(username=request.user.username))
    all_users = User.objects.filter(
        groups__name='訂餐系統使用者').order_by('user_info__section', 'username')
    all_sections = User_info.objects.exclude(section__contains="空污").values('section').distinct()
    result = {}
    section_total_cost = {}
    for s in all_sections:
        section_total_cost[s['section']] = 0
    for section in all_sections:
        result[section['section']] = []
    for user in all_users:
        user_monthly_obj = Order.objects.filter(
            user_id=user,
            order_date__range=[last_month, this_month])
        temp2 = {}
        temp = [
            user_monthly_obj.aggregate(
                b_state__sum=Count(Case(When(b_state=True, then=1))))['b_state__sum'],
            user_monthly_obj.aggregate(
                l_state__sum=Count(Case(When(l_state=True, then=1))))['l_state__sum'],
            user_monthly_obj.aggregate(
                d_state__sum=Count(Case(When(d_state=True, then=1))))['d_state__sum'],
            user_monthly_obj.aggregate(Sum('cost'))['cost__sum']
        ]
        temp2[user.user_info_set.last().name] = temp
        result[user.user_info_set.last().section].append(temp2)
    for section in section_total_cost:
        c = Order.objects.filter(order_date__range=[last_month, this_month], section=section)
        section_total_cost[section] = c.aggregate(Sum('cost'))['cost__sum']
    # 非公司員工訂餐
    none_staff = None_staff_order.objects.filter(
        order_date__range=[last_month, this_month]
        ).order_by('order_date', 'user_name')
    total_cost = none_staff.aggregate(Sum('cost'))
    return render(
        request,
        'check_monthly_quantity.html',
        {
            'result':result,
            '統計年':last_month.year,
            '統計月':last_month.month,
            '非公司人員':none_staff,
            '各組總和':section_total_cost,
            '非公司人員總計':total_cost['cost__sum'],
            'member': member,
            'admin': admin,
            'username': username})

# 管理者界面「臨時輸入」
@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def pressing_input(request):
    pat = re.compile(r'^[0-9]{4}[0-1]{1}[0-9]{1}[0-3]{1}[0-9]{1}$')
    username = User.objects.get(username=request.user.username).user_info_set.last().name
    member = is_member(User.objects.get(username=request.user.username))
    admin = is_admin(User.objects.get(username=request.user.username))
    if 'staff' in request.POST:
        if request.POST['name'] and request.POST['order_date']:
            name = request.POST['name']
            order_date = request.POST['order_date']
            user = User_info.objects.filter(name=name)
            order_state = request.POST.getlist('order')
            if user:
                user = user.last().user_id
            else:
                error = "請輸入正確之人員姓名"
                return render(
                    request,
                    'pressing_input.html',
                    {
                        'error': error,
                        'username': username,
                        'member': member,
                        'admin': admin})
            if pat.match(order_date):
                try:
                    order_date = datetime.strptime(order_date, '%Y%m%d').date()
                except:
                    error = "請輸入正確之日期格式"
                    return render(
                        request,
                        'pressing_input.html',
                        {
                            'error': error,
                            'username': username,
                            'admin': admin,
                            'member': member})
            else:
                error = "請輸入正確之日期格式"
                return render(
                    request,
                    'pressing_input.html',
                    {
                        'error': error,
                        'username': username,
                        'admin': admin,
                        'member': member})
            temp = Order.objects.filter(user_id=user.username, user_name=name, order_date=order_date)
            dinner_before_holiday = check_d_state_before_holiday(order_date)
            breakfast_after_holiday = check_b_state_after_holiday(order_date)
            if temp:
                temp = temp.last()
                temp.user_id = user.username
                temp.user_name = name
                temp.order_date = order_date
                b_state = False
                l_state = False
                d_state =False
                v_state = False
                for i in order_state:
                    if i == "breakfast":
                        b_state = True
                    elif i == "lunch":
                        l_state = True
                    elif i == "dinner":
                        d_state = True
                    elif i == "vegetarian":
                        v_state = True
                temp.b_state = bool(b_state * breakfast_after_holiday)
                temp.l_state = l_state
                temp.d_state = bool(d_state * dinner_before_holiday)
                temp.v_state = v_state
                identity = user.user_info_set.last().identity
                if identity == "正式員工":
                    cost = 25 * temp.b_state * breakfast_after_holiday + 50 * temp.l_state \
                                + 50 * temp.d_state * dinner_before_holiday
                elif identity == "AE人員":
                    cost = 30 * temp.b_state * breakfast_after_holiday + 55 * temp.l_state \
                                + 55 * temp.d_state * dinner_before_holiday
                elif identity == "勞務人員":
                    cost = 30 * temp.b_state * breakfast_after_holiday + 55 * temp.l_state \
                                + 55 * temp.d_state * dinner_before_holiday
                temp.cost = cost
                temp.section = user.user_info_set.last().section
                temp.add_by_manager = True
                temp.save()
            else:
                b_state = False
                l_state = False
                d_state =False
                v_state = False
                for i in order_state:
                    if i == "breakfast":
                        b_state = bool(True * breakfast_after_holiday)
                    elif i == "lunch":
                        l_state = True
                    elif i == "dinner":
                        d_state = bool(True * dinner_before_holiday)
                    elif i == "vegetarian":
                        v_state = True
                identity = user.user_info_set.last().identity
                if identity == "正式員工":
                    cost = 25 * b_state * breakfast_after_holiday + 50 * l_state \
                                + 50 * d_state * dinner_before_holiday
                elif identity == "AE人員":
                    cost = 30 * b_state * breakfast_after_holiday + 55 * l_state \
                                + 55 * d_state * dinner_before_holiday
                elif identity == "勞務人員":
                    cost = 30 * b_state * breakfast_after_holiday + 55 * l_state \
                                + 55 * d_state * dinner_before_holiday
                Order.objects.create(
                    user_id=user.username,
                    user_name=request.POST['name'],
                    order_date=order_date,
                    b_state=b_state,
                    l_state=l_state,
                    d_state=d_state,
                    v_state=v_state,
                    cost=cost,
                    section=user.user_info_set.last().section,
                    add_by_manager=True
                    )
            msg = "儲存成功"
            return render(
                request,
                'pressing_input.html',
                {
                    'msg': msg,
                    'username': username,
                    'member': member,
                    'admin': admin})
        else:
            error = "請輸入使用者姓名和訂餐日期"
            return render(
                request,
                'pressing_input.html',
                {
                    'error': error,
                    'username': username,
                    'member': member,
                    'admin': admin})
    elif 'none_staff' in request.POST:
        if request.POST['name'] and request.POST['order_date'] and request.POST['quantity']:
            user_name = request.POST['name']
            if pat.match(request.POST['order_date']):
                try:
                    order_date = datetime.strptime(request.POST['order_date'], '%Y%m%d').date()
                except:
                    error = "請輸入正確之日期格式"
                    return render(
                        request,
                        'pressing_input.html',
                        {
                            'error': error,
                            'username': username,
                            'admin': admin,
                            'member': member})
            else:
                error = "請輸入正確之日期格式"
                return render(
                    request,
                    'pressing_input.html',
                    {
                        'error': error,
                        'username': username,
                        'admin': admin,
                        'member': member})
            try:
                l_quantity = int(request.POST['quantity'])
            except:
                error = "請輸入正確之數量"
                return render(
                    request,
                    'pressing_input.html',
                    {
                        'error': error,
                        'username': username,
                        'admin': admin,
                        'member': member})
            if 'v_state' in request.POST:
                v_state = True
            else:
                v_state = False
            cost = l_quantity * 60
            None_staff_order.objects.create(
                user_name=user_name,
                order_date=order_date,
                l_quantity=l_quantity,
                v_state=v_state,
                cost=cost)
            msg = '儲存成功'
            return render(
                request,
                'pressing_input.html',
                {
                    'msg': msg,
                    'username': username,
                    'member': member,
                    'admin': admin})
        else:
            error = "請輸入使用者之姓名、訂餐日期、數量"
            return render(
                request,
                'pressing_input.html',
                {
                    'error': error,
                    'username': username,
                    'admin': admin,
                    'member': member})
    else:
        return render(
            request,
            'pressing_input.html',
            {
                'username': username,
                'admin': admin,
                'member': member})

# 起始頁面，依權限給功能
def ordering_system_root(request):
    if  request.user.username:
        user = User.objects.get(username=request.user.username)
        # user = User.objects.get(username="u111111") # for test
        user_name = user.user_info_set.last().name
        member = is_member(user)
        admin = is_admin(user)
        return render(request, 'root.html', {'使用者':member, '管理者':admin, '姓名': user_name})
    else:
        return redirect('/login/?next=/order/')