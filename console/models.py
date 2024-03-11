from django.db import models

class Dataset(models.Model):
    # Define your model fields here
    file_name = models.CharField(max_length=100)
    upload_date = models.DateTimeField(auto_now_add=True)
