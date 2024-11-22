from django.contrib import admin
from .models import AdminPic
from .models import RepositoryGroup
from .models import RepositoryItem
from .models import InitiativesModel

admin.site.register(AdminPic)
admin.site.register(RepositoryItem)
admin.site.register(RepositoryGroup)
admin.site.register(InitiativesModel)