from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from .models import Dataset, Experiment, Model, Project, TrainingJob


class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['file_name']  # Add any additional fields as needed


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'description', 'status']  # Customize the fields displayed in the form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create Project'))

        # Layout definition
        self.helper.layout = Layout(
            'project_name',
            'description',
            'status',
        )
class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ['name', 'description', 'dataset']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create Experiment'))
        self.helper.layout = Layout(
            'name',
            'description',
            'dataset',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dataset'].queryset = Dataset.objects.all()

class ModelForm(forms.ModelForm):
    class Meta:
        model = Model
        fields = ['name', 'parameters']  # Add any additional fields as needed

class TrainingJobForm(forms.ModelForm):
    class Meta:
        model = TrainingJob
        fields = ['status', 'end_time']  # Add any additional fields as needed
