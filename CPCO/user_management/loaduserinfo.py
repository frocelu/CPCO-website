with open(r"E:\google drive\CPCO website\ldap_output.txt", mode='r', encoding='utf8') as userinfo:
    while True:
        i = userinfo.readline()
        if i == "":
            break
        else:
            print(i.split(",")[0].replace("\ufeff",""))