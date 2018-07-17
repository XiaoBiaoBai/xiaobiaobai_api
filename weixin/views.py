from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect, csrf_exempt

import requests
import json
from urllib.parse import urlparse, urlunparse

from rest_framework.response import Response
from rest_framework import status

from xiaobiaobai.utils import ResponseCode, get_systemconfigs
from orders.models import OrderModel
from weixin.weixinapi.wxlogin import WeixinLogin
from weixin.weixinapi.wxutils import get_wx_config, WeixinLoginError

from accounts.models import WxUserModel
from weixin.manager import WxManager
from weixin.manager import get_wx_pay_client

import logging

logger = logging.getLogger(__name__)


def get_wx_login_client():
    wxconfig = get_wx_config()
    wxlogin = WeixinLogin(wxconfig)
    return wxlogin


def wxuser_redirectlogin(request):
    wxlogin = get_wx_login_client()
    if request.GET.get('code', default=''):
        try:
            code = request.GET.get('code')
            token_response = wxlogin.access_token(code)
            logger.info(token_response)
            openid, userid = WxManager.wxlogin_with_createuser(token_response)
            config = get_systemconfigs()
            url = request.GET.get('state', default=config.default_index_url)
            p = urlparse(url)
            if p.query:
                url += '&userid=' + str(userid)
            else:
                url += '?userid=' + str(userid)
            logger.info(url)
            return HttpResponseRedirect(url)
        except WeixinLoginError as e:

            sysconfig = get_systemconfigs()
            logger.error(e)
            return HttpResponseRedirect(sysconfig.default_index_url)
        except Exception as e:
            logger.error(e)
            sysconfig = get_systemconfigs()
            logger.error(e)
            return HttpResponseRedirect(sysconfig.default_index_url)
    else:
        redirecturl = request.GET.get('redirecturl')
        uri = wxlogin.authorize(state=redirecturl)
        logger.info(uri)
        return HttpResponseRedirect(uri)


def wxuser_login(request):
    wxlogin = get_wx_login_client()
    if request.GET.get('code', default=''):
        try:
            code = request.GET.get('code')
            token_response = wxlogin.access_token(code)
            logger.info(token_response)
            openid, userid = WxManager.wxlogin_with_createuser(token_response)
            return JsonResponse(
                {'code': 200, "msg": 'ok', 'openid': openid, 'userid': userid})
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


@csrf_exempt
def wx_pay_callback(request):
    pay_client = get_wx_pay_client()
    if request.method == "POST":
        body = pay_client.to_dict(request.body)
        if pay_client.check(body):
            logger.info("收到支付回调，data：{data}".format(data=body))
            try:
                result = WxManager.wx_pay_callback(body)
                if result:
                    resultxml = pay_client.to_xml(dict(return_code="SUCCESS", return_msg="OK"));
                    logger.info(resultxml)
                    return HttpResponse(resultxml)
            except OrderModel.DoesNotExist:
                resultxml = pay_client.to_xml(dict(return_code="Failed", return_msg="订单不存在"));
                return HttpResponse(resultxml, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(e)

        else:
            resultxml = pay_client.to_xml(dict(return_code="Failed", return_msg="签名错误"));
            return HttpResponse(resultxml, status=status.HTTP_403_FORBIDDEN)


def wx_sign(request):
    if request.method == 'GET':
        url = request.GET.get('url')
        type = request.GET.get('type', default='pay')
        data = WxManager.create_wxconfig_sign(url, type)
        data['type'] = type
        return JsonResponse(data)
    else:
        return JsonResponse({'msg': '非法调用', 'code': 400}, status=status.HTTP_400_BAD_REQUEST)
