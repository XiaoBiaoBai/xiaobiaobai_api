import datetime
import os
import uuid

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse, Http404
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.models import UserModel
from accounts.viewmodels import UserModelSerializer
from xiaobiaobai.utils import logger


# Create your views here.


@csrf_exempt
def fileupload(request):
    if request.method == 'POST':
        urls = []
        for filename in request.FILES:
            timestr = datetime.datetime.now().strftime('%Y/%m/%d')

            basepath = r'{base}/image/{timestr}'.format(timestr=timestr, base=settings.SITE_ROOT)

            if not os.path.exists(basepath):
                os.makedirs(basepath)
            ext = os.path.splitext(filename)[1]
            savefilename = str(uuid.uuid4()) + ext

            savepath = os.path.join(basepath, savefilename)
            with open(savepath, 'wb+') as wfile:
                for chunk in request.FILES[filename].chunks():
                    wfile.write(chunk)
            if ext in ['.jpg', '.png', 'jpeg']:
                from PIL import Image
                image = Image.open(savepath)
                image.save(savepath, quality=20, optimize=True)
            url = 'https://resource.lylinux.net/{timestr}/{filename}'.format(timestr=timestr, filename=savefilename)
            urls.append(url)

        return JsonResponse({
            'code': 200,
            'msg': '',
            'data': urls
        })

    else:
        return JsonResponse({
            'code': 404,
            'msg': 'only for post',
            'data': ''
        }, status=status.HTTP_404_NOT_FOUND)


def check_is_uuid():
    def wrapper(func):
        def check(*args, **kwargs):
            id = kwargs.get('pk')
            try:
                id = uuid.UUID(id)
                kwargs['pk'] = id
            except:
                raise Http404
            return func(*args, **kwargs)

        return check

    return wrapper


class UserObjectApi(APIView):
    def get_object(self, pk):
        user = get_object_or_404(UserModel, id=pk)
        return user

    @check_is_uuid()
    def get(self, request, pk, format=None):
        logger.info(pk)
        user = self.get_object(pk)
        serializer = UserModelSerializer(user)
        return Response(serializer.data)

    @check_is_uuid()
    def put(self, request, pk, format=None):
        logger.info(pk)
        user = self.get_object(pk)
        serializer = UserModelSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        user = UserModelSerializer(data=request.data)
        if user.is_valid():
            user.save()
            return Response(user.data, status=status.HTTP_201_CREATED)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
