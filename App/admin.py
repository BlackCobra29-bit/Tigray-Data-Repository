from django.contrib import admin
from .models import AdminPic
from .models import RepositoryGroup
from .models import Repository

admin.site.register(AdminPic)
admin.site.register(Repository)
admin.site.register(RepositoryGroup)