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
from App.views import (
    IndexView,
    ViewDataRepositoryView,
    SignInView,
    DashboardView,
    DatasetGroup,
    DatasetUpdateGroup,
    DatasetDeleteGroup,
    AdminAccountSettings,
    AdminAccountUpdate,
    LogoutView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("view-repository", ViewDataRepositoryView.as_view(), name="view_repo"),
    # Admin related urls
    path("admin-login", SignInView.as_view(), name="sign-in"),
    path("dashboard/", DashboardView.as_view(), name="dashboard-page"),
    path("dataset-groups/", DatasetGroup.as_view(), name="dataset-groups"),
    path(
        "dataset-update-group/<int:pk>",
        DatasetUpdateGroup.as_view(),
        name="dataset-update-group",
    ),
    path(
        "dataset-delete-group/<int:pk>",
        DatasetDeleteGroup.as_view(),
        name="dataset-delete-group",
    ),
    path("account-settings/", AdminAccountSettings.as_view(), name="account-settings"),
    path('admin-account-update/', AdminAccountUpdate.as_view(), name = 'admin-account-update'),
    path("logout/", LogoutView.as_view(), name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
