from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.models import UserModel, WxUserModel


class OrderView(APIView):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        pass
