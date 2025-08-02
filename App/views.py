# Tigray data repository
# developed by: tesfahiwet truneh
# date: 2024, 2025
# location: Mekelle, Tigray, Ethiopia

# Standard Library Imports

import os
from django.http.response import HttpResponse as HttpResponse
from folium import Map, Marker
from folium.plugins import Fullscreen

# Third-Party Imports
from django.views import View
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.functions import ExtractYear
from django.views.generic import TemplateView
from django.shortcuts import redirect, render, get_object_or_404
# Local Application Imports
from .models import RepositoryGroup, RepositoryItem, InitiativesModel, Blog, SubFolder, DownloadCounter


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all repository groups with their subfolders
        repository_groups = RepositoryGroup.objects.prefetch_related('subfolders').all()
        
        context["repository_groups"] = []
        
        # Count variables
        total_repository_items = 0
        parent_repositories_count = repository_groups.count()
        
        for group in repository_groups:
            group_data = {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "repository_items": [],  # Items directly in parent folder
                "subfolders": []
            }
            
            # Get repository items directly in the parent folder (RepositoryGroup)
            from django.contrib.contenttypes.models import ContentType
            group_content_type = ContentType.objects.get_for_model(RepositoryGroup)
            group_repository_items = RepositoryItem.objects.filter(
                content_type=group_content_type,
                object_id=group.id
            )
            
            for item in group_repository_items:
                # Get download count for this item
                download_count = 0
                try:
                    download_counter = item.download_counter
                    download_count = download_counter.download_count
                except DownloadCounter.DoesNotExist:
                    download_count = 0
                
                file_data = {
                    "id": item.id,
                    "title": item.title,
                    "file_name": os.path.basename(item.file.name),
                    "file_url": item.file.url,
                    "uploaded_at": item.uploaded_at,
                    "file_size": item.file.size if item.file else 0,
                    "download_count": download_count,
                }
                
                group_data["repository_items"].append(file_data)
                total_repository_items += 1
            
            # Get subfolders for this group
            for subfolder in group.subfolders.all():
                subfolder_data = {
                    "id": subfolder.id,
                    "name": subfolder.name,
                    "description": subfolder.description,
                    "repository_items": []
                }
                
                # Get repository items for this subfolder using GenericForeignKey
                subfolder_content_type = ContentType.objects.get_for_model(SubFolder)
                repository_items = RepositoryItem.objects.filter(
                    content_type=subfolder_content_type,
                    object_id=subfolder.id
                )
                
                for item in repository_items:
                    # Get download count for this item
                    download_count = 0
                    try:
                        download_counter = item.download_counter
                        download_count = download_counter.download_count
                    except DownloadCounter.DoesNotExist:
                        download_count = 0
                    
                    file_data = {
                        "id": item.id,
                        "title": item.title,
                        "file_name": os.path.basename(item.file.name),
                        "file_url": item.file.url,
                        "uploaded_at": item.uploaded_at,
                        "file_size": item.file.size if item.file else 0,
                        "download_count": download_count,
                    }
                    
                    subfolder_data["repository_items"].append(file_data)
                    total_repository_items += 1
                
                group_data["subfolders"].append(subfolder_data)
            
            context["repository_groups"].append(group_data)
        
        # Add counts to context
        context["parent_repositories_count"] = parent_repositories_count
        context["total_repository_items"] = total_repository_items
        
        return context

class DownloadFileView(View):
    """View to handle file downloads and track download counts"""
    
    def get(self, request, item_id):
        # Get the repository item
        repository_item = get_object_or_404(RepositoryItem, id=item_id)
        
        # Get or create download counter for this item
        download_counter, created = DownloadCounter.objects.get_or_create(
            repository_item=repository_item,
            defaults={'download_count': 0}
        )
        
        # Increment the download count
        download_counter.increment_download()
        
        # Serve the file for download
        file_path = repository_item.file.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
        else:
            messages.error(request, "File not found.")
            return redirect('index')
    
class WhyTdr(TemplateView):
    template_name = "why_tdr.html"

class BlogView(TemplateView):
    template_name = "blog.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filter blog posts by type
        articles = Blog.objects.filter(article_type='articles')
        journals = Blog.objects.filter(article_type='journals')
        special_issues = Blog.objects.filter(article_type='special_issues')

        # Pagination (optional)
        page_number = self.request.GET.get('page')
        context["articles_page"] = Paginator(articles, 3).get_page(page_number)
        context["journals_page"] = Paginator(journals, 3).get_page(page_number)
        context["specials_page"] = Paginator(special_issues, 3).get_page(page_number)

        # Counts
        context["count_articles"] = articles.count()
        context["count_journals"] = journals.count()
        context["count_specials"] = special_issues.count()

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