"""
URL configuration for tigray_data_repo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from App.views import (
    # User page url map
    IndexView,
    WhyTdr,
    BlogView,
    ViewBlog,
    InitiativesView,
    ManifestoView,
    ContributeView,
    SignInView,
    StripeCheckoutView,
    PaymentSuccessView,
    PaymentCancelView,
    # Reset passsword URL Map
    ForgotPasswordView,
    # Admin Dashboard URL Map
    DashboardView,
    # Dataset Group URL Maps
    DatasetGroup,
    DatasetUpdateGroup,
    DatasetDeleteGroup,
    # Dataset Items Url Maps
    DatasetAddItem,
    DatasetItemUpdate,
    DatasetItemDelete,
    # Initiatives URL Map
    InitiativesAdd,
    DisplayInitiatives,
    InitiativeItemUpdate,
    InitiativeDelete,
    # User Admin Management
    AdminManagement,
    RemoveAdminAccount,
    # Blog articles URL Map
    WriteArticle,
    ArticleManagement,
    ArticleUpdate,
    ArticleDelete,
    # Admin's Account Settings URL Maps
    AdminAccountSettings,
    AdminAccountUpdate,
    AdminUpdatePassword,
    # Logout Session URL Map
    LogoutView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("why-tdr/", WhyTdr.as_view(), name = "why-tdr"),
    path("blog/", BlogView.as_view(), name="blog-view"),
    path("view-blog/<int:pk>", ViewBlog.as_view(), name = "view-blog"),
    path("initiatives/", InitiativesView.as_view(), name="initiatives"),
    path("manifesto/", ManifestoView.as_view(), name = "manifesto-view"),
    path("contribute/", ContributeView.as_view(), name = "contribute-view"),
    path("stripe-checkout/", StripeCheckoutView.as_view(), name = "stripe-checkout"),
    path("payment-success/", PaymentSuccessView.as_view(), name = "payment-success"),
    path("payment-cancel/", PaymentCancelView.as_view(), name = "payment-cancel"),
    # Admin Dashboard URL Maps
    path("admin-login/", SignInView.as_view(), name="sign-in"),
    # Reset password URL Maps
    path("forgot-password/", ForgotPasswordView.as_view(), name = "forgot-password"),
    # Dashboard URL Maps
    path("dashboard/", DashboardView.as_view(), name="dashboard-page"),
    # Dataset Groups URL Maps
    path("dataset-groups/", DatasetGroup.as_view(), name="dataset-groups"),
    path("dataset-update-group/<int:pk>", DatasetUpdateGroup.as_view(), name="dataset-update-group"),
    path("dataset-delete-group/<int:pk>", DatasetDeleteGroup.as_view(), name="dataset-delete-group"),
    # Dataset Items URL Maps
    path("add-dataset-item/", DatasetAddItem.as_view(), name = 'add-dataset-item'),
    path("dataset-update-item/<int:pk>", DatasetItemUpdate.as_view(), name = "dataset-update-item"),
    path("dataset-delete-item/<int:pk>", DatasetItemDelete.as_view(), name = "dataset-delete-item"),
    # Initiatives Management
    path("add-initiative/", InitiativesAdd.as_view(), name = "add-initiative"),
    path("display-initiatives/", DisplayInitiatives.as_view(), name = "display-initiatives"),
    path("update-initiatives/<int:pk>", InitiativeItemUpdate.as_view(), name = "update-initiatives"),
    path("delete-initiatives/<int:pk>", InitiativeDelete.as_view(), name = "delete-initiatives"),
    # Blog Articles Management
    path("write-analysis/", WriteArticle.as_view() ,name = "write-article"),
    path("analysis-management/", ArticleManagement.as_view() ,name = "article-management"),
    path("update-article/<int:pk>", ArticleUpdate.as_view(), name = "update-article"),
    path("delete-article/<int:pk>", ArticleDelete.as_view(), name = "delete-article"),
    # User Admin Account Management
    path("admin-management/", AdminManagement.as_view(), name = "admin-management"),
    path("remove-admin-account/<int:pk>", RemoveAdminAccount.as_view(), name = "remove-admin-account"),
    # Admin's Account Settings URL Maps
    path("account-settings/", AdminAccountSettings.as_view(), name="account-settings"),
    path('admin-account-update/', AdminAccountUpdate.as_view(), name = 'admin-account-update'),
    path('admin-password-update/', AdminUpdatePassword.as_view(), name = 'admin-password-update'),
    # url pattern for password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='admin_page/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='admin_page/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='admin_page/password_reset_complete.html'), name='password_reset_complete'),
    # Logout Session URL Map
    path("logout/", LogoutView.as_view(), name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
