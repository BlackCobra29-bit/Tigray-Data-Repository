# Standard Library Imports
import json
import os
import zipfile

# Third-Party Imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.views import View
from django.views.generic import TemplateView
import plotly
import plotly.graph_objects as go

# Local Application Imports
from .models import RepositoryGroup, RepositoryItem


class IndexView(TemplateView):
    template_name = "index.html"


class ViewDataRepositoryView(TemplateView):
    template_name = "render_repo.html"


class SignInView(TemplateView):
    template_name = "admin_page/sign_in.html"
    success_url = reverse_lazy("dashboard-page")

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")

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
    template_name = "admin_page/dashboard.html"
    login_url = "sign-in"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        data_initiative = {
            "labels": [
                "Community Service Organisation (CSO)",
                "Business/Grassroots Organisation (BGO)",
                "Humanitarian International NGO",
                "Public Media",
                "Media house",
                "Media Organization",
                "NGO",
                "Storytelling platform",
            ],
            "values": [65.2, 8.7, 8.7, 10, 20, 30, 8.7, 8.7],
        }

        fig_initiative = go.Figure(
            data=[
                go.Pie(
                    labels=data_initiative["labels"], values=data_initiative["values"]
                )
            ]
        )
        pie_chart_initiative = json.dumps(
            fig_initiative, cls=plotly.utils.PlotlyJSONEncoder
        )

        data_geo = {
            "labels": [
                "Ethiopia (Outside of Tigray)",
                "Africa",
                "North America",
                "Central/South America",
                "Asia",
                "Europe",
                "Middle East",
                "Australia",
            ],
            "values": [22.7, 22.7, 13.6, 10, 20, 40.9, 30, 40],
        }

        fig_geo = go.Figure(
            data=[
                go.Pie(labels=data_geo["labels"], values=data_geo["values"], hole=0.2)
            ]
        )
        pie_chart_geo = json.dumps(fig_geo, cls=plotly.utils.PlotlyJSONEncoder)

        context = super().get_context_data(**kwargs)
        context["pie_chart_initiative"] = pie_chart_initiative
        context["pie_chart_geo"] = pie_chart_geo
        return context


# Dataset Group Views
class DatasetGroup(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/dataset_groups.html"
    login_url = "sign-in"
    redirect_field_name = "next"
    model = RepositoryGroup

    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(**kwargs)

        context["AvailableRepositoryGroups"] = RepositoryGroup.objects.all()

        return context

    def post(self, request, *args, **kwargs):
        CreateRepositoryGroup = RepositoryGroup.objects.create(
            name=request.POST["repository_name"],
            description=request.POST["repository_description"],
        )

        CreateRepositoryGroup.save()

        messages.success(request, "New repositrory created successfully!")

        return redirect("dataset-groups")


class DatasetManagement(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/dataset_groups.html"
    login_url = "sign-in"
    redirect_field_name = "next"


class DatasetUpdateGroup(LoginRequiredMixin, TemplateView):

    def post(self, request, pk):
        FetchedRepository = get_object_or_404(RepositoryGroup, pk=pk)
        FetchedRepository.name = request.POST["UpdateRepositoryName"]
        FetchedRepository.description = request.POST["UpdateRepositoryDescription"]
        FetchedRepository.save()

        messages.success(request, "Repository Updated successfully!")

        return redirect("dataset-groups")


class DatasetDeleteGroup(LoginRequiredMixin, TemplateView):

    def post(self, request, pk):
        FetchedRepository = get_object_or_404(RepositoryGroup, pk=pk)
        FetchedRepository.delete()

        messages.success(request, "Repository removed successfully!")

        return redirect("dataset-groups")


# Dataset Item Views
class DatasetAddItem(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/dataset_items.html"
    login_url = "sign-in"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["RepositoryGroupsList"] = RepositoryGroup.objects.all()
        context["RepositoryItemList"] = RepositoryItem.objects.all()

        return context

    def post(self, request, *args, **kwargs):

        SaveRepositoryItem = RepositoryItem.objects.create(
            repository=get_object_or_404(RepositoryGroup, id=request.POST["ItemGroup"]),
            title=request.POST["ItemTitle"],
            file=request.FILES["ItemFile"],
        )

        SaveRepositoryItem.save()

        messages.success(
            request,
            f"New file added to {get_object_or_404(RepositoryGroup, id = request.POST["ItemGroup"]).name} repository!",
        )

        return redirect("add-dataset-item")


class DatasetItemUpdate(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/dataset_items.html"
    login_url = "sign-in"
    redirect_field_name = "next"

    def post(self, request, *args, **kwargs):
        
        item_id = kwargs.get("pk")
        item = get_object_or_404(RepositoryItem, id=item_id)

        if "ItemGroup" in request.POST:
            item.repository = get_object_or_404(RepositoryGroup, id=request.POST["ItemGroup"])

        if "UpdateRepositoryName" in request.POST:
            item.title = request.POST["UpdateRepositoryName"]

        if "ItemFile" in request.FILES:
            item.file = request.FILES["ItemFile"]

        item.save()

        messages.success(request, f"Repository item '{item.title}' updated successfully!")

        return redirect("add-dataset-item")
    
class DatasetItemDelete(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/dataset_items.html"
    login_url = "sign-in"
    redirect_field_name = "next"

# Admin Account Settings Views
class AdminAccountSettings(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/account_settings.html"
    login_url = "sign-in"
    redirect_field_name = "next"


class AdminAccountUpdate(LoginRequiredMixin, TemplateView):

    def post(self, request):
        try:
            logged_in_account = request.user
            logged_in_account.first_name = request.POST.get("UpdatedFirstName")
            logged_in_account.last_name = request.POST.get("UpdatedLastName")
            logged_in_account.username = request.POST.get("UpdatedUserName")
            logged_in_account.email = request.POST.get("UpdatedEmail")
            logged_in_account.save()
            messages.success(request, "Account information updated successfully!")
        except User.DoesNotExist:
            messages.error(request, "User not found!")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect("account-settings")


class AdminUpdatePassword(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        current_password = request.POST.get("CurrentPassword")
        new_password = request.POST.get("NewPassword")
        confirm_password = request.POST.get("ConfirmNewPassword")

        if not current_password or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect("account-settings")

        if not check_password(current_password, request.user.password):
            messages.error(request, "Current password is incorrect.")
            return redirect("account-settings")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("account-settings")

        request.user.set_password(new_password)
        request.user.save()

        update_session_auth_hash(request, request.user)

        messages.success(request, "Password updated successfully.")
        return redirect("account-settings")


# Logout View
class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("sign-in")
