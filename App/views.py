# Tigray data repository
# developed by: tesfahiwet truneh
# date: 2024, 2025
# location: Mekelle, Tigray, Ethiopia
# TechStack Used: Django, Bootstrap4 Template and Plotly for graph design

# Standard Library Imports

import os
import stripe
import random
import logging
import string
from zipfile import ZipFile
from django.http.response import HttpResponse as HttpResponse
import plotly
import plotly.graph_objects as go
from folium import Map, Marker, Icon
from folium.plugins import Fullscreen

# Third-Party Imports
from django.views import View
from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count
from django.conf import settings
from .forms import ArticleForm
from django.core.paginator import Paginator
from django.views.generic.edit import UpdateView
from django.utils.safestring import mark_safe
from django.core.mail import send_mail
from django.db.models.functions import ExtractYear
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest, HttpResponseRedirect
from django.template.loader import render_to_string
from django.shortcuts import redirect, render, get_object_or_404, reverse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password

# Local Application Imports
from .models import RepositoryGroup, RepositoryItem, AdminPic, InitiativesModel, Blog

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blog_articles"] = Blog.objects.all()[:3]
        repository_groups = RepositoryGroup.objects.prefetch_related("repositories")
        context["repository_groups"] = []

        for group in repository_groups:
            group_data = {
                "name": group.name,
                "repositories": [],
            }
            for repository in group.repositories.all():
                file_data = {
                    "name": os.path.basename(repository.file.name),
                    "is_zip": repository.file.name.endswith(".zip"),
                    "download_url": repository.file.url,
                    "contents": "",
                }
                if file_data["is_zip"]:
                    zip_path = repository.file.path
                    with ZipFile(zip_path, "r") as zip_file:
                        file_tree = self._build_zip_tree(zip_file)
                        file_data["contents"] = self._render_zip_tree(file_tree)
                group_data["repositories"].append(file_data)
            context["repository_groups"].append(group_data)

        return context

    def _build_zip_tree(self, zip_file):
        tree = {}
        for file in zip_file.namelist():
            parts = file.split("/")
            node = tree
            for part in parts:
                if part not in node:
                    node[part] = {}
                node = node[part]
        return tree

    def _render_zip_tree(self, tree, level=0):
        html = f'<ul class="list-unstyled" style="margin-left: {level * 20}px;">'
        for name, subitems in tree.items():
            if subitems:  # Folder
                folder_id = f"folder-{level}-{hash(name)}"
                html += f"""
                <li class="ps-4">
                    <i class="expandable-table-caret fas fa-caret-right fa-fw"></i>
                    <i class="fa fa-folder me-2" style="color: #428bca;"></i> 
                    <a href="#" data-bs-toggle="collapse" data-bs-target="#{folder_id}" aria-expanded="false">{name}</a>
                    <div id="{folder_id}" class="collapse">
                        {self._render_zip_tree(subitems, level + 1)}
                    </div>
                </li>
                """
            else:  # File
                html += f"""
                <li class="ps-5">
                    <i class="fa fa-file me-2"></i> {name}
                </li>
                """
        html += "</ul>"
        return mark_safe(html)
    
class WhyTdr(TemplateView):
    template_name = "why_tdr.html"

class BlogView(TemplateView):
    template_name = "blog.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_articles = Blog.objects.all()
        paginator = Paginator(all_articles, 3)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
        return context
    
class ViewBlog(TemplateView):
    template_name = "view_blog.html"

    def get(self, request, pk, *args, **kwargs):
        fetched_article = get_object_or_404(Blog, slug=pk)
        context = {"article": fetched_article}
        return render(request, self.template_name, context)

class InitiativesView(TemplateView):
    template_name = "initiatives.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        initiatives = InitiativesModel.objects.all()

        unique_origins = InitiativesModel.objects.values_list(
            "InitiativeOrigin", flat=True
        ).distinct()
        context["unique_origins"] = list(set(unique_origins))

        unique_type = InitiativesModel.objects.values_list(
            "InitiativeType", flat=True
        ).distinct()
        context["unique_type"] = list(set(unique_type))

        unique_area_focus = InitiativesModel.objects.values_list(
            "AriaOfFocus", flat=True
        ).distinct()
        context["unique_area_focus"] = list(set(unique_area_focus))

        unique_foundation_year = InitiativesModel.objects.annotate(
            foundation_year=ExtractYear('FoundationYear')
        ).values_list('foundation_year', flat=True).distinct()
        context["unique_foundation_year"] = list(set(unique_foundation_year))

        foundation_year_data = {}
        origin_data = {}
        initiative_type_data = {}

        for initiative in initiatives:
            foundation_year = initiative.FoundationYear.year
            foundation_year_data[foundation_year] = (
                foundation_year_data.get(foundation_year, 0) + 1
            )
            origin_data[initiative.InitiativeOrigin] = (
                origin_data.get(initiative.InitiativeOrigin, 0) + 1
            )
            initiative_type_data[initiative.InitiativeTypeforgraph] = (
                initiative_type_data.get(initiative.InitiativeTypeforgraph, 0) + 1
            )

        origin_coordinates = {
            'Ethiopia (Outside of Tigray)': [8.988913, 38.720441],
            'Africa': [8.572851, 18.916199],
            'North America': [37.0902, -95.7129],
            'Central/South America': [-10.649842, -57.603866],
            'Asia': [38.901695, 101.828851],
            'Europe': [51.246039, 15.631759],
            'Middle East': [29.956507, 43.444022],
            'Australia': [-25.2744, 133.7751],
        }

        origin_map = Map(location=[20, 0], zoom_start=1, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                          attr='Esri')

        Fullscreen(position='topright', title='Expand', title_cancel='Exit', force_separate_button=True).add_to(origin_map)
        for origin, lat_lon in origin_coordinates.items():
            count = origin_data.get(origin, 0)  # Default to 0 if origin is not in origin_data
            Marker(
                location=lat_lon,
                popup=f"<strong style='color: cornflowerblue'>{origin}</strong>: {count} initiatives"
            ).add_to(origin_map)

        context["origin_map"] = origin_map._repr_html_()

        doughnut_data = [
                {"label": key, "y": value} for key, value in sorted(foundation_year_data.items())
            ]
        column_data = [{"label": key, "y": value} for key, value in origin_data.items()]
        pyramid_data = [{"label": key, "y": value} for key, value in initiative_type_data.items()]

        context["diaspora_initiatives"] = initiatives
        context["doughnut_data"] = doughnut_data
        context["column_data"] = column_data
        context["pyramid_data"] = pyramid_data

        return context
    
class ManifestoView(TemplateView):
    template_name = "manifesto.html"

class ContributeView(TemplateView):
    template_name = "contribute.html"
    
class StripeCheckoutView(View):

    def get(self, request, *args, **kwargs):
        try:

            amount_in_cents = int(request.GET.get("amount", 0)) * 100

            stripe_session = stripe.checkout.Session.create(
                payment_method_types=[
                    "card",
                ],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": amount_in_cents,
                            "product_data": {
                                "name": "Tigray Data Repository",
                                "description": "The Tigray Data Repository (TDR) is an online, open-source repository of datasets documenting Tigray’s history and the experiences of the Tigray communities living in other countries. The TDR was established in May 2024 and went live in January 2025. It is an archive created to document the digital, humanitarian, socio-economic, cultural, political, educational, historical, and many other types of data related to the community, serving as a resource for education and research for the benefit of future generations. As such, it is best described by its motto: “Data for Tigray, Knowledge for Generations!”.",  
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=request.build_absolute_uri(reverse("payment-success")),
                cancel_url=request.build_absolute_uri(reverse("payment-cancel")),
                metadata={
                    "amount_paid": amount_in_cents,
                },
            )

            return redirect(stripe_session.url)

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return redirect("index")
        except Exception as e:
            logger.error(f"Error during checkout: {str(e)}")
            return redirect("index")

class PaymentSuccessView(TemplateView):
    template_name = "payment_success.html"

class PaymentCancelView(TemplateView):
    template_name = "payment_cancel.html"

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
            
            if self.request.POST.get("remember_me"):
                self.request.session.set_expiry(1209600)
            else:
                self.request.session.set_expiry(0)
                
            login(request, user)
            return HttpResponseRedirect(self.success_url)
        else:
            messages.error(request, "Invalid username or password")
            return render(request, self.template_name)
        
# Password reset views
class ForgotPasswordView(TemplateView):
    template_name = "admin_page/forgot_password.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/dashboard.html"
    login_url = "sign-in"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        top_groups = RepositoryGroup.objects.annotate(
            num_items=Count("repositories")
        ).order_by("-num_items")[:4]

        context = super().get_context_data(**kwargs)
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
        FoundationYear = request.POST.get("FoundationYear")
        InitiativeType = request.POST.get("InitiativeType")
        InitiativeOrigin = request.POST.get("InitiativeOrigin")
        AriaOfFocus = request.POST.get("AriaOfFocus")
        OfficialLink = request.POST.get("OfficialLink")

        InitiativesModel.objects.create(
            InitiativeName=InitiativeName,
            FoundationYear=FoundationYear,
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

# Blog Article Section Views
class WriteArticle(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/write_article.html"
    login_url = "sign_in"
    redirect_field_name = "next"
    
    def post(self, request, *args, **kwargs):
        
        AnalysisCreate = Blog.objects.create(ArticleTitle = request.POST["ArticleTitle"],
                                             content = request.POST["content"])
        
        AnalysisCreate.save()
        
        messages.success(request, f"Analysis article published successfully!")
        
        return redirect("write-article")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ArticleForm()
        return context
    
class ArticleManagement(LoginRequiredMixin, TemplateView):
    template_name = "admin_page/manage_analysis.html"
    login_url = "sign-in"
    redirect_field_name = "next"
    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        
        context["FetchedArticles"] = Blog.objects.all()
        
        return context
    
class ArticleUpdate(LoginRequiredMixin, UpdateView):
    model = Blog
    form_class = ArticleForm
    template_name = "admin_page/update-article.html"
    success_url = reverse_lazy('article-management')

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        return get_object_or_404(Blog, slug=slug)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=self.object)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Article updated successfully!")
                return redirect(self.success_url)
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Invalid form data. Please correct the errors below.")

        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.get_object())
        return context
    
class ArticleDelete(LoginRequiredMixin, TemplateView):

    def post(self, request, pk):
        FetchedArticle = get_object_or_404(Blog, pk=pk)
        FetchedArticle.delete()

        messages.success(request, "Article deleted successfully!")

        return redirect("article-management")

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
