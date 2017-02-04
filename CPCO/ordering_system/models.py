from django.db import models
from django.conf import settings

# Create your models here.
class User_default_order_state(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=None,
    )
    b_state = models.BooleanField()
    l_state = models.BooleanField()
    d_state = models.BooleanField()
    v_state = models.BooleanField()
    update_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        t = ""
        if self.b_state:
            t += "早"
        if self.l_state:
            t += "中"
        if self.d_state:
            t += "晚"
        if self.v_state:
            t += "素"
        return str(self.user_id) + "_" + t
    
class Temp_order(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=None,
    )
    order_date = models.DateField()
    b_state = models.BooleanField()
    l_state = models.BooleanField()
    d_state = models.BooleanField()
    v_state = models.BooleanField()
    add_time = models.DateTimeField(auto_now=True)
    make_order_user = models.CharField(max_length=7,blank=True, null=True)

    def __str__(self):
        t = ""
        if self.b_state:
            t += "早"
        if self.l_state:
            t += "中"
        if self.d_state:
            t += "晚"
        if self.v_state:
            t += "素"
        return str(self.user_id) + "_" + str(self.order_date) + "_" + t

class Order(models.Model):
    user_id = models.CharField(max_length=7, blank=True, null=True)
    user_name = models.CharField(max_length=10)
    order_date = models.DateField()
    b_state = models.BooleanField()
    l_state = models.BooleanField()
    d_state = models.BooleanField()
    v_state = models.BooleanField()
    cost = models.IntegerField()
    section = models.CharField(max_length=20, blank=True, null=True)
    add_by_manager = models.NullBooleanField(blank=True, null=True)


    add_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        t = ""
        if self.b_state:
            t += "早"
        if self.l_state:
            t += "中"
        if self.d_state:
            t += "晚"
        if self.v_state:
            t += "素"
        if self.user_id:
            return str(self.user_id) + "_" + str(self.order_date) + "_" + t
        else:
            return str(self.user_name) + "_" + str(self.order_date) + "_" + t

class Order_b(models.Model):
    user_id = models.CharField(max_length=7, blank = True, null = True)
    user_name = models.CharField(max_length=10)
    order_date = models.DateField()
    b_state = models.BooleanField()
    add_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        t = ""
        if self.b_state:
            t += "早"
        if self.user_id:
            return str(self.user_id) + "_" + str(self.order_date) + "_" + t
        else:
            return str(self.user_name) + "_" + str(self.order_date) + "_" + t

class None_staff_order(models.Model):
    user_name = models.CharField(max_length=20)
    order_date = models.DateField()
    l_quantity = models.IntegerField()
    v_state = models.BooleanField()
    cost = models.IntegerField()

    add_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user_name)

