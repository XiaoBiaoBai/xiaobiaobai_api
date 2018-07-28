from django.contrib import admin

# Register your models here.

from .models import WxOrderModel, OrderModel, BlessingModel
from accounts.models import UserModel
from django.urls import reverse
from django.utils.html import format_html


class ReadOnlyModelAdmin(admin.ModelAdmin):
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields] + \
               [field.name for field in obj._meta.many_to_many]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderModelAdmin(ReadOnlyModelAdmin):
    list_per_page = 20
    search_fields = ('order_content',)
    list_display = (
        'id', 'third_orderid', 'order_status', 'usermodel', 'username', 'target_username', 'txid', 'fee',
        'created_time')
    list_filter = ('order_status', 'city', 'fee')

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # list_editable = ('target_username', 'username')


class UserModelInLine(admin.StackedInline):
    model = UserModel


class BlessingModelAdmin(ReadOnlyModelAdmin):
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
