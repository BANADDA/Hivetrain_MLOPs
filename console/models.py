from django.db import models


class Dataset(models.Model):
    # Define your model fields here
    id = models.BigAutoField(primary_key=True)
    file_name = models.CharField(max_length=100)
    upload_date = models.DateTimeField(auto_now_add=True)
    
class Project(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    project_name = models.CharField(max_length=100)
    description = models.TextField(default=None, blank=True, null=True)
    status = models.CharField(max_length=100)
    create_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            last_project = Project.objects.order_by('-id').first()
            if last_project:
                last_id = int(last_project.id[2:])  
                self.id = 'UP{:04d}'.format(last_id + 1) 
            else:
                self.id = 'UP0001'  
        super().save(*args, **kwargs)

class Experiment(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
class Model(models.Model):
    id = models.BigAutoField(primary_key=True)
    experiment = models.OneToOneField(Experiment, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    parameters = models.JSONField()  # Storing parameters as JSON

class TrainingJob(models.Model):
    id = models.BigAutoField(primary_key=True)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
