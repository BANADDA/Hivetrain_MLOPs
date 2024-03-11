from django.contrib import admin
from django.urls import path
from .views import index, datasets, upload, delete_dataset, get_datasets, eda_page

urlpatterns = [
    path('', index, name='index'), 
    path('datasets/', datasets, name='datasets'),
    path('upload/', upload, name='upload'),
    path('delete_dataset/<int:dataset_id>/', delete_dataset, name='delete_dataset'),
    path('get_datasets/', get_datasets, name='get_datasets'),
    path('eda/<int:dataset_id>/', eda_page, name='eda_page'),    
]