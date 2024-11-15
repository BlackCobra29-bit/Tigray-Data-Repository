from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages

class IndexView(TemplateView):
    template_name = 'index.html'

class ViewDataRepositoryView(TemplateView):
    template_name = 'render_repo.html'

class SignInView(TemplateView):
    template_name = 'admin_page/sign_in.html'
    success_url = reverse_lazy('dashboard-page')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(self.success_url)
        else:
            messages.error(request, "Invalid username or password")
            return render(request, self.template_name)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_page/dashboard.html'
    login_url = 'sign-in'
    redirect_field_name = 'next'

class AddDatasets(LoginRequiredMixin, TemplateView):
    template_name = 'add_dataset.html'
    login_url = 'sign-in'
    redirect_field_name = 'next'

class DatasetManagement(LoginRequiredMixin, TemplateView):
    template_name = 'dataset_management.html'
    login_url = 'dataset-management'
    redirect_field_name = 'next'

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('sign-in')