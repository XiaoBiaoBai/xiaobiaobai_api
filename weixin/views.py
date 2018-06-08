from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.timezone import now

import requests
import json

from xiaobiaobai.utils import logger, ResponseCode

from weixin.weixinapi.wxlogin import WeixinLogin
from weixin.weixinapi.wxutils import get_wx_config, WeixinLoginError

from accounts.models import WxUserModel
from weixin.wxmanager import WxManager

wxconfig = get_wx_config()

wxlogin = WeixinLogin(wxconfig)


def get_wxuser_openid(request):
    if request.GET.get('code', default=''):
        try:
            code = request.GET.get('code')
            token_response = wxlogin.access_token(code)
            logger.info(token_response)
            openid, userid = WxManager.wxlogin_with_createuser(token_response)
            return JsonResponse({'code': ResponseCode.SUCCESS, 'openid': openid, 'userid': userid})
        except WeixinLoginError as e:
            logger.error(e)
            return JsonResponse({'code': ResponseCode.WX_ERROR, 'openid': ''})
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': ResponseCode.ERROR, 'openid': ''})

    else:
        uri = wxlogin.authorize()
        return HttpResponseRedirect(uri)
