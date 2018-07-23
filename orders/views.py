from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.http.response import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework.decorators import api_view

from accounts.models import UserModel, WxUserModel
from orders.viewmodels import PostLoveSerializer, OrderSerializer, BlessingSerializer, ConfessionWallSerializer
from orders.manager import OrderManager
from orders.models import OrderModel
from accounts.views import check_is_uuid
from xiaobiaobai.utils import convert_to_uuid, check_words_spam
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import logging

logger = logging.getLogger(__name__)


class OrderList(APIView):
    def options(self, request, *args, **kwargs):
        return Response({
            'code': 403,
            'msg': '非法调用'
        }, status=status.HTTP_403_FORBIDDEN)

    def get(self, request, format=None):
        size = request.GET.get('size', default=20)
        index = request.GET.get('index', default=1)
        ordertype = request.GET.get('ordertype', default=1)
        userid = convert_to_uuid(request.GET.get('userid', default=''))

        if ordertype == "1":
            if userid:
                queryset = OrderModel.objects.filter(show_confession_wall=True) \
                    .filter(usermodel__id=userid) \
                    .filter(order_status='p') \
                    .order_by('-created_time')
            else:
                queryset = OrderModel.objects.filter(show_confession_wall=True) \
                    .filter(order_status='p') \
                    .order_by('-created_time')
        else:
            from django.db.models import Count
            if userid:
                queryset = OrderModel.objects.filter(usermodel__id=userid).filter(order_status='p').annotate(
                    blesscounts=Count('blessingmodel')).order_by('-blesscounts')

            else:
                queryset = OrderModel.objects.filter(show_confession_wall=True).filter(order_status='p').annotate(
                    blesscounts=Count('blessingmodel')).order_by('-blesscounts')

        paginator = Paginator(queryset, size)
        try:
            index = int(index)
        except:
            index = 1

        confessionwall_count = OrderManager.get_confessionwall_counts()
        if index > paginator.num_pages:
            return Response({
                "code": 200,
                "data": {
                    "orders": list(),
                    "totalcount": paginator.count,
                    "index": paginator.num_pages,
                    "confessionwall_count": confessionwall_count
                },
            }, status=status.HTTP_200_OK)
        else:
            datas = paginator.get_page(index)


            serializer = OrderSerializer(datas, many=True)

            return Response({
                "code": 200,
                "data": {
                    "orders": serializer.data,
                    "totalcount": paginator.count,
                    "index": paginator.num_pages,
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
        else:
            logger.error(serializer.errors)
            logger.error(request.data)
            return Response({
                'code': 400,
                'msg': ','.join(serializer.errors) + '请求参数不正确'
            }, status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(APIView):
    def get_object(self, pk):
        try:
            user = OrderModel.objects.get(id=pk)
            return user
        except ObjectDoesNotExist:
            raise

    def options(self, request, *args, **kwargs):
        return Response({
            'code': 403,
            'msg': '非法调用'
        }, status=status.HTTP_403_FORBIDDEN)

    @check_is_uuid()
    def get(self, request, pk, userid, format=None):
        order = None
        try:
            order = self.get_object(pk)
        except ObjectDoesNotExist:
            return Response({
                "code": 404,
                "msg": "订单不存在"
            }, status=status.HTTP_404_NOT_FOUND)

        if userid and convert_to_uuid(userid):
            if not hasattr(order, 'queryuserid'):
                setattr(order, 'queryuserid', userid)
        serializer = OrderSerializer(order)
        confessionwall_count = OrderManager.get_confessionwall_counts()
        return Response({
            "code": 200,
            "data": {
                "order": serializer.data,
                "confessionwall_count": confessionwall_count
            },
        }, status=status.HTTP_200_OK)


@csrf_exempt
def update_show_confession_wall(request):
    if request.method != 'POST':
        return JsonResponse({
            "code": 400
        }, status=status.HTTP_400_BAD_REQUEST)
    else:
        data = JSONParser().parse(request)
        serializer = ConfessionWallSerializer(data=data)
        if serializer.is_valid():
            try:
                userid = serializer.data["usermodel"]
                orderid = serializer.data["ordermodel"]
                savestatus = serializer.data["status"]
                OrderManager.update_show_confession_wall(userid, orderid, savestatus)
                return JsonResponse({
                    "code": 200,
                    "msg": "ok"
                }, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return JsonResponse({
                    "code": 404,
                    "msg": "用户或订单不存在"
                }, status=status.HTTP_404_NOT_FOUND)
            except ValueError:
                return JsonResponse({
                    "code": 403,
                    "msg": "非当前用户订单",
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            logger.error(serializer.errors)
            logger.error(request.data)
            return JsonResponse({
                'code': 400,
                'msg': ','.join(serializer.errors) + '请求参数不正确'
            }, status=status.HTTP_400_BAD_REQUEST)


class BlessingDetail(APIView):
    def get(self, request, format=None):
        return Response({
            'code': 403,
            'msg': '非法调用'
        }, status=status.HTTP_403_FORBIDDEN)

    def options(self, request, *args, **kwargs):
        return Response({
            'code': 403,
            'msg': '非法调用'
        }, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, format=None):
        serializer = BlessingSerializer(data=request.data)
        if serializer.is_valid():
            usermodel = serializer.data['usermodel']
            ordermodel = serializer.data['ordermodel']
            order = OrderModel.objects.get(id=ordermodel)
            if order.blessingmodel_set.filter(usermodel=usermodel):
                return Response({
                    'code': 400,
                    'msg': "不能重复点赞"
                })

            OrderManager.create_blessing_order(serializer)
            return Response({
                'code': 200,
                'msg': 'ok'
            }, status=status.HTTP_201_CREATED)

        else:
            logger.error(serializer.errors)
            logger.error(request.data)
            return Response({
                'code': 400,
                'msg': ','.join(serializer.errors) + '请求参数不正确'
            }, status=status.HTTP_400_BAD_REQUEST)
