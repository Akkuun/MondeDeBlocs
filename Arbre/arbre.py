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

def load_objects_data(filename):
    """Load objects data with appropriate type conversions"""
    converters = {
        'ID': int,
        'MATERIAU_ID': int,
        'SUR_ID': int,
        'COUCHE': lambda x: x.strip().lower() == 'true',  # Convert to boolean
        'FORME': str
    }
    return load_csv_data(filename, converters)

def load_materials_data():
    """Load materials data with appropriate type conversions"""
    converters = {
        'ID': int,
        'POIDS': float,
        'OPACITE': float
    }
    return load_csv_data('materiau.csv', converters)

def get_objects_on_top(obj_id, objects_data):
    """
    Get all objects that are directly on top of the given object
    
    Args:
        obj_id (int): ID of the object to check
        objects_data (list): List of object dictionaries
    
    Returns:
        list: List of objects that are on top of this object
    """
    return [obj for obj in objects_data if obj['SUR_ID'] == obj_id]

def peut_etre_deplace(obj_id, objects_data):
    """
    Returns True if the object can be moved
    Conditions: object is not the table AND object has nothing on top of it
    
    Args:
        obj_id (int): ID of the object to check
        objects_data (list): List of object dictionaries
    
    Returns:
        bool: True if object can be moved
    """
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        return False
    
    # Cannot move if it's a table
    if obj['FORME'].strip().upper() == 'TABLE':
        return False
    
    # Cannot move if something is on top of it
    objects_on_top = get_objects_on_top(obj_id, objects_data)
    return len(objects_on_top) == 0

def peut_etre_couche(obj_id, objects_data):
    """
    Returns True if the object can be laid down
    Conditions: object is not the table AND object has nothing on top of it AND object is not a cube
    
    Args:
        obj_id (int): ID of the object to check
        objects_data (list): List of object dictionaries
    
    Returns:
        bool: True if object can be laid down
    """
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        return False
    
    # Cannot lay down if it's a table
    if obj['FORME'].strip().upper() == 'TABLE':
        return False
    
    # Cannot lay down if it's a cube
    if obj['FORME'].strip().upper() == 'CUBE':
        return False
    
    # Cannot lay down if something is on top of it
    objects_on_top = get_objects_on_top(obj_id, objects_data)
    return len(objects_on_top) == 0

def peut_recevoir_deplacement(obj_id, objects_data):
    """
    Returns True if the object can receive another object on top of it
    Conditions: 
    - object is the table OR
    - object is a cylinder and is standing up OR  
    - object is a donut saucisse and laying down OR
    - object is a cube that has nothing on top of it
    
    Args:
        obj_id (int): ID of the object to check
        objects_data (list): List of object dictionaries
    
    Returns:
        bool: True if object can receive another object
    """
    # Find the object
    obj = next((o for o in objects_data if o['ID'] == obj_id), None)
    if not obj:
        return False
    
    forme = obj['FORME'].strip().upper()
    
    # Table can always receive objects
    if forme == 'TABLE':
        return True
    
    # Cylinder can receive objects if standing up (not couché)
    if forme == 'CYLINDRE' and not obj['COUCHE']:
        return True
    
    # Donut saucisse can receive objects if laying down (couché)
    if forme == 'DONUT_SAUCISSE' and obj['COUCHE']:
        return True
    
    # Cube can receive objects if nothing is on top of it
    if forme == 'CUBE':
        objects_on_top = get_objects_on_top(obj_id, objects_data)
        return len(objects_on_top) == 0
    
    return False

# Load start and final object datasets
start_objects_data = load_objects_data('start_objet.csv')
final_objects_data = load_objects_data('final_objet.csv')
materials_data = load_materials_data()

print("\n=== START OBJECTS DATA ===")
for obj in start_objects_data:
    couche_status = "Couché" if obj['COUCHE'] else "Debout"
    print(f"Object {obj['ID']}: {obj['NOM']} ({obj['FORME'].strip()}) - {couche_status} (Material: {obj['MATERIAU_ID']}, On: {obj['SUR_ID']})")

print("\n=== FINAL OBJECTS DATA ===")
for obj in final_objects_data:
    couche_status = "Couché" if obj['COUCHE'] else "Debout"
    print(f"Object {obj['ID']}: {obj['NOM']} ({obj['FORME'].strip()}) - {couche_status} (Material: {obj['MATERIAU_ID']}, On: {obj['SUR_ID']})")

print("\n=== MATERIALS DATA ===")
for mat in materials_data:
    print(f"Material {mat['ID']}: {mat['NOM']} - {mat['COULEUR']} {mat['MATERIAU']} (Weight: {mat['POIDS']}, Opacity: {mat['OPACITE']})")

print("\n=== CHANGES BETWEEN START AND FINAL ===")
for start_obj, final_obj in zip(start_objects_data, final_objects_data):
    if start_obj['ID'] == final_obj['ID']:
        changes = []
        if start_obj['SUR_ID'] != final_obj['SUR_ID']:
            changes.append(f"SUR_ID: {start_obj['SUR_ID']} → {final_obj['SUR_ID']}")
        if start_obj['COUCHE'] != final_obj['COUCHE']:
            changes.append(f"COUCHE: {start_obj['COUCHE']} → {final_obj['COUCHE']}")
        if changes:
            print(f"Object {start_obj['ID']} ({start_obj['NOM']}): {', '.join(changes)}")
        else:
            print(f"Object {start_obj['ID']} ({start_obj['NOM']}): No changes")

print("\n=== MOVEMENT CAPABILITIES ANALYSIS ===")

def test_movement_functions(objects_data, dataset_name):
    print(f"\n--- {dataset_name} ---")
    for obj in objects_data:
        obj_id = obj['ID']
        nom = obj['NOM']
        
        peut_deplacer = peut_etre_deplace(obj_id, objects_data)
        peut_coucher = peut_etre_couche(obj_id, objects_data)
        peut_recevoir = peut_recevoir_deplacement(obj_id, objects_data)
        
        print(f"Object {obj_id} ({nom}):")
        print(f"  - Peut être déplacé: {peut_deplacer}")
        print(f"  - Peut être couché: {peut_coucher}")
        print(f"  - Peut recevoir un objet: {peut_recevoir}")
        
        # Show what's on top
        objects_on_top = get_objects_on_top(obj_id, objects_data)
        if objects_on_top:
            names_on_top = [o['NOM'] for o in objects_on_top]
            print(f"  - Objets dessus: {', '.join(names_on_top)}")
        else:
            print(f"  - Objets dessus: Aucun")

test_movement_functions(start_objects_data, "START DATASET")
test_movement_functions(final_objects_data, "FINAL DATASET")
