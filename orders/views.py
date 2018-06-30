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
from orders.viewmodels import PostLoveSerializer, OrderSerializer, BlessingSerializer
from orders.manager import OrderManager
from orders.models import OrderModel
from accounts.views import check_is_uuid
from xiaobiaobai.utils import logger, convert_to_uuid, check_words_spam


class OrderList(APIView):
    def get(self, request, format=None):
        size = request.GET.get('size', default=20)
        index = request.GET.get('index', default=1)
        ordertype = request.GET.get('ordertype', default=1)
        userid = request.GET.get('userid')
        if ordertype == 1:
            queryset = OrderModel.objects.order_by('created_time').all()
        else:
            from django.db.models import Count
            queryset = OrderModel.objects.annotate(blesscounts=Count('blessingmodel')).order_by('-blesscounts').all()

        paginator = Paginator(queryset, size)
        datas = paginator.get_page(index)
        if userid and convert_to_uuid(userid):
            for d in datas:
                if not hasattr(d, 'queryuserid'):
                    setattr(d, 'queryuserid', userid)

        serializer = OrderSerializer(datas, many=True)
        confessionwall_count = OrderManager.get_confessionwall_counts()
        return Response({
            "code": 200,
            "data": {
                "orders": serializer.data,
                "confessionwall_count": confessionwall_count
            },
        }, status=status.HTTP_200_OK)

    @csrf_exempt
    def post(self, request, format=None):
        serializer = PostLoveSerializer(data=request.data)
        if serializer.is_valid():
            if not check_words_spam(serializer.data['order_content']):
                return Response({
                    "code": 403,
                    "msg": "内容违规"
                }, status=status.HTTP_403_FORBIDDEN)
            ordermodel, jsdata = OrderManager.create_order(serializer)
            if ordermodel and jsdata:
                return JsonResponse({
                    "code": 200,
                    "data":
                        {
                            'jsdata': jsdata,
                            'orderid': ordermodel.id
                        }
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"msg": "创建订单失败", "code": 500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({
            'code': 400,
            'msg': ','.join(serializer.errors) + '请求参数不正确'
        }, status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(APIView):
    def get_object(self, pk):
        user = get_object_or_404(OrderModel, id=pk)
        return user

    @check_is_uuid()
    def get(self, request, pk, format=None):
        order = self.get_object(pk)
        serializer = OrderSerializer(order)
        confessionwall_count = OrderManager.get_confessionwall_counts()
        return Response({
            "code": 200,
            "data": {
                "order": serializer.data,
                "confessionwall_count": confessionwall_count
            },
        }, status=status.HTTP_200_OK)


class BlessingDetail(APIView):
    def post(self, request, format=None):
        serializer = BlessingSerializer(data=request.data)
        if serializer.is_valid():
            OrderManager.create_blessing_order(serializer)
            return Response({
                'code': 200,
                'msg': 'ok'
            }, status=status.HTTP_201_CREATED)
        logger.info(serializer.errors)
        return Response({
            'code': 400,
            'msg': ','.join(serializer.errors) + '请求参数不正确'
        }, status=status.HTTP_400_BAD_REQUEST)
