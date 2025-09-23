import csv
import os

def load_csv_data(filename, data_converters=None):
    """
    Generic function to load CSV data from the csv folder
    
    Args:
        filename (str): Name of the CSV file (e.g., 'export_objet.csv')
        data_converters (dict): Optional dictionary to convert specific columns to different types
                               e.g., {'ID': int, 'POIDS': float}
    
    Returns:
        list: List of dictionaries containing the CSV data
    """
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'csv', filename)
    data = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Apply data converters if provided
                if data_converters:
                    for column, converter in data_converters.items():
                        if column in row and row[column]:
                            try:
                                row[column] = converter(row[column])
                            except ValueError as e:
                                print(f"Warning: Could not convert {column}='{row[column]}' using {converter.__name__}: {e}")
                
                data.append(row)
        
        print(f"Loaded {len(data)} records from {filename}")
        return data
    except FileNotFoundError:
        print(f"CSV file not found at: {csv_path}")
        return []
    except Exception as e:
        print(f"Error loading CSV {filename}: {e}")
        return []

def load_objects_data():
    """Load objects data with appropriate type conversions"""
    converters = {
        'ID': int,
        'MATERIAU_ID': int,
        'SUR_ID': int
    }
    return load_csv_data('export_objet.csv', converters)

def load_materials_data():
    """Load materials data with appropriate type conversions"""
    converters = {
        'ID': int,
        'POIDS': float,
        'OPACITE': float
    }
    return load_csv_data('export_materiau.csv', converters)

# Load both datasets
objects_data = load_objects_data()
materials_data = load_materials_data()

print("\n=== OBJECTS DATA ===")
for obj in objects_data:
    print(f"Object {obj['ID']}: {obj['NOM']} (Material: {obj['MATERIAU_ID']}, On: {obj['SUR_ID']})")

print("\n=== MATERIALS DATA ===")
for mat in materials_data:
    print(f"Material {mat['ID']}: {mat['NOM']} - {mat['COULEUR']} {mat['MATERIAU']} (Weight: {mat['POIDS']}, Opacity: {mat['OPACITE']})")

