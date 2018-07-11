from django.contrib import admin

# Register your models here.

from .models import WxOrderModel, OrderModel, BlessingModel
from accounts.models import UserModel
from django.urls import reverse
from django.utils.html import format_html


class OrderModelAdmin(admin.ModelAdmin):
    list_per_page = 20
    search_fields = ('order_content',)
    list_display = (
        'id', 'third_orderid', 'order_status', 'usermodel', 'username', 'target_username', 'txid', 'fee',
        'created_time')
    list_filter = ('order_status', 'city', 'fee')
    # list_editable = ('target_username', 'username')


class UserModelInLine(admin.StackedInline):
    model = UserModel


class BlessingModelAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'link_to_usermodel', 'link_to_ordermodel', 'created_time')

    def link_to_usermodel(self, obj):
        info = (obj.usermodel._meta.app_label, obj.usermodel._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.usermodel.id,))
        return format_html(u'<a href="%s">%s</a>' % (link, obj.usermodel.id))

    link_to_usermodel.short_description = '编辑用户'

    def link_to_ordermodel(self, obj):
        info = (obj.ordermodel._meta.app_label, obj.ordermodel._meta.model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.ordermodel.id,))
        return format_html(u'<a href="%s">%s</a>' % (link, obj.ordermodel.id))

    link_to_ordermodel.short_description = '编辑订单'
