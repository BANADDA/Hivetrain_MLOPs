import os

import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from console.models import Project


def insert_dummy_projects():
    dummy_projects = [
        {'project_name': 'Project 1', 'model_type': 'Type A', 'status': 'Active'},
        {'project_name': 'Project 2', 'model_type': 'Type B', 'status': 'Inactive'},
        {'project_name': 'Project 3', 'model_type': 'Type C', 'status': 'Pending'}
        # Add more dummy projects as needed
    ]

    for project_data in dummy_projects:
        Project.objects.create(**project_data)

if __name__ == "__main__":
    insert_dummy_projects()
