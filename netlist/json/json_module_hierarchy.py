import json
import tkinter
from tkinter import filedialog, messagebox

def get_top_level_module(parsed_objects):
    try:
        # Declare two sets to identify top_level_module
        top_level_module = set(parsed_objects.keys())
        instantiated_modules = set()

        # Iterate through each module's instances
        for module_name, module_data in parsed_objects.items():
            # Remove instantiated modules from top-level modules
            instantiated_modules.update(instance['ref_name'] for instance in module_data.get('instances', []))

        top_level_module -= instantiated_modules

        # Check if there is any top-level module
        if not top_level_module:
            raise ValueError("No top-level module found in the parsed objects")

        # Convert set to string if there's only one top-level module
        return next(iter(top_level_module))

    except Exception as e:
        print("An error occurred:", str(e))
        return None

# def generate_hierarchical_names(module_name, instances, hierarchical_names):
#     for instance in instances:
#         instance_name = instance['instance']
#         hierarchical_name = f"{module_name}.{instance_name}"
#         hierarchical_names.append(hierarchical_name)

#         # if instance['cell_type'] == 'hierarchical':
#         # for each instance
#             # get its instance data as in if the instance is hierarchical there will 
#             # be a module defined in the same file which has the instance's ref_name
#             # Suppose m0 is the instance and its cell_type is 'hierarchical', so get 
#             # the data of m0's ref_type 'nibble_parity' module and print out its instances.
#             # 
#             # Do the same for other 'hierarchical' cell types.

def generate_hierarchical_names(module_name, instances, hierarchical_names, parent_prefix=""):
    for instance in instances:
        instance_name = instance['instance']
        hierarchical_name = f"{parent_prefix}{module_name}.{instance_name}"
        hierarchical_names.append(hierarchical_name)
        
        # Check if the instance is hierarchical
        if instance.get('cell_type') == 'hierarchical':
            # Construct the full hierarchical name for the current instance
            instance_prefix = f"{parent_prefix}{module_name}."
            # Recursively call generate_hierarchical_names for the nested instances
            generate_hierarchical_names(instance_name, instance['instances'], hierarchical_names, instance_prefix)

def get_file_path_json():
    """
    Open a file dialog to get the path to a JSON file.

    Returns:
    str: The selected file path.
    """
    while True:
        root = tkinter.Tk()
        root.withdraw()  # Hide the main window

        file_path = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON Files", "*.json")]
        )

        # Check if the selected file has a valid extension
        if file_path and not file_path.lower().endswith(".json"):
            error_message = "Invalid file format. Please select a valid JSON file with a '.json' extension."
            messagebox.showerror("Error", error_message)
        else:
            break  # Break out of the loop if a valid file is selected

    return file_path

def main():
    # Get the file path using the file dialog
    file_path = get_file_path_json()

    # Load the JSON data from the selected file
    with open(file_path, 'r') as file:
        modules = json.load(file)

    # Convert the list to a dictionary where keys are module names
    module_objects = {module_data['module_name']: module_data for module_data in modules}

    # Determine the top-level module
    top_module_name = get_top_level_module(module_objects)
    if top_module_name:
        print(f"Top-level module: {top_module_name}")

        top_module_data = module_objects[top_module_name]
        top_module_instances = top_module_data['instances']
        
        # Generate hierarchical names for the top module
        hierarchical_names = []
        generate_hierarchical_names(top_module_name, top_module_instances, hierarchical_names)
        
        # Print the hierarchical names
        for name in hierarchical_names:
            print(name)

    else:
        print("No top-level module found.")

if __name__ == "__main__":
    main()
