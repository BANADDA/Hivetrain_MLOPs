from django.contrib import admin
from django.urls import path

from .views import (create_experiment, create_project, datasets,
                    delete_dataset, delete_project, eda_page, get_datasets,
                    index, new_project, project_detail, projects, upload)

urlpatterns = [
    path('', index, name='index'), 
    path('datasets/', datasets, name='datasets'),
    path('projects/', projects, name='projects'),
    path('upload/', upload, name='upload'),
    path('delete_dataset/<int:dataset_id>/', delete_dataset, name='delete_dataset'),
    path('get_datasets/', get_datasets, name='get_datasets'),
    path('eda/<int:dataset_id>/', eda_page, name='eda_page'),
    path('projects/new/', new_project, name='new_project'),
    path('projects/<str:project_id>/', project_detail, name='project_detail'),
    # path('project_detail/<str:project_name>/', project_detail, name='project_detail'),

    # URLs for project related views
    path('project/create/', create_project, name='create_project'),
    path('project/<str:project_id>/delete/', delete_project, name='delete_project'),

    # URLs for experiment related views
    path('project/<str:project_id>/exp/create/', create_experiment, name='create_experiment'),
    path('experiment/<int:experiment_id>/delete/', project_detail, name='delete_experiment'),

    # URLs for model related views
    path('experiment/<int:experiment_id>/model/create/', eda_page, name='create_model'),
    path('model/<int:model_id>/delete/', datasets, name='delete_model'),

    # URLs for training job related views
    path('model/<int:model_id>/training_job/create/', projects, name='create_training_job'),
    path('training_job/<int:job_id>/delete/', index, name='delete_training_job')
]