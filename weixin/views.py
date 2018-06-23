from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect

import requests
import json

from rest_framework.response import Response
from rest_framework import status

from xiaobiaobai.utils import logger, ResponseCode
from orders.models import OrderModel
from weixin.weixinapi.wxlogin import WeixinLogin
from weixin.weixinapi.wxutils import get_wx_config, WeixinLoginError

from accounts.models import WxUserModel
from weixin.manager import WxManager

from weixin.manager import pay_client

wxconfig = get_wx_config()

wxlogin = WeixinLogin(wxconfig)


def wxuser_login(request):
    if request.GET.get('code', default=''):
        try:
            code = request.GET.get('code')
            token_response = wxlogin.access_token(code)
            logger.info(token_response)
            openid, userid, target_userid = WxManager.wxlogin_with_createuser(token_response)
            return JsonResponse(
                {'code': 200, "msg": 'ok', 'openid': openid, 'userid': userid, 'target_userid': target_userid})
        except WeixinLoginError as e:
            logger.error(e)
            return JsonResponse({'openid': '', "msg": str(e), "code": 500},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'openid': '', "msg": str(e), "code": 500},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        uri = wxlogin.authorize()
        logger.info(uri)
        return HttpResponseRedirect(uri)


def wx_pay_callback(request):
    if request.method == "POST":
        body = pay_client.to_dict(request.body)
        if pay_client.check(body):
            logger.info("收到支付回调，data：{data}".format(data=body))
            try:
                result = WxManager.wx_pay_callback(body)
                if result:
                    resultxml = pay_client.to_xml(dict(return_code="SUCCESS", return_msg="OK"));
                    return Response(resultxml)
            except OrderModel.DoesNotExist:
                resultxml = pay_client.to_xml(dict(return_code="Failed", return_msg="订单不存在"));
                return Response(resultxml, status=status.HTTP_404_NOT_FOUND)
        else:
            resultxml = pay_client.to_xml(dict(return_code="Failed", return_msg="签名错误"));
            return Response(resultxml, status=status.HTTP_403_FORBIDDEN)


def wx_sign(request):
    if request.method == 'GET':
        url = request.GET.get('url')
        data = WxManager.create_wxconfig_sign(url)
        return JsonResponse(data)
    else:
        return Response('非法调用', status=status.HTTP_400_BAD_REQUEST)
