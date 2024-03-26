import json
import random
from datetime import *

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, DeleteView

from . import utils
# from .forms import (DatasetForm, ExperimentForm, ModelForm, ProjectForm,
#                     TrainingJobForm)
from .models import (Dataset, DatasetConfig, Domain, Experiment, Model, Task,
                     TrainingJob)


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
            # Add success message with experiment name
            messages.success(request, f'Experiment {experiment_name} created successfully', 'alert-success alert-dismissible')
            
            # Set a timer to automatically dismiss the success message after 2 seconds
            request.session['dismiss_success_message'] = timezone.now().timestamp() + 2000
            
            return JsonResponse({'success': True, 'exp_id': experiment.id})
        else:
            messages.error(request, 'Failed to save experiment data')
            return JsonResponse({'success': False, 'message': 'Failed to save experiment data.'}, status=400)
    else:
        messages.error(request, 'Only POST requests are allowed')
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed.'}, status=400)

@csrf_exempt 
@require_http_methods(["POST"])
def delete_experiment(request, experiment_id):
    try:
        # Retrieve the experiment to be deleted
        experiment = get_object_or_404(Experiment, pk=experiment_id)

        # Delete the experiment itself
        experiment.delete()

        # Add a success message
        messages.success(request, f'Experiment "{experiment.name}" and all associated models and training jobs have been successfully deleted.')

        # Redirect to the experiment list page or another appropriate page
        return JsonResponse({
            'success': True,
            'message': 'Experiment deleted successfully.',
        })
    except Exception as e:
        # Handle any exceptions that occur during deletion
        return JsonResponse({
            'success': False,
            'message': 'Failed to delete experiment. Error: {}'.format(str(e))
        }, status=500)

def view_experiment(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    training_jobs = TrainingJob.objects.filter(experiment=experiment)
    
    latest_model = Model.objects.filter(training_jobs__in=training_jobs).order_by('-created_at').first()

    datasets = Dataset.objects.all()

    return render(request, 'exps/experiment_details.html', {
        'experiment': experiment,
        'latest_model': latest_model,  # Pass the specific model to focus on
        'training_jobs': training_jobs,
        'datasets': datasets
    })

@csrf_exempt
@require_http_methods(["POST"])
def create_model_and_start_training_ajax(request):
    # Decode JSON data from the request body
    data = json.loads(request.body.decode('utf-8'))

    # Direct mapping of form data to model fields
    model_name = data.get('modelName', '')
    # architecture = data.get('architecture', '')  # Assuming architecture is part of form data
    model_type = data.get('modelType', 'new')  # Defaulting to 'new' if not provided
    domain_type = data.get('modelDomain', '')
    dataset_url = data.get('datasetURL', '')
    train_percentage = data.get('trainPercentage', 0)
    test_percentage = data.get('testPercentage', 0)
    validation_percentage = data.get('validationPercentage', 0)
    task_type = data.get('taskType', '')
    task_configs = data.get('taskConfigs', {}),
    experiment_id = data.get('experimentId')
    
    try:
        experiment = Experiment.objects.get(id=experiment_id)
    except Experiment.DoesNotExist:
        return JsonResponse({'error': 'Experiment not found'}, status=404)

    try:
        # Create Model instance
        model_instance = Model.objects.create(
            name=model_name,
            # architecture=architecture,
            model_type=model_type,
            created_at=timezone.now()
        )

        # Create Domain instance
        domain_instance = Domain.objects.create(
            model=model_instance,
            domain_type=domain_type
        )

        # Create Task instance
        task_instance = Task.objects.create(
            domain=domain_instance,
            task_name=task_type,
            configuration=task_configs
        )

        # Create DatasetConfig instance
        dataset_config_instance = DatasetConfig.objects.create(
            model=model_instance,
            dataset_url=dataset_url,
            train_percentage=train_percentage,
            test_percentage=test_percentage,
            validation_percentage=validation_percentage
        )

        # Create TrainingJob instance
        training_job_instance = TrainingJob.objects.create(
            model=model_instance,
            experiment=experiment,
            dataset_config=dataset_config_instance,
            status='queued',  # Assuming the job status starts as 'queued'
        )
        
        monitor_url = reverse('monitor_training', args=[training_job_instance.id])


        return JsonResponse({
            "status": "success",
            "message": f"Model '{data.get('modelName', '')}' and training job created successfully.",
            "model_id": model_instance.id,
            "training_job_id": training_job_instance.id,
            "redirect_url": monitor_url
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })
        
def monitor_training(request, training_job_id):
    training_job = get_object_or_404(TrainingJob, pk=training_job_id)
    # Optionally, fetch additional data related to the training job
    # For example, training metrics stored in a related model or logs

    context = {
        'training_job': training_job,
        # Include other context as needed, such as metrics or logs
    }
    return render(request, 'exps/monitor_training.html', context)

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

