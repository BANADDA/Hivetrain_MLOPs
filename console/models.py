from django.db import models
from django.utils import timezone


class Dataset(models.Model):
    # Define your model fields here
    id = models.BigAutoField(primary_key=True)
    file_name = models.CharField(max_length=100)
    upload_date = models.DateTimeField(auto_now_add=True)

class Experiment(models.Model):
    id = models.BigAutoField(primary_key=True)
    # project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('stopped', 'Stopped'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.name
    
class Model(models.Model):
    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=10, choices=[('new', 'New Model'), ('finetune', 'FineTune')], default='new')
    created_at = models.DateTimeField(auto_now_add=False, default=timezone.now)
    version = models.PositiveIntegerField(default=1)
    formatted_version = models.CharField(max_length=20, blank=True)  # New field for storing formatted version
    
    def __str__(self):
        return self.name

    def update_formatted_version(self):
        self.formatted_version = f"ML{self.id}v{self.version}"
        self.save()

class Domain(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name="domains")
    domain_type = models.CharField(max_length=50)  # e.g., 'Computer Vision', 'NLP'

    def __str__(self):
        return f'{self.domain_type} - {self.model.name}'

class Task(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="tasks")
    task_name = models.CharField(max_length=100)  # e.g., 'Object Detection', 'Machine Translation'
    configuration = models.JSONField(default=dict) # To store variable task-specific configuration dynamically

    def __str__(self):
        return f'{self.task_name} - {self.domain.domain_type}'

class DatasetConfig(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name="datasets")
    dataset_url = models.URLField(max_length=1024)
    train_percentage = models.IntegerField()
    test_percentage = models.IntegerField()
    validation_percentage = models.IntegerField()

    def __str__(self):
        return f'{self.model.name} Dataset Configuration'

class TrainingJob(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name="training_jobs")
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, null=True, blank=True, related_name="training_jobs")
    dataset_config = models.ForeignKey(DatasetConfig, on_delete=models.SET_NULL, null=True, blank=True, related_name="training_jobs")  # Link to DatasetConfig
    status = models.CharField(max_length=100, choices=[('queued', 'Queued'), ('training', 'Training'), ('completed', 'Completed'), ('error', 'Error')])  # Expanded status choices
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    metrics = models.JSONField(default=dict)  # To dynamically store training metrics
    log_path = models.TextField(null=True, blank=True)  # Optional path to log file or direct log storage
    
    def save(self, *args, **kwargs):
        creating = not self.pk
        super().save(*args, **kwargs)
        if creating:
            # If creating a new instance, increment the model version and update the formatted version
            self.model.version += 1
            self.model.update_formatted_version()

    def __str__(self):
        return f'Training Job for {self.model.name} - Status: {self.status}'
