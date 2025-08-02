from django import forms
from .models import Blog
from django_summernote.widgets import SummernoteWidget

class ArticleForm(forms.ModelForm):
    ARTICLE_TYPES = [
        ('articles', 'Articles'),
        ('journals', 'Journals'),
        ('special_issues', 'Special Issues'),
    ]

    article_type = forms.ChoiceField(
        choices=ARTICLE_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Blog
        fields = ['ArticleTitle', 'content', 'article_type']
        widgets = {
            'ArticleTitle': forms.TextInput(
                attrs={
                    'class': 'form-control position-relative',
                    'placeholder': 'Article title',
                    'data-parsley-trigger': 'change',
                    'required': 'required',
                    'id': 'title-icon'
                }
            ),
            'content': SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ArticleTitle'].label = 'Title'
        self.fields['content'].label = 'Content'
        self.fields['article_type'].label = 'Article Type'