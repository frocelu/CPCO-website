from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from holidays.models import Holiday
from datetime import date, timedelta

def is_admin(user):
    return user.groups.filter(name='訂餐系統管理者').exists()

def convert_date_format(date_list):
    convert_dates = []
    for the_date in date_list:
        year = the_date.split("-")[0]
        month = the_date.split("-")[1]
        day = the_date.split("-")[2]
        convert_dates.append(month + "/" + day + "/" +year)
    return convert_dates

# 設定假日
@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def list_Holidays(request, the_year=None):
    if not the_year:
        the_year = date.today().year
    minDate = date(int(the_year), 1, 1) - date.today()
    maxDate = date(int(the_year), 12, 31) - date.today()
    next_year = date.today().year + 1
    this_year = date.today().year
    holidays = []
    if Holiday.objects.filter(holidays__year=the_year):
        for holiday in Holiday.objects.filter(holidays__year=the_year).order_by('holidays'):
            holidays.append(str(holiday))
        holidays = convert_date_format(holidays)

    if 'ok' in request.POST and request.POST['ok'] != '':
        Holiday.objects.filter(holidays__year=the_year).delete()
        input_dates = request.POST['ok'].split(",")
        convert_dates = []
        for i in input_dates:
            year = int(i.split("/")[2])
            month = int(i.split("/")[0])
            day = int(i.split("/")[1])
            convert_dates.append(date(year, month, day))
        for i in convert_dates:
            holiday = Holiday(holidays=i)
            holiday.save()
        return redirect('/holidays/' + str(the_year))
    else:
        return render(
            request,
            'holidays.html', {
                '本年度':this_year,
                '明年度':next_year,
                '年度':the_year,
                '假日': holidays,
                'minDate': minDate.days,
                'maxDate': maxDate.days,})


# 將某一年度重設回只有星期六、日為休假日之狀態
@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def reset_default_weekends(request):
    if 'the_year' in request.POST:
        if request.POST['the_year']:
            try:
                the_year = int(request.POST['the_year'])
                if len(request.POST['the_year']) != 4:
                    errors = "請輸入4位數字"
                    return render(request, 'reset_default_weekends.html', {'errors': errors})
                existed = Holiday.objects.filter(holidays__year=the_year)
                if existed:
                    existed.delete()
                inyear_days = date(the_year, 12, 31) - date(the_year, 1, 1)
                for i in range(0, int(inyear_days.days)+1):
                    day = date(the_year, 1, 1) + timedelta(days=i)
                    if day.isoweekday() > 5:
                        weekend = Holiday(holidays=day)
                        weekend.save()
                return redirect('/holidays/' + str(the_year))
            except:
                errors = "請輸入數字"
                return render(request, 'reset_default_weekends.html', {'errors': errors})
        else:
            errors = "請輸入年度（4位數字）"
            return render(request, 'reset_default_weekends.html', {'errors': errors})
    else:
        return render(request, 'reset_default_weekends.html')
