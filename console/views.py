from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Dataset
from django.http import JsonResponse
from django.http import HttpResponse
from . import utils

def index(request):
    return render(request, 'index.html', {})

def datasets(request):
    # Fetch all dataset objects from the database
    datasets = Dataset.objects.all()
    return render(request, 'datasets.html', {'datasets': datasets})

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
        dataset_rows += f"<tr><td>{dataset.file_name}</td><td>{dataset.upload_date}</td><td><button class='btn btn-primary'>EDA</button></td><td><button class='btn btn-danger'><i class='fas fa-trash-alt'></i></button></td></tr>"
    return JsonResponse({'dataset_rows': dataset_rows})

def delete_dataset(request, dataset_id):
    # Get the dataset object to delete
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    # Delete the dataset
    dataset.delete()
    # Add a success message
    messages.error(request, f'Dataset {dataset.file_name} has been deleted successfully.')
    # Redirect back to datasets page
    return redirect('datasets')