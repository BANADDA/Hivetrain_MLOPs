from django.contrib import admin
from django.urls import path

from .views import (create_model_and_start_training_ajax, datasets,
                    delete_dataset, delete_experiment, eda_page,
                    experiment_list, get_datasets, index, model_detail,
                    monitor_training, new_model, submit_experiment, upload,
                    user_login, user_logout, user_signup, view_experiment)

urlpatterns = [
    path('', experiment_list, name='index'),
    path('login/', user_login, name='login'),
    path('signup/', user_signup, name='signup'),
    path('logout/', user_logout, name='logout'),
    path('datasets/', datasets, name='datasets'),
    path('datasets/upload/', upload, name='upload'),
    path('datasets/<int:dataset_id>/eda/', eda_page, name='eda_page'),
    path('datasets/<int:dataset_id>/delete/', delete_dataset, name='delete_dataset'),
    path('datasets/api/get_datasets/', get_datasets, name='get_datasets'),
    path('experiments/', experiment_list, name='experiments'),
    path('submit_experiment/', submit_experiment, name='submit_experiment'),
    path('submit_model/', new_model, name='submit_model'),
    path('experiment/<int:experiment_id>/', view_experiment, name='view_experiment'),
    path('api/submit_form/', create_model_and_start_training_ajax, name='submit_form_ajax'),
    path('training_jobs/<int:training_job_id>/monitor/', monitor_training, name='monitor_training'),
    path('experiment/delete/<int:experiment_id>/', delete_experiment, name='delete_experiment'),
    # path('experiment/<int:experiment_id>/new_model/', new_model, name='new_model'),
    path('models/<int:model_id>/', model_detail, name='model_detail'),
]


# urlpatterns = [
#     path('', index, name='index'), 
#     path('datasets/', datasets, name='datasets'),
#     path('projects/', projects, name='projects'),
#     path('upload/', upload, name='upload'),
#     path('delete_dataset/<int:dataset_id>/', delete_dataset, name='delete_dataset'),
#     path('get_datasets/', get_datasets, name='get_datasets'),
#     path('eda/<int:dataset_id>/', eda_page, name='eda_page'),
#     path('projects/new/', new_project, name='new_project'),
#     path('projects/<str:project_id>/', project_detail, name='project_detail'),
#     # path('project_detail/<str:project_name>/', project_detail, name='project_detail'),

#     # URLs for project related views
#     path('project/create/', create_project, name='create_project'),
#     path('project/<str:project_id>/delete/', delete_project, name='delete_project'),

#     # URLs for experiment related views
#     path('project/<str:project_id>/exp/create/', create_experiment, name='create_experiment'),
#     path('experiment/<int:experiment_id>/delete/', project_detail, name='delete_experiment'),

#     # URLs for model related views
#     path('experiment/<int:experiment_id>/model/create/', eda_page, name='create_model'),
#     path('model/<int:model_id>/delete/', datasets, name='delete_model'),

#     # URLs for training job related views
#     path('model/<int:model_id>/training_job/create/', projects, name='create_training_job'),
#     path('training_job/<int:job_id>/delete/', index, name='delete_training_job')
# ]