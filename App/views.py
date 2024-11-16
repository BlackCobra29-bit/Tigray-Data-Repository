# Standard Library Imports
import json
import os
import zipfile

# Third-Party Imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
import plotly
import plotly.graph_objects as go
# Local Application Imports
from .models import Repository, RepositoryGroup


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        repo = Repository.objects.first()

        if repo and repo.zip_file:
            zip_path = os.path.join(settings.MEDIA_ROOT, repo.zip_file.name)
            context['files'] = self.get_files_from_zip(zip_path)
            context['repo'] = repo

        return context

    def get_files_from_zip(self, zip_path):
        file_names = []
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get all file names from the zip
            file_names = zip_ref.namelist()

        # Filter out directories (those with a trailing slash or without a file extension)
        file_hierarchy = {
            'root': [
                os.path.basename(file_name) for file_name in file_names
                if not file_name.endswith('/') and '.' in os.path.basename(file_name)
            ]
        }

        return file_hierarchy

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

"""
Admin Views --> CBV --> Class Based Views
"""

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_page/dashboard.html'
    login_url = 'sign-in'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        data_initiative = {
            'labels': [
                'Community Service Organisation (CSO)',
                'Business/Grassroots Organisation (BGO)',
                'Humanitarian International NGO',
                'Public Media',
                'Media house',
                'Media Organization',
                'NGO',
                'Storytelling platform',
            ],
            'values': [65.2, 8.7, 8.7, 10, 20, 30, 8.7, 8.7],
        }

        fig_initiative = go.Figure(
            data=[go.Pie(labels=data_initiative['labels'], values=data_initiative['values'], hole=0.3)]
        )
        fig_initiative.update_layout(
            title="Type of Initiative or Organisation",
            title_x=0.5,
        )
        pie_chart_initiative = json.dumps(fig_initiative, cls=plotly.utils.PlotlyJSONEncoder)

        data_geo = {
            'labels': [
                'Ethiopia (Outside of Tigray)',
                'Africa',
                'North America',
                'Central/South America',
                'Asia',
                'Europe',
                'Middle East',
                'Australia',
            ],
            'values': [22.7, 22.7, 13.6, 10, 20, 40.9, 30, 40],
        }

        fig_geo = go.Figure(
            data=[go.Pie(labels=data_geo['labels'], values=data_geo['values'], hole=0.3)]
        )
        fig_geo.update_layout(
            title="Geographic Origin of the Initiative or Organisation",
            title_x=0.5,
        )
        pie_chart_geo = json.dumps(fig_geo, cls=plotly.utils.PlotlyJSONEncoder)

        context = super().get_context_data(**kwargs)
        context['pie_chart_initiative'] = pie_chart_initiative
        context['pie_chart_geo'] = pie_chart_geo
        return context


class DatasetGroup(LoginRequiredMixin, TemplateView):
    template_name = 'admin_page/dataset_groups.html'
    login_url = 'sign-in'
    redirect_field_name = 'next'
    model = RepositoryGroup

    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(**kwargs)

        context["AvailableRepositoryGroups"] = RepositoryGroup.objects.all()

        return context

    def post(self, request, *args, **kwargs):
        CreateRepositoryGroup = RepositoryGroup.objects.create(
            name = request.POST['repository_name'],
            description = request.POST['repository_description']
        )

        return JsonResponse({"success": True, "message": "Monthly amount updated successfully!"})


class AddDatasets(LoginRequiredMixin, TemplateView):
    template_name = 'add_dataset.html'
    login_url = 'sign-in'
    redirect_field_name = 'next'

class DatasetManagement(LoginRequiredMixin, TemplateView):
    template_name = 'admin_page/dataset_groups.html'
    login_url = 'sign-in'
    redirect_field_name = 'next'

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('sign-in')