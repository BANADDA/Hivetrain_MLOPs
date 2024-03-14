from django.contrib import admin
from django.urls import path

from .views import (datasets, delete_dataset, eda_page, get_datasets, index,
                    new_project, project_detail, projects, upload)

urlpatterns = [
    path('', index, name='index'), 
    path('datasets/', datasets, name='datasets'),
    path('projects/', projects, name='projects'),
    path('upload/', upload, name='upload'),
    path('delete_dataset/<int:dataset_id>/', delete_dataset, name='delete_dataset'),
    path('get_datasets/', get_datasets, name='get_datasets'),
    path('eda/<int:dataset_id>/', eda_page, name='eda_page'),
        path('projects/new/', new_project, name='new_project'),
    path('project_detail/<int:project_id>/', project_detail, name='project_detail'),
    path('project_detail/<str:project_name>/', project_detail, name='project_detail'),
]