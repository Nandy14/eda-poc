import json
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd


def get_file_path_json():
    """
    Open a file dialog to get the path to a JSON file.

    Returns:
    str: The selected file path.
    """
    while True:
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        file_path = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON Files", "*.json")]
        )

        # Check if the selected file has a valid extension
        if file_path and not file_path.lower().endswith(".json"):
            messagebox.showerror("Error", "Invalid file format. Please select a valid JSON file with a '.json' extension.")
        elif not file_path:
            messagebox.showinfo("Info", "No file selected. Please choose a JSON file.")
        else:
            break  # Break out of the loop if a valid file is selected

    return file_path

def check_pin_direction(pin_name, ref_name, cell_type, pin_direction_map):
    """
    Determine pin directions based on the provided reference name, pin name, cell type, and pin_direction_map.
    """
    if cell_type == 'leaf-level':
        return pin_name in ['Z', 'Q']
    elif cell_type == 'hierarchical':
        # Use pin_direction_map to determine pin direction for hierarchical cells
        if ref_name in pin_direction_map:
            if pin_name in pin_direction_map[ref_name]['input']:
                return False  # Endpoint
            elif pin_name in pin_direction_map[ref_name]['output']:
                return True  # Startpoint
        return None  # Direction not determined
    else:
        return None

def get_top_level_module(parsed_objects):
    # Declare two sets to to identify top_level_module
    top_level_module = set(parsed_objects.keys())
    instantiated_modules = set()

    # Iterate through each module's instances
    for module_name, module_data in parsed_objects.items():
        # Remove instantiated modules from top-level modules
        instantiated_modules.update(instance['ref_name'] for instance in module_data.get('instances', []))

    top_level_module -= instantiated_modules

    return top_level_module   

def net_connectivity(parsed_objects):
    
    # DataFrame input
    rows = []

    # Get top level module
    top_level_module = get_top_level_module(parsed_objects)

    # Initialize the pin_direction_map for each module
    pin_direction_map = {module_name: {'input': [], 'output': []} for module_name in parsed_objects.keys()}
    
    for module_name, module_data in parsed_objects.items():

        # Iterate over the ports in the module to build pin_direction_map
        for port_direction, ports in module_data['ports'].items():
            pin_direction_map[module_name][port_direction].extend(ports)

        # Iterate through each module for pi and po
        for module_name, module_data in parsed_objects.items():
            is_top_level = module_name in top_level_module

            if is_top_level:
                # Identify SPs and EPs based on module type
                sp_ports = module_data['ports'].get('input', [])
                ep_ports = module_data['ports'].get('output', [])
            else:
                sp_ports = module_data['ports'].get('output', [])
                ep_ports = module_data['ports'].get('input', [])

            # Iterate through primary inputs (PIs) and assign them as startpoints for corresponding nets
            for pi_port in sp_ports:
                pi_net_name = pi_port['name']
                pi_net_identifier = f"{module_name}.{pi_net_name}"
                rows.append({"Module": module_name, "Net": pi_net_name, "Startpoint": pi_net_identifier, "Endpoint": "", "Fanout": 0})

            # Iterate through primary outputs (POs) and assign them as endpoints for corresponding nets
            for po_port in ep_ports:
                po_net_name = po_port['name']
                po_net_identifier = f"{module_name}.{po_net_name}"
                rows.append({"Module": module_name, "Net": po_net_name, "Startpoint": "", "Endpoint": po_net_identifier, "Fanout": 0})
        
            # Iterate through instances
            for instance_data in module_data.get("instances", []):
                instance_name = instance_data.get("instance", "")
                ref_name = instance_data.get("ref_name", "")
                cell_type = instance_data.get("cell_type", "")
                instance_name_with_ref = f"{ref_name} {instance_name}"

                # Check pin directions for hierarchical cell types
                if cell_type == 'hierarchical':
                    for pin_data in instance_data.get("pins", []):
                        pin_name = pin_data.get("name", "")
                        direction = check_pin_direction(pin_name, ref_name, cell_type, pin_direction_map)
                        if direction is not None:
                            is_startpoint = direction
                            is_endpoint = not direction
                            pin_net = pin_data.get("net", "")
                            pin_identifier = f"{instance_name_with_ref}.{pin_name}"
                            # Append data to the list
                            if is_startpoint:
                                rows.append({"Module": module_name, "Net": pin_net, "Startpoint": pin_identifier, "Endpoint": ""})
                            elif is_endpoint:
                                rows.append({"Module": module_name, "Net": pin_net, "Startpoint": "", "Endpoint": pin_identifier})
                else:
                    # Continue with the existing code for leaf-level cells
                    # Iterate through pins
                    for pin_data in instance_data.get("pins", []):
                        pin_name = pin_data.get("name", "")
                        pin_net = pin_data.get("net", "")
                        pin_identifier = f"{instance_name_with_ref}.{pin_name}"
                        direction = check_pin_direction(pin_name, ref_name, cell_type, pin_direction_map)
                        # If cell_type == 'leaf-level' and pin not in ['Z','Q'] direction is True (return value)
                        # pin is a startpoint
                        if direction is not None:
                            is_startpoint = direction
                            is_endpoint = not direction
                            # Append data to the list
                            if is_startpoint:
                                rows.append({"Module": module_name, "Net": pin_net, "Startpoint": pin_identifier, "Endpoint": ""})
                            elif is_endpoint:
                                rows.append({"Module": module_name, "Net": pin_net, "Startpoint": "", "Endpoint": pin_identifier})

    # Create a DataFrame from the list of rows
    df_result = pd.DataFrame(rows)

    # Filter out rows with empty values in 'Startpoint' or 'Endpoint'
    df_result_filtered = df_result[(df_result['Startpoint'] != "") | (df_result['Endpoint'] != "")]

    # Group by 'Module', 'Net' and aggregate non-empty values in 'Startpoint' and 'Endpoint' into lists
    grouped_df = df_result_filtered.groupby(['Module', 'Net'])
    aggregated_df = grouped_df.agg(lambda x: list(filter(None, x))).reset_index()

    # Calculate the count of the endpoint list for each net and add the value to the 'Fanout' column for each row
    aggregated_df['Fanout'] = aggregated_df.apply(lambda row: len(row['Endpoint']), axis=1)

    return aggregated_df

def save_to_excel(dataframe):

    # Save the DataFrame to Excel files
    try:
        dataframe.to_excel('output_2/dataframe_module_merged.xlsx', index=False)
        messagebox.showinfo("Info", "Data saved to Excel successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving data to Excel: {str(e)}")

def main():
    try:
        input_file_path = get_file_path_json()

        # Read data from the JSON file
        with open(input_file_path, 'r') as file:
            parsed_objects_list = json.load(file)

        # Convert the list to a dictionary where keys are module names
        parsed_objects = {module_data['module_name']: module_data for module_data in parsed_objects_list}

        # Process parsed_objects using the function
        connectivity_table = net_connectivity(parsed_objects)

        # Save to excel
        save_to_excel(connectivity_table)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
