import os
from collections import Counter
from django.conf import settings
import pandas as pd

def analyze_data(file_name):
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found.")

        if file_name.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Only CSV and Excel files are supported.")

        columns_info = []

        for column in df.columns:
            distinct_values = df[column].nunique()
            percentage_distinct_values = (distinct_values / len(df[column])) * 100
            missing_values = df[column].isnull().sum()
            percentage_missing_values = (missing_values / len(df[column])) * 100

            columns_info.append({
                'column_name': column,
                'distinct_values': distinct_values,
                'percentage_distinct_values': percentage_distinct_values,
                'missing_values': missing_values,
                'percentage_missing_values': percentage_missing_values
            })

        return columns_info
    except Exception as e:
        print(f"Error occurred while analyzing data: {str(e)}")
        return None
    
def get_dataset_info(file_name):
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found.")

        if file_name.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Only CSV and Excel files are supported.")

        num_rows = len(df)
        num_columns = len(df.columns)
        column_data_types = df.dtypes  # Get data types of columns

        return {
            'num_rows': num_rows,
            'num_columns': num_columns,
            'total_records': num_rows * num_columns,  # Total number of records
            'column_data_types': column_data_types.to_dict()  # Convert Series to dictionary for serialization
        }
    except Exception as e:
        print(f"Error occurred while retrieving dataset information: {str(e)}")
        return None

def get_numeric_columns_data(file_name):
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found.")

        if file_name.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Only CSV and Excel files are supported.")

        numeric_columns_data = {}

        for column in df.select_dtypes(include=['int64', 'float64']).columns:
            numeric_columns_data[column] = df[column].tolist()

        return numeric_columns_data
    except Exception as e:
        print(f"Error occurred while retrieving numeric columns data: {str(e)}")
        return None

def get_categorical_columns_data(file_name):
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found.")

        if file_name.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Only CSV and Excel files are supported.")

        categorical_columns_data = {}

        for column in df.select_dtypes(include=['object', 'category']).columns:
            categorical_columns_data[column] = df[column].value_counts().to_dict()

        return categorical_columns_data
    except Exception as e:
        print(f"Error occurred while retrieving categorical columns data: {str(e)}")
        return None

def get_text_data(file_name):
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found.")

        # Assuming the text file contains source-target language pairs separated by a delimiter
        with open(file_path, 'r', encoding='utf-8') as file:
            text_data = [line.strip().split('\t') for line in file.readlines()]

        return text_data
    except Exception as e:
        print(f"Error occurred while retrieving text data: {str(e)}")
        return None

def extract_text_statistics(text_data):
    try:
        source_texts = [pair[0] for pair in text_data]
        target_texts = [pair[1] for pair in text_data]

        source_word_counts = Counter(" ".join(source_texts).split())
        target_word_counts = Counter(" ".join(target_texts).split())

        return {
            'source_word_counts': source_word_counts,
            'target_word_counts': target_word_counts,
        }
    except Exception as e:
        print(f"Error occurred while extracting text statistics: {str(e)}")
        return None
