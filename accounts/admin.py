from django.contrib import admin


# Register your models here.


class UserModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'sex')


class WxUserModelAdmin(admin.ModelAdmin):
    list_display = ('openid', 'matedata')
