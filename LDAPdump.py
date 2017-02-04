import ldap
import os

def ldap_authenticate(address, username):
    ldap_username = username + "@d634.taipower.com.tw"
    conn = ldap.initialize('ldap://' + address)
    conn.protocol_version = 3
    conn.set_option(ldap.OPT_REFERRALS, 0)
    success_output = [username]
    result = conn.simple_bind_s(r"a402685@d634.taipower.com.tw", r"xj4qo65j/402685")
    basedn = "DC=d634,DC=taipower,DC=com,DC=tw"
    results = conn.search_s(basedn,ldap.SCOPE_SUBTREE,"(sAMAccountName=" +username  + ")")
    temp = results[0][0].split(",")
    for s in temp:
        if s.find("CN=") != -1:
            success_output.append(s[3:])
        if s.find("OU=") != -1:
            success_output.append(s[3:])
    return success_output

basedir = os.path.dirname(os.path.abspath(__file__))

for i in range(1000000):
    account = "u" + str(i).zfill(6)
    try:
        strlist = ldap_authenticate("s67620008", account)
        for i in strlist:
            with open(os.path.join(basedir, "ldap_output.txt"), "a", encoding='utf8') as myfile:
                myfile.write(i + ",")
        with open(os.path.join(basedir, "ldap_output.txt"), "a", encoding='utf8') as myfile:
            myfile.write("\n")
    except:
        pass

for i in range(100):
    account = "uas" + "60" + str(i).zfill(2)
    try:
        strlist = ldap_authenticate("s67620008", account)
        for i in strlist:
            with open(os.path.join(basedir, "ldap_output.txt"), "a", encoding='utf8') as myfile:
                myfile.write(i + ",")
        with open(os.path.join(basedir, "ldap_output.txt"), "a", encoding='utf8') as myfile:
            myfile.write("\n")
    except:
        pass

for i in range(1000):
    account = "w" + "762" + str(i).zfill(3)
    try:
        strlist = ldap_authenticate("s67620008", account)
        for i in strlist:
            with open(os.path.join(basedir, "ldap_output.txt"), "a", encoding='utf8') as myfile:
                myfile.write(i + ",")
        with open(os.path.join(basedir, "ldap_output.txt"), "a", encoding='utf8') as myfile:
            myfile.write("\n")
    except:
        pass