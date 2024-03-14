from django.db import models


class Dataset(models.Model):
    # Define your model fields here
    id = models.BigAutoField(primary_key=True)
    file_name = models.CharField(max_length=100)
    upload_date = models.DateTimeField(auto_now_add=True)
    
class Project(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    project_name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    create_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            # Generate custom ID if not provided
            last_project = Project.objects.order_by('-id').first()
            if last_project:
                last_id = int(last_project.id[2:])  
                self.id = 'UP{:04d}'.format(last_id + 1) 
            else:
                self.id = 'UP0001'  
        super().save(*args, **kwargs)
