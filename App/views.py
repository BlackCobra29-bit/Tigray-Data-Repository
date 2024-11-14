from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
import json

# Create your views here.
def Index(request):

    return render(request, 'index.html')

def ViewDataRepository(request):

    return render(request, 'render_repo.html')

"""
Admin page views [CBV --> Class Based Views]
"""
def signin(request):

    return render(request, 'admin_page/sign_in.html')

def dashboard(request):

    return render(request, 'admin_page/dashboard.html')