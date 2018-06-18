from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.http.response import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework.decorators import api_view

from accounts.models import UserModel, WxUserModel
from orders.viewmodels import PostLoveSerializer, OrderSerializer
from orders.manager import OrderManager
from orders.models import OrderModel
from accounts.views import check_is_uuid


# @csrf_exempt
# @api_view(['POST'])
# def submit_lovecontent(request):
#     """
#     发布誓言
#     :param request:
#     :return:
#     """
#     if request.method == 'POST':
#         serializer = PostLoveSerializer(data=request.data)
#         if serializer.is_valid():
#             ordermodel, jsdata = OrderManager.create_order(serializer)
#             if ordermodel and jsdata:
#                 return JsonResponse(jsdata)
#             else:
#                 return JsonResponse({"msg": "创建订单失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             return JsonResponse({"msg": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         return JsonResponse({"msg": "only for post"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class OrderList(APIView):
    def get(self, request, format=None):
        size = request.GET.get('size', default=20)
        index = request.GET.get('index', default=1)
        paginator = Paginator(OrderModel.objects.all(), size)
        datas = paginator.get_page(index)
        serializer = OrderSerializer(datas, many=True)
        return Response(serializer.data)


class OrderDetail(APIView):
    def get_object(self, pk):
        user = get_object_or_404(OrderModel, id=pk)
        return user

    @check_is_uuid()
    def get(self, request, pk, format=None):
        order = self.get_object(pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @csrf_exempt
    def post(self, request, format=None):
        serializer = PostLoveSerializer(data=request.data)
        if serializer.is_valid():
            ordermodel, jsdata = OrderManager.create_order(serializer)
            if ordermodel and jsdata:
                return JsonResponse(jsdata)
            else:
                return JsonResponse({"msg": "创建订单失败"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#
# def order_list(request):
#     size = request.GET.get('size', default=20)
#     index = request.GET.get('index', default=1)
#     paginator = Paginator(OrderModel.objects.all(), size)
#     datas = paginator.get_page(index)
