import ldap
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import User_info
from datetime import datetime



# ldap_authenticate()向AD取得認證，三個參數為伺服器位址、帳號(不含DC)、密碼。
# 若錯誤，傳回錯誤訊息(字串)，若驗證正確，傳回[帳號, 姓名, 組別]
def ldap_authenticate(address, username, password):
    ldap_username = username + "@d634.taipower.com.tw"
    conn = ldap.initialize('ldap://' + address)
    conn.protocol_version = 3
    conn.set_option(ldap.OPT_REFERRALS, 0)
    success_output = [username]
    if password == "":
        return "請輸入開機密碼"
    if username == "":
        return "請輸入開機帳戶"
    try:
        result = conn.simple_bind_s(ldap_username, password)
    except ldap.INVALID_CREDENTIALS:
        return "認證錯誤，請輸入正確的帳號密碼"
    except ldap.SERVER_DOWN:
        return "伺服器關機，請通知資訊管理員"
    except ldap.LDAPError as e:
        if type(e.message) == dict and e.message.has_key('desc'):
            return "其他LDAP錯誤: " + e.message['desc']
        else: 
            return "其他LDAP錯誤: " + e
    else:
        basedn = "DC=d634,DC=taipower,DC=com,DC=tw"
        results = conn.search_s(basedn,ldap.SCOPE_SUBTREE,"(sAMAccountName=" +username  + ")")
        temp = results[0][0].split(",")
        for s in temp:
            if s.find("CN=") != -1:
                success_output.append(s[3:])
            if s.find("OU=") != -1:
                success_output.append(s[3:])
        conn.unbind_s()
    return success_output


# login_ldap()先檢查是否通過AD認證，如果成功，且有使用者，便更新密碼至最新，
# 如無此使用者，將產生使用者，並將使用者資訊（姓名、組別、身份）存入資料庫。
# 使用Django之內建認證系統。
def login_ldap(request):
    login_server = "s67620001"
    if 'account' in request.POST and 'password' in request.POST:
        account = request.POST['account']
        password = request.POST['password']
        login_info = ldap_authenticate(login_server, account, password)
        if type(login_info) is list and len(login_info) == 3:
            try:
                user = User.objects.get(username=account)
                user.set_password(password)
                user.save()
                # 搬移使用者組別後之處理
                user_info = User_info.objects.get(user_id=user)
                if user_info.section != login_info[2]:
                    user_info.section = login_info[2]
                    user_info.save()
            except:
                user = User.objects.create_user(account, account+'@taipower.com.tw', password)
                user.save()
                if login_info[0].upper().startswith("UAS"):
                    identity = "勞務人員"
                elif login_info[0].upper().startswith("W"):
                    identity = "AE人員"
                else:
                    identity = "正式員工"  
                user_info = User_info(user_id=user, section=login_info[2], name=login_info[1], identity=identity)
                user_info.save()

            djangoUser = authenticate(username=account, password=password)
            if user is not None:
                login(request, user)
                if 'next' in request.GET:
                    next = request.GET['next']
                else:
                    next = "/holidays/"  #預設重導之頁面
                return redirect(next)
            else:
                return redirect("/login/")
        else:
            return render(request, 'login.html', {'errors': login_info} )
    else:
        return render(request, 'login.html' )

def user_logout(request):
    logout(request)
    return redirect('/login/')


# def load_user_info(request):
#     with open(r"/var/django/ldap_output.txt", mode='r', encoding='utf8') as userinfo:
#         while True:
#             i = userinfo.readline()
#             if i == "":
#                 break
#             else:
#                 try:
#                     user = User.objects.get(username=i.split(",")[0].replace("\ufeff",""))
#                     user_info = User_info.objects.get(user_id=user)
#                     user_info.section = i.split(",")[2]
#                     user_info.name = i.split(",")[1]
#                     if i.split(",")[0].replace("\ufeff","").upper().startswith("UAS"):
#                         identity = "勞務人員"
#                     elif i.split(",")[0].replace("\ufeff","").upper().startswith("W"):
#                         identity = "AE人員"
#                     else:
#                         identity = "正式員工"
#                     user_info.identity = identity
#                     user_info.save()
#                     print(i.split(",")[0].replace("\ufeff",""))
#                 except:
#                     User.objects.create(
#                         username=i.split(",")[0].replace("\ufeff",""),
#                         date_joined=datetime.now(),
#                         is_staff=False,
#                         is_active=True,
#                         is_superuser=False,
#                         password="1234567"
#                     )
#                     user = User.objects.get(username=i.split(",")[0].replace("\ufeff",""))
#                     if i.split(",")[0].replace("\ufeff","").upper().startswith("UAS"):
#                         identity = "勞務人員"
#                     elif i.split(",")[0].replace("\ufeff","").upper().startswith("W"):
#                         identity = "AE人員"
#                     else:
#                         identity = "正式員工"
#                     User_info.objects.create(
#                         user_id=user,
#                         section=i.split(",")[2],
#                         name=i.split(",")[1],
#                         identity=identity
#                     )
#     return redirect("/order/")