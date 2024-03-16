from datetime import timezone

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView

from . import utils
from .forms import (DatasetForm, ExperimentForm, ModelForm, ProjectForm,
                    TrainingJobForm)
from .models import Dataset, Experiment, Model, Project, TrainingJob


def index(request):
    return render(request, 'index.html', {})

def datasets(request):
    # Fetch all dataset objects from the database
    datasets = Dataset.objects.all()
    return render(request, 'datasets.html', {'datasets': datasets})

def projects(request):
    projects = Project.objects.all()
    return render(request, 'index_projects.html', {'projects': projects})

def new_project(request):
    return render(request, 'exps/no_exp.html')

def project_detail(request, project_id=None, project_name=None):
    project = None
    if project_id:
        project = get_object_or_404(Project, id=project_id)
    elif project_name:
        project = get_object_or_404(Project, name=project_name)
    return render(request, 'project_detail.html', {'project': project})

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

# Views for creating instances

# Views for creating instances
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # Set the default status to 'active'
            form.instance.status = 'active'
            form.save()
            return redirect('projects')  # Redirect to projects list page
    else:
        form = ProjectForm()
    return render(request, 'projects/create_project.html', {'form': form})

def create_experiment(request, project_id):
    if request.method == 'POST':
        form = ExperimentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('experiments', project_id=project_id)  # Redirect to experiments list page for the project
    else:
        form = ExperimentForm()
    return render(request, 'create_experiment.html', {'form': form})

def create_model(request, experiment_id):
    if request.method == 'POST':
        form = ModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('models', experiment_id=experiment_id)  # Redirect to models list page for the experiment
    else:
        form = ModelForm()
    return render(request, 'create_model.html', {'form': form})

def create_training_job(request, model_id):
    if request.method == 'POST':
        form = TrainingJobForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('training_jobs', model_id=model_id)  # Redirect to training jobs list page for the model
    else:
        form = TrainingJobForm()
    return render(request, 'create_training_job.html', {'form': form})

# Views for deleting instances

def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        project.delete()
        return redirect('projects')  # Redirect to projects list page
    return render(request, 'delete_project.html', {'project': project})

def delete_experiment(request, experiment_id):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    if request.method == 'POST':
        experiment.delete()
        return redirect('experiments', project_id=experiment.project_id)  # Redirect to experiments list page for the project
    return render(request, 'delete_experiment.html', {'experiment': experiment})

def delete_model(request, model_id):
    model = get_object_or_404(Model, id=model_id)
    if request.method == 'POST':
        model.delete()
        return redirect('models', experiment_id=model.experiment_id)  # Redirect to models list page for the experiment
    return render(request, 'delete_model.html', {'model': model})

def delete_training_job(request, job_id):
    job = get_object_or_404(TrainingJob, id=job_id)
    if request.method == 'POST':
        job.delete()
        return redirect('training_jobs', model_id=job.model_id)  # Redirect to training jobs list page for the model
    return render(request, 'delete_training_job.html', {'job': job})

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