from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.http.response import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.models import UserModel, WxUserModel
from orders.viewmodels import PostLoveSerializer
from orders.manager import OrderManager


def submit_lovecontent(request):
    """
    发布誓言
    :param request:
    :return:
    """
    if request.method == 'POST':
        serializer = PostLoveSerializer(data=request.data)
        if serializer.is_valid():
            ordermodel, jsdata = OrderManager.create_order(serializer)
            if ordermodel and jsdata:
                return JsonResponse(jsdata)
            else:
                return JsonResponse({"msg": "创建订单失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return JsonResponse({"msg": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"msg": "only for post"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
