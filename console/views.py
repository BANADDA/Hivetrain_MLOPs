import json
import random
from datetime import *

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView

from . import utils
# from .forms import (DatasetForm, ExperimentForm, ModelForm, ProjectForm,
#                     TrainingJobForm)
from .models import Dataset, Experiment, Model, TrainingJob


def index(request):
    return render(request, 'index.html', {})

def datasets(request):
    # Fetch all dataset objects from the database
    datasets = Dataset.objects.all()
    return render(request, 'datasets.html', {'datasets': datasets})

def experiment_list(request):
    experiments = Experiment.objects.all()
    image_urls = [
        'https://optimine.com/wp-content/uploads/2023/04/how-to-learn-big-data-7-places-to-start-in-2022.jpg',
        'https://www.simplilearn.com/ice9/free_resources_article_thumb/data_analyticstrendsmin.jpg',
        'https://www.datamation.com/wp-content/uploads/2023/08/dm08172023-what-is-data-analytics-768x502.png'
    ]
    for experiment in experiments:
        experiment.random_image_url = random.choice(image_urls)
    return render(request, 'exps/exp.html', {'experiments': experiments})  # Change 'experiment' to 'experiments'

def submit_experiment(request):
    if request.method == 'POST':
        experiment_name = request.POST.get('experimentName')
        experiment_description = request.POST.get('experimentDescription')
        
        experiment = Experiment.objects.create(name=experiment_name, description=experiment_description)

        if experiment:
            messages.success(request, 'Experiment submitted successfully!', 'alert-success alert-dismissible')
            return JsonResponse({'success': True})
        else:
            messages.error(request, 'Failed to save experiment data')
            return JsonResponse({'success': False, 'message': 'Failed to save experiment data.'}, status=400)
    else:
        messages.error(request, 'Only POST requests are allowed')
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed.'}, status=400)

def view_experiment(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    # Retrieve the model associated with the experiment
    model = Model.objects.filter(experiment=experiment).first() 
    # Retrieve training jobs associated with the model
    training_jobs = TrainingJob.objects.filter(model=model) if model else []
    datasets = Dataset.objects.all() 
    return render(request, 'exps/experiment_details.html', {'experiment': experiment, 'model': model, 'training_jobs': training_jobs, 'datasets': datasets})

def new_model(request):
    if request.method == 'POST':
        # Parse JSON data from the request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)

        # Retrieve form data from parsed JSON data
        model_name = data.get('modelName')
        model_domain = data.get('modelDomain')
        selected_dataset_id = data.get('selectedDatasetId')
        experiment_id = data.get('experiment_id')

        # Check if all required data is available
        if model_name and model_domain and selected_dataset_id and experiment_id:
            # Create the Model instance
            model = Model.objects.create(
                experiment_id=experiment_id,
                dataset_id=selected_dataset_id,
                name=model_name,
                domain=model_domain
            )
            
            # Create the TrainingJob instance
            if model:
                training_job = TrainingJob.objects.create(
                    model=model,
                    status='pending',
                    start_time=timezone.now()
                )
                if training_job:
                    return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'message': 'Failed to create model or training job.'}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Only POST requests are allowed.'}, status=400)

def model_detail(request, model_id):
    model = Model.objects.get(pk=model_id)
    return render(request, 'model_detail.html', {'model': model})

def upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        save_path = 'media/' + uploaded_file.name
        with open(save_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        # Create a record for the dataset in the database
        dataset = Dataset.objects.create(file_name=uploaded_file.name)
        # Add a success message
        messages.success(request, 'Your file has been uploaded successfully.')
        # Redirect to datasets page to avoid form resubmission
        return redirect('datasets')
    return render(request, 'datasets.html', {'file_uploaded': False})

def get_datasets(request):
    row_count = request.GET.get('rowCount')
    # Fetch datasets based on the specified row count
    datasets = Dataset.objects.all()[:int(row_count)]  # Adjust as per your logic
    # Generate HTML for the dataset rows (you may use a template for this)
    dataset_rows = ""
    for dataset in datasets:
        dataset_rows += f"<tr><td>{dataset.file_name}</td><td>{dataset.upload_date}</td><td><button class='btn btn-primary'>EDA</button></td><td><button class='btn btn-danger' onclick='deleteDataset({dataset.id})'><i class='fas fa-trash-alt'></i></button></td></tr>"
    return JsonResponse({'dataset_rows': dataset_rows})

def delete_dataset(request, dataset_id):
    # Get the dataset object to delete
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    dataset.delete()
    messages.error(request, f'Dataset {dataset.file_name} has been deleted successfully.')
    return redirect('datasets')

def eda_page(request, dataset_id):
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        file_name = dataset.file_name
        columns_info = utils.analyze_data(file_name)
        dataset_info = utils.get_dataset_info(file_name)

        # Additional data for visualization
        numeric_columns_data = utils.get_numeric_columns_data(file_name)
        categorical_columns_data = utils.get_categorical_columns_data(file_name)
        text_data = utils.get_text_data(file_name)
        text_statistics = utils.extract_text_statistics(text_data)

        context = {
            'file_name': file_name,
            'dataset_id': dataset_id,
            'columns_info': columns_info,
            'dataset_info': dataset_info,
            'numeric_columns_data': numeric_columns_data,
            'categorical_columns_data': categorical_columns_data,
            'text_statistics': text_statistics,
        }
        return render(request, 'eda_page.html', context)
    except Dataset.DoesNotExist:
        messages.error(request, 'Dataset does not exist.')
        return redirect('datasets')

# def trainingjob_detail(request, trainingjob_id):
#     trainingjob = TrainingJob.objects.get(pk=trainingjob_id)
#     return render(request, 'trainingjob_detail.html', {'trainingjob': trainingjob})

# def projects(request):
#     projects = Project.objects.all()
#     return render(request, 'index_projects.html', {'projects': projects})

# def new_project(request):
#     return render(request, 'exps/no_exp.html')

# def project_detail(request, project_id):
#     project = get_object_or_404(Project, pk=project_id)
#     experiments = Experiment.objects.filter(project=project)
#     image_urls = [
#         'https://optimine.com/wp-content/uploads/2023/04/how-to-learn-big-data-7-places-to-start-in-2022.jpg',
#         'https://www.simplilearn.com/ice9/free_resources_article_thumb/data_analyticstrendsmin.jpg',
#         'https://www.datamation.com/wp-content/uploads/2023/08/dm08172023-what-is-data-analytics-768x502.png'
#     ]
#     for experiment in experiments:
#         experiment.random_image_url = random.choice(image_urls)
#     return render(request, 'exps/exp.html', {'project': project, 'experiments': experiments})



# Views for creating instances

# Views for creating instances
# def create_project(request):
#     if request.method == 'POST':
#         form = ProjectForm(request.POST)
#         if form.is_valid():
#             # Set the default status to 'active'
#             form.instance.status = 'active'
#             form.save()
#             return redirect('projects')  # Redirect to projects list page
#     else:
#         form = ProjectForm()
#     return render(request, 'projects/create_project.html', {'form': form})

# def create_experiment(request):
#     # project = get_object_or_404(Project, pk=project_id)
#     experiments = Experiment.objects.filter(project=project)
#     image_urls = [
#         'https://optimine.com/wp-content/uploads/2023/04/how-to-learn-big-data-7-places-to-start-in-2022.jpg',
#         'https://www.simplilearn.com/ice9/free_resources_article_thumb/data_analyticstrendsmin.jpg',
#         'https://www.datamation.com/wp-content/uploads/2023/08/dm08172023-what-is-data-analytics-768x502.png'
#     ]
#     for experiment in experiments:
#         experiment.random_image_url = random.choice(image_urls)
#     if request.method == 'POST':
#         # Initialize the form with both POST data and project_id
#         form = ExperimentForm(request.POST)
#         if form.is_valid():
#             # Save the form with the project_id
#             experiment = form.save(commit=False)
#             # experiment.project_id = project_id  # Associate experiment with project
#             experiment.save()
#             return redirect('project_detail', project_id=project_id)
#     else:
#         # Initialize the form with the project_id in the initial data
#         form = ExperimentForm(initial={'project': project_id})

#     return render(request, 'exps/create_experiment.html', {'form': form, 'project': project})

# def create_model(request, experiment_id):
#     if request.method == 'POST':
#         form = ModelForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('models', experiment_id=experiment_id)  # Redirect to models list page for the experiment
#     else:
#         form = ModelForm()
#     return render(request, 'create_model.html', {'form': form})

# def create_training_job(request, model_id):
#     if request.method == 'POST':
#         form = TrainingJobForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('training_jobs', model_id=model_id)  # Redirect to training jobs list page for the model
#     else:
#         form = TrainingJobForm()
#     return render(request, 'create_training_job.html', {'form': form})

# # Views for deleting instances

# def delete_project(request, project_id):
#     project = get_object_or_404(Project, id=project_id)
#     if request.method == 'POST':
#         project.delete()
#         return redirect('projects')  # Redirect to projects list page
#     return render(request, 'delete_project.html', {'project': project})

# def delete_experiment(request, experiment_id):
#     experiment = get_object_or_404(Experiment, id=experiment_id)
#     if request.method == 'POST':
#         experiment.delete()
#         return redirect('experiments', project_id=experiment.project_id)  # Redirect to experiments list page for the project
#     return render(request, 'delete_experiment.html', {'experiment': experiment})

# def delete_model(request, model_id):
#     model = get_object_or_404(Model, id=model_id)
#     if request.method == 'POST':
#         model.delete()
#         return redirect('models', experiment_id=model.experiment_id)  # Redirect to models list page for the experiment
#     return render(request, 'delete_model.html', {'model': model})

# def delete_training_job(request, job_id):
#     job = get_object_or_404(TrainingJob, id=job_id)
#     if request.method == 'POST':
#         job.delete()
#         return redirect('training_jobs', model_id=job.model_id)  # Redirect to training jobs list page for the model
#     return render(request, 'delete_training_job.html', {'job': job})

