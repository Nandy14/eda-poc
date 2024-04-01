import json
import tkinter
from tkinter import filedialog, messagebox

def get_top_level_module(parsed_objects):
    try:
        top_level_module = None
        instantiated_modules = set()

        # Find the top-level module by checking which module is not instantiated
        for module_name, module_data in parsed_objects.items():
            instantiated_modules.update(instance['ref_name'] for instance in module_data.get('instances', []))

        for module_name in parsed_objects:
            if module_name not in instantiated_modules:
                top_level_module = module_name
                break

        if not top_level_module:
            raise ValueError("No top-level module found in the parsed objects")

        return top_level_module

    except Exception as e:
        print("An error occurred:", str(e))
        return None

def generate_hierarchical_names_instances(module_name, instances, module_objects, parent_prefix=""):
    hierarchical_names_instances = []
    for instance in instances:
        instance_name = instance['instance']
        hierarchical_name = f"{parent_prefix}/{instance_name}"
        hierarchical_names_instances.append(hierarchical_name)
        print(hierarchical_name)

        # Check if the instance is hierarchical
        if instance.get('cell_type') == 'hierarchical':
            # Recursively call generate_hierarchical_names for nested instances
            ref_module_name = instance['ref_name']
            ref_module_data = module_objects.get(ref_module_name)
            if ref_module_data:
                # Pass the current instance name as the parent_prefix for the recursive call
                generate_hierarchical_names_instances(ref_module_name, ref_module_data['instances'], module_objects, hierarchical_name)
    
    return hierarchical_names_instances
    
def generate_hierarchical_names_nets(module_name, instances, module_objects, parent_prefix=""):
    hierarchical_names_nets = []

    # Print nets of the current module
    module_data = module_objects[module_name]
    nets = module_data.get('nets', [])
    for net in nets:
        if net['net_type'] == 'wire':
            net_name = net['name']
            hierarchical_name = f"{parent_prefix}/{net_name}"
            hierarchical_names_nets.append(hierarchical_name)
            print(hierarchical_name)

    # Check if the instance is hierarchical and print its nets
    for instance in instances:
        if instance.get('cell_type') == 'hierarchical':
            ref_module_name = instance['ref_name']
            ref_module_data = module_objects.get(ref_module_name)
            if ref_module_data:
                instance_name = instance['instance']
                instance_prefix = f"{parent_prefix}/{instance_name}"
                generate_hierarchical_names_nets(ref_module_name, ref_module_data['instances'], module_objects, instance_prefix)
    
    return hierarchical_names_nets

def generate_hierarchical_names_ports(module_name, instances, module_objects, parent_prefix=""):
    hierarchical_names_ports = []

    # Print nets of the current module
    module_data = module_objects[module_name]
    ports = module_data.get('ports', [])

    for direction,ports in ports.items():        
        for port in ports:
            port_name = port['name']
            hierarchical_name = f"{parent_prefix}/{port_name}"
            hierarchical_names_ports.append(hierarchical_name)
            print(hierarchical_name)
        
    # Check if the instance is hierarchical and print its ports
    for instance in instances:        
        if instance['cell_type'] == 'hierarchical':
            ref_module_name = instance['ref_name']
            ref_module_data = module_objects.get(ref_module_name)
            if ref_module_data:
                instance_name = instance['instance']
                instance_prefix = f"{parent_prefix}/{instance_name}"
                generate_hierarchical_names_ports(ref_module_name, ref_module_data['instances'], module_objects, instance_prefix)

    return hierarchical_names_ports

def generate_hierarchical_names_pins(module_name, instances, module_objects, parent_prefix=""):
    hierarchical_names_pins = []

    # Print pins of the current module
    module_data = module_objects[module_name]
    instances = module_data.get('instances', [])
    
    instance_pins = [i.get('pins',[]) for i in instances if i.get('pins') is not None]

    for pin in instance_pins:
        hierarchical_name = f"{parent_prefix}/{pin.name}"

    print(instance_pins)

    # for direction,ports in ports.items():        
    #     for port in ports:
    #         port_name = port['name']
    #         hierarchical_name = f"{parent_prefix}/{port_name}"
    #         hierarchical_names_ports.append(hierarchical_name)
    #         print(hierarchical_name)
        
    # # Check if the instance is hierarchical and print its ports
    # for instance in instances:        
    #     if instance['cell_type'] == 'hierarchical':
    #         ref_module_name = instance['ref_name']
    #         ref_module_data = module_objects.get(ref_module_name)
    #         if ref_module_data:
    #             instance_name = instance['instance']
    #             instance_prefix = f"{parent_prefix}/{instance_name}"
    #             generate_hierarchical_names_ports(ref_module_name, ref_module_data['instances'], module_objects, instance_prefix)

    # return hierarchical_names_ports


def get_file_path_json():
    while True:
        root = tkinter.Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON Files", "*.json")]
        )

        if file_path and not file_path.lower().endswith(".json"):
            error_message = "Invalid file format. Please select a valid JSON file with a '.json' extension."
            messagebox.showerror("Error", error_message)
        else:
            break

    return file_path

def main():
    # Get the file path using the file dialog
    file_path = get_file_path_json()

    # Load the JSON data from the selected file
    with open(file_path, 'r') as file:
        modules = json.load(file)

    '''
    Converting the list of modules to a dictionary where the keys are module names 
    is necessary for efficient access to module data during the traversal and processing of the hierarchy.
    '''

    # Convert the list to a dictionary where keys are module names
    module_objects = {module_data['module_name']: module_data for module_data in modules}

    # Determine the top-level module
    top_module_name = get_top_level_module(module_objects)
    if top_module_name:
        print()
        print(f"Top-level module: {top_module_name}")

        top_module_data = module_objects[top_module_name]
        top_module_instances = top_module_data['instances']
        
        # Print the hierarchical names of instances
        print()
        print("Hierarchical names for instances:")        
        print()
        hierarchical_names_instances = generate_hierarchical_names_instances(top_module_name, top_module_instances, module_objects, parent_prefix=top_module_name)
        

        # Print hierarchical nets for the top module
        print()
        print("Hierarchical names for nets")
        print()
        hierarchical_names_nets = generate_hierarchical_names_nets(top_module_name, top_module_instances, module_objects, parent_prefix=top_module_name)

        # Print hierarchical ports for the top module
        print()
        print("Hierarchical names for ports")
        print()
        hierarchical_names_ports = generate_hierarchical_names_ports(top_module_name, top_module_instances, module_objects, parent_prefix=top_module_name)

        # Print hierarchical pins for the top module
        print()
        print("Hierarchical names for pins")
        print()
        hierarchical_names_pins = generate_hierarchical_names_pins(top_module_name, top_module_instances, module_objects, parent_prefix=top_module_name)

    else:
        print("No top-level module found.")

if __name__ == "__main__":
    main()
