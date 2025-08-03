# get_class_names.py
# This simple script reads the subdirectories from your dataset folder
# and prints a Python list of the class names in the correct alphabetical order.

import os

# The directory where your dataset is stored
DATASET_DIR = "PlantVillage"

if not os.path.exists(DATASET_DIR):
    print(f"Error: Directory '{DATASET_DIR}' not found.")
    print("Please make sure your dataset folder is in the same directory as this script.")
else:
    # Get a list of all subdirectories (which are the class names)
    class_names = sorted([d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))])
    
    print(f"Found {len(class_names)} classes.\n")
    print("Please copy the list below and paste it into your 'digital_pathologist.py' file.\n")
    
    # Print the list in a format that's easy to copy and paste
    print("CLASS_NAMES = [")
    for name in class_names:
        print(f"    '{name}',")
    print("]")

