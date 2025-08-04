from django.contrib import admin
from django import forms
from django.contrib.contenttypes.models import ContentType

from .models import RepositoryGroup
from .models import RepositoryItem
from .models import DownloadCounter
from .models import InitiativesModel
from .models import Blog
from .models import SubFolder
from django.contrib.auth.models import Group
from django_summernote.models import Attachment
from django_summernote.admin import SummernoteModelAdmin

from django.contrib.admin import AdminSite

# Change admin site title and header/Customize admin site
admin.site.site_header = "Tigray Data Repository"
admin.site.site_title = "Tigray Data Repository Admin"
admin.site.index_title = "Welcome to the Tigray Data Repository"
admin.site.unregister(Group)
admin.site.unregister(Attachment)

# Main folder custom admin
class RepositoryGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ('name',)
admin.site.register(RepositoryGroup, RepositoryGroupAdmin)

# Main sub-folder custom admin
class RepositorySubFolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ('name',)
admin.site.register(SubFolder, RepositorySubFolderAdmin)

# Main initiatives custom admin
class InitiativesModelAdmin(admin.ModelAdmin):
    list_display = ('InitiativeName', 'InitiativeType', 'InitiativeOrigin', 'FoundationYear')
    ordering = ('InitiativeName',)
admin.site.register(InitiativesModel, InitiativesModelAdmin)

# Main initiatives custom admin
class BlogAdmin(SummernoteModelAdmin):
    list_display = ('ArticleTitle', 'article_type', 'DatePublished')
    summernote_fields = ('content',)
    ordering = ('-DatePublished',)
    exclude = ('slug', 'DatePublished')

admin.site.register(Blog, BlogAdmin)


# tigray_data_repo/App/admin.py
class RepositoryItemAdminForm(forms.ModelForm):
    parent_choice = forms.ChoiceField(label="Folder name")

    class Meta:
        model = RepositoryItem
        fields = ['parent_choice', 'file', "uploaded_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        group_choices = [
            (f"RepositoryGroup-{g.id}", f"Repository: {g.name}") for g in RepositoryGroup.objects.all()
        ]
        subfolder_choices = [
            (f"SubFolder-{s.id}", f"Folder: {s.name}") for s in SubFolder.objects.all()
        ]
        self.fields['parent_choice'].choices = group_choices + subfolder_choices

        # Set initial value if editing
        if self.instance.pk:
            ct = self.instance.content_type
            oid = self.instance.object_id
            if ct and oid:
                model_name = ct.model_class().__name__
                self.fields['parent_choice'].initial = f"{model_name}-{oid}"

    def clean(self):
        cleaned_data = super().clean()
        parent_choice = cleaned_data.get('parent_choice')
        if parent_choice:
            model_name, obj_id = parent_choice.split('-')
            if model_name == "RepositoryGroup":
                model = RepositoryGroup
            else:
                model = SubFolder
            content_type = ContentType.objects.get_for_model(model)
            self.instance.content_type = content_type
            self.instance.object_id = obj_id
        return cleaned_data
    
class RepositoryItemAdmin(admin.ModelAdmin):
    form = RepositoryItemAdminForm
    list_display = ['uploaded_at', 'parent', 'file',]

admin.site.register(RepositoryItem, RepositoryItemAdmin)