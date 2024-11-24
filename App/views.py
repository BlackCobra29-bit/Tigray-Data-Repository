# Standard Library Imports
import json
import os
import random
import string
import plotly
import plotly.graph_objects as go

# Third-Party Imports
from django.views import View
from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.core.mail import send_mail
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password

# Local Application Imports
from .models import RepositoryGroup, RepositoryItem, AdminPic, InitiativesModel


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["repository_groups"] = RepositoryGroup.objects.prefetch_related(
            "repositories"
        )

        return context


class InitiativesView(TemplateView):
    template_name = "initiatives.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        initiatives = InitiativesModel.objects.all()

        # Data dictionaries
        foundation_year_data = {}
        origin_data = {}
        focus_data = {}
        initiative_type_data = {}

        for initiative in initiatives:
            foundation_year_data[initiative.FoundationYear] = foundation_year_data.get(initiative.FoundationYear, 0) + 1
            origin_data[initiative.InitiativeOrigin] = origin_data.get(initiative.InitiativeOrigin, 0) + 1
            focus_data[initiative.AriaOfFocus] = focus_data.get(initiative.AriaOfFocus, 0) + 1
            initiative_type_data[initiative.InitiativeType] = initiative_type_data.get(initiative.InitiativeType, 0) + 1

        # Convert dictionaries to CanvasJS-compatible data points
        doughnut_data = [{"label": key, "y": value} for key, value in foundation_year_data.items()]
        pie_data = [{"label": key, "y": value} for key, value in focus_data.items()]
        column_data = [{"label": key, "y": value} for key, value in origin_data.items()]
        pyramid_data = [{"label": key, "y": value} for key, value in initiative_type_data.items()]

        # Pass data to context
        context["diaspora_initiatives"] = initiatives
        context["doughnut_data"] = doughnut_data
        context["pie_data"] = pie_data
        context["column_data"] = column_data
        context["pyramid_data"] = pyramid_data

        return context

"""
Admin Views --> CBV --> Class Based Views
"""


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


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/dashboard.html"
    login_url = "sign-in"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        top_groups = RepositoryGroup.objects.annotate(
            num_items=Count("repositories")
        ).order_by("-num_items")[:4]

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

        fig_initiative.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.7,
                xanchor="center",
                x=0.5,
                itemwidth=50,
                traceorder="normal",
                font=dict(size=12),
                bgcolor="rgba(255, 255, 255, 0.7)",
            ),
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

        fig_geo.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.7,
                xanchor="center",
                x=0.5,
                itemwidth=50,
                traceorder="normal",
                font=dict(size=12),
                bgcolor="rgba(255, 255, 255, 0.7)",
            ),
        )

        pie_chart_geo = json.dumps(fig_geo, cls=plotly.utils.PlotlyJSONEncoder)

        context = super().get_context_data(**kwargs)
        context["pie_chart_initiative"] = pie_chart_initiative
        context["pie_chart_geo"] = pie_chart_geo
        context["top_groups"] = top_groups
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
            item.repository = get_object_or_404(
                RepositoryGroup, id=request.POST["ItemGroup"]
            )

        if "UpdateRepositoryName" in request.POST:
            item.title = request.POST["UpdateRepositoryName"]

        if "ItemFile" in request.FILES:
            item.file = request.FILES["ItemFile"]

        item.save()

        messages.success(
            request, f"Repository item '{item.title}' updated successfully!"
        )

        return redirect("add-dataset-item")


class DatasetItemDelete(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/dataset_items.html"
    login_url = "sign-in"
    redirect_field_name = "next"

    def post(self, request, *args, **kwargs):

        item_id = kwargs.get("pk")

        item = get_object_or_404(RepositoryItem, id=item_id)

        item_file_name = os.path.basename(item.file.name)

        item.delete()

        messages.success(
            request, f"Repository item '{item_file_name}' deleted successfully!"
        )

        return redirect("add-dataset-item")


# Diaspora Initiatives and organizations management
class InitiativesAdd(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/add_initiatives.html"
    login_url = "sign-in"
    redirect_field_name = "next"

    def post(self, request, *args, **kwargs):
        InitiativeName = request.POST.get("InitiativeName")
        FoundationYear = request.POST.get("FoundationYear")[:4]
        InitiativeType = request.POST.get("InitiativeType")
        InitiativeOrigin = request.POST.get("InitiativeOrigin")
        AriaOfFocus = request.POST.get("AriaOfFocus")
        OfficialLink = request.POST.get("OfficialLink")

        InitiativesModel.objects.create(
            InitiativeName=InitiativeName,
            FoundationYear=int(FoundationYear),
            InitiativeType=InitiativeType,
            InitiativeOrigin=InitiativeOrigin,
            AriaOfFocus=AriaOfFocus,
            OfficialLink=OfficialLink,
        )

        messages.success(request, "Initiative has been successfully added!")
        return self.render_to_response({"success": True})
    
class DisplayInitiatives(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/display_initiatives.html"
    login_url = "sign-in"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["diaspora_initiatives"] = InitiativesModel.objects.all()

        return context
    
class InitiativeItemUpdate(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/display_initiatives.html"
    login_url = "sign-in"
    redirect_field_name = "next"

    def post(self, request, pk):
        initiative = get_object_or_404(InitiativesModel, pk=pk)
        initiative.InitiativeName = request.POST.get("InitiativeName")
        initiative.FoundationYear = request.POST.get("FoundationYear")
        initiative.InitiativeType = request.POST.get("InitiativeType")
        initiative.InitiativeOrigin = request.POST.get("InitiativeOrigin")
        initiative.AriaOfFocus = request.POST.get("AriaOfFocus")
        initiative.OfficialLink = request.POST.get("OfficialLink")
        initiative.save()

        messages.success(request, "Initiative Updated successfully!")

        return redirect("display-initiatives")


class InitiativeDelete(LoginRequiredMixin, TemplateView):

    def post(self, request, pk):
        FetchedRepository = get_object_or_404(InitiativesModel, pk=pk)
        FetchedRepository.delete()

        messages.success(request, "Initiative removed successfully!")

        return redirect("display-initiatives")


# User Admin Management
class AdminManagement(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/admin_management.html"
    login_url = "sign-in"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["UserAdminList"] = User.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        while True:
            username = "admin_" + "".join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )
            if not User.objects.filter(username=username).exists():
                break

        while True:
            password = "".join(
                random.choices(
                    string.ascii_letters + string.digits + string.punctuation, k=12
                )
            )

            if not User.objects.filter(password=make_password(password)).exists():
                break

        first_name = request.POST.get("FirstName")
        last_name = request.POST.get("LastName")
        email = request.POST.get("UserEmail")
        profile_pic = request.FILES.get("UserProfile")

        if not email:
            messages.error(request, "Email is required")
            return render(request, self.template_name)

        if User.objects.filter(email=email).exists():
            messages.error(
                request, "Email is already taken. Please choose another one."
            )

            return render(request, self.template_name)

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        admin_pic = AdminPic(user=user, profile_pic=profile_pic)
        admin_pic.save()

        subject = "New Admin Account Created"
        message = render_to_string(
            "admin_page/admin_email_template.html",
            {
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "password": password,
            },
        )

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            html_message=message,
        )

        messages.success(request, "Admin account created successfully!")

        return redirect("admin-management")


class RemoveAdminAccount(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/admin_management.html"
    login_url = "sign-in"
    redirect_field_name = "next"

    def post(self, request, *args, **kwargs):
        admin_id = kwargs.get("pk")

        try:
            admin = User.objects.get(id=admin_id)

            if admin.is_superuser:
                messages.error(request, "You cannot remove a superadmin.")
            else:
                admin.delete()
                messages.success(request, "Admin removed successfully.")
        except User.DoesNotExist:
            messages.error(request, "Admin not found.")

        return redirect("admin-management")


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
