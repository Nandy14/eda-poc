
import json
import logging
import os
import pickle
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from netlist_models import INSTANCE_PATTERN, MODULE_PATTERN, PIN_PATTERN, PORT_PATTERN, VerilogModule, VerilogPort, VerilogPin, VerilogInstance, VerilogNet
from tkinter import filedialog, messagebox

def generate_verilog(modules):
    verilog_code = ""
    for module in modules:
        # Module declaration
        verilog_code += f"module {module.name} (\n"
        for direction in module.ports:
            for port in module.ports[direction]:
                port_width = f"[{port.width[0]}:{port.width[1]}]" if port.width else ""
                verilog_code += f"    {direction} {port_width} {port.name},\n"
        verilog_code = verilog_code.rstrip(',\n') + "\n);\n\n"

        # Wire declarations
        for net in module.nets:
            if net.net_type == "wire":
                net_width = f"[{net.width[0]}:{net.width[1]}]" if net.width else ""
                verilog_code += f"    wire {net_width} {net.name};\n"

        # Instance declarations
        for instance in module.instances:
            verilog_code += f"    {instance.ref_name} {instance.name} ("
            pin_connections = []
            for pin in instance.pins:
                net_name = pin.net.name if pin.net else ""
                # Directly use the net name, as it now includes any indexing
                pin_connections.append(f".{pin.name}({net_name})")
            verilog_code += ", ".join(pin_connections) + ");\n"

        # # Assignment statements
        # for assignment in module.assignments:
        #     verilog_code += f"    {assignment}\n"

        verilog_code += "endmodule\n\n"

    return verilog_code

def verify_parser(modules):
    """
    Verifies and prints the parsed data from a list of VerilogModule objects.

    This function iterates through each VerilogModule object in the provided list,
    printing out details of the module, its ports, nets, and instances. For each
    instance, it also prints the details of its pins and their connections. This
    function is useful for verifying the correctness of the parsed data from a
    Verilog netlist file.

    Args:
        modules (List[VerilogModule]): A list of VerilogModule objects to be verified.

    Returns:
        None: This function does not return anything. It prints the verification details.

    Raises:
        TypeError: If the input is not a list of VerilogModule objects.
        ValueError: If any module, port, net, or instance is malformed.
    """
    # Function Implementation
    
    print('\ndef verify_parser: is called.\n')
    logging.info("verify_parser is called.")
    
    if not isinstance(modules, list):
        logging.error("Expected a list of VerilogModule objects, got %s", type(modules).__name__)
        raise TypeError("Expected a list of VerilogModule objects.")

    for module in modules:
        if not isinstance(module, VerilogModule):
            logging.error("Expected a VerilogModule object, got %s", type(module).__name__)
            raise ValueError("Expected a VerilogModule object.")

        print(f"<----Verifying parser---->")
        logging.info("<----Verifying parser---->")
        print(f"Module: {module.name}")
        logging.info("Module: %s", module.name)

        for direction, ports in module.ports.items():
            for port in ports:
                if not isinstance(port, VerilogPort):
                    logging.error("Expected a VerilogPort object, got %s", type(port).__name__)
                    raise ValueError("Expected a VerilogPort object.")
                print(f"  Port: {port.name}, Direction: {port.direction}, Width: {port.width} ")
                logging.info("  Port: %s, Direction: %s, Width: %s", port.name, port.direction, port.width)
                for net in port.net:
                    print(f"Port-Net : {net}")
                    logging.info("Port-Net : %s", net)

        for net in module.nets:
            if not isinstance(net, VerilogNet):
                logging.error("Expected a VerilogNet object, got %s", type(net).__name__)
                raise ValueError("Expected a VerilogNet object.")
            print(f"  Net: {net.name}, Type: {net.net_type}, Width: {net.width}")
            logging.info("  Net: %s, Type: %s, Width: %s", net.name, net.net_type, net.width)

        for instance in module.instances:
            if not isinstance(instance, VerilogInstance):
                logging.error("Expected a VerilogInstance object, got %s", type(instance).__name__)
                raise ValueError("Expected a VerilogInstance object.")
            print(f"  Instance: {instance.name}, Ref : {instance.ref_name}, Cell Type: {instance.cell_type}")
            logging.info("  Instance: %s, Ref : %s, Cell Type: %s", instance.name, instance.ref_name, instance.cell_type)

            for pin in instance.pins:
                connected_net = pin.net.name if pin.net else "None"
                print(f"    Pin: {pin.name}, Connected to: {connected_net}")
                logging.info("    Pin: %s, Connected to: %s", pin.name, connected_net)

def prepare_graph(modules):
    """
    Prepares data from modules for graph construction.

    Args:
        modules (List[VerilogModule]): A list of VerilogModule objects.

    Returns:
        List[Dict]: A list of dictionaries, each representing a module with its elements (ports, instances, nets)
                    and their connections.
    """
    graph_data = {'nodes': [], 'edges': []}

    for module in modules:
        # Add ports, instances, and nets as nodes
        for direction, ports in module.ports.items():
            for port in ports:
                port_id = f"{module.name}.{port.name}"
                graph_data['nodes'].append({'id': port_id, 'type': 'port', 'direction': direction})

        for instance in module.instances:
            instance_id = f"{module.name}.{instance.name}"
            graph_data['nodes'].append({'id': instance_id, 'type': 'instance'})

            for pin in instance.pins:
                pin_id = f"{instance_id}.{pin.name}"
                graph_data['nodes'].append({'id': pin_id, 'type': 'pin'})
                # Add edge from instance to pin
                graph_data['edges'].append({'from': instance_id, 'to': pin_id})

                if pin.net:
                    net_id = f"{module.name}.{pin.net.name}"
                    # Add edge from pin to net
                    graph_data['edges'].append({'from': pin_id, 'to': net_id})

        # for net in module.nets:
        #     net_id = f"{module.name}.{net.name}"
        #     graph_data['nodes'].append({'id': net_id, 'type': 'net'})

    return graph_data

def load_from_json(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
    
    modules = []
    for module_data in data:
        module = VerilogModule(module_data["module_name"])

        # Load ports
        for direction, ports in module_data["ports"].items():
            for port_data in ports:
                width = tuple(port_data["width"]) if port_data["width"] else None
                port = VerilogPort(port_data["name"], port_data["direction"], width)
                module.ports[direction].append(port)

        # Load nets
        net_dict = {}
        for net_data in module_data["nets"]:
            width = tuple(net_data["width"]) if net_data["width"] else None
            net = VerilogNet(net_data["name"], net_data["net_type"], width)
            module.nets.append(net)
            net_dict[net_data["name"]] = net

        # Load instances and pins
        for instance_data in module_data["instances"]:
            instance = VerilogInstance(instance_data["instance"], instance_data["cell_type"], instance_data["ref_name"])
            for pin_data in instance_data["pins"]:
                net_name = pin_data["net"]
                net = None

                # Handle constants
                if "'" in net_name:
                    net = VerilogNet(net_name, "constant", None)
                # Handle indexed nets as 'wire-sub'
                elif '[' in net_name:
                    net = VerilogNet(net_name, "wire-sub", None)
                # Handle regular nets
                else:
                    net = net_dict.get(net_name, None)

                if net is None:
                    print(f"Warning: Net '{net_name}' not found for pin '{pin_data['name']}' in instance '{instance.name}'.")

                pin = VerilogPin(pin_data["name"], instance, net, pin_data.get("direction"))
                instance.pins.append(pin)
            module.instances.append(instance)

        modules.append(module)
    
    return modules

def save_to_json_file(modules, file_name="json/parsed_objects.json"):
    modules_data = [module.to_dict() for module in modules]
    with open(file_name, 'w') as file:
        json.dump(modules_data, file, indent=4)

def print_module_details(module):
    print(f"Module: {module.name}")
    print("  Ports:")
    for direction, ports in module.ports.items():
        for port in ports:
            print(f"    {direction} - {port.name}, Width: {port.width}, Net: {port.net if port.net else ''}")

    print("  Instances:")
    for instance in module.instances:
        print(f"    Instance: {instance.name}, Cell Type: {instance.cell_type}, Reference: {instance.ref_name}")
        for pin in instance.pins:
            print(f"      Pin: {pin.name}, Net: {pin.net.name if pin.net else 'None'}")

    print("  Nets:")
    for net in module.nets:
        print(f"    Net: {net.name}, Type: {net.net_type}, Width: {net.width}")

def pickling_file(input_file_path, pickled_file_path='pickle/pickled_data.pkl', unpickled_file_path='unpickled_data.txt'):
    # Read the content of the input file line by line
    with open(input_file_path, 'r') as input_file:
        file_lines = input_file.readlines()

    # Pickle all lines and save them to a separate file with the highest protocol
    with open(pickled_file_path, 'wb+') as pickle_file:
        pickle.dump(file_lines, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

    # Print a message indicating that pickling is completed
    print(f"Pickling completed. Pickled data saved to: {pickled_file_path}")

    # Unpickle all lines from the pickled file
    with open(pickled_file_path, 'rb+') as pickle_file:
        unpickled_data = pickle.load(pickle_file)

    # # Display the unpickled data
    # print("Unpickled Data:")
    # for line in unpickled_data:
    #     print(line.strip())

    # Save the unpickled data to a separate file
    with open(unpickled_file_path, 'w') as unpickled_file:
        unpickled_file.writelines(unpickled_data)

    print(f"Unpickled data saved to: {unpickled_file_path}")

def verify_instance_declaration(instance, module_templates):
    """
    Verifies whether an instance declaration is valid based on the module templates.
    If the instance is not found in the templates, it is considered a leaf-level instance.

    Args:
        instance (dict): The instance declaration.
        module_templates (list): A list of module templates.

    Returns:
        bool: True if the instance declaration is valid, False otherwise.

    Raises:
        TypeError: If the input arguments are not of the expected type.
        KeyError: If required keys are missing in the input dictionaries.
    """
    # Function Implementation
    
    logging.info('Verifying instance declaration for instance: %s, %s', instance['ref_name'], instance['name'])
    print(f'Verifying instance declaration for instance: {instance["ref_name"]}, {instance["name"]}')

    if not isinstance(instance, dict) or not isinstance(module_templates, list):
        logging.error("Invalid input types for instance or module_templates. Instance type: %s, Module templates type: %s", type(instance).__name__, type(module_templates).__name__)
        print(f"Invalid input types for instance or module_templates. Instance type: {type(instance).__name__}, Module templates type: {type(module_templates).__name__}")
        raise TypeError("Invalid input types for instance or module_templates.")

    try:
        template = next((t for t in module_templates if t['name'] == instance['ref_name']), None)
        
        if not template:
            logging.info("Instance %s is a leaf-level instance or a library cell.", instance['name'])
            print(f"Instance {instance['name']} is a leaf-level instance or a library cell.")
            return True

        template_ports = {port['name']: port for direction in template['ports'] for port in template['ports'][direction]}
        for pin in instance['pins']:
            pin_name = pin['name']
            if pin_name not in template_ports:
                logging.error("Port %s in instance %s is not defined in module %s.", pin_name, instance['name'], template['name'])
                print(f"Error: Port {pin_name} in instance {instance['name']} is not defined in module {template['name']}.")
                return False

        logging.info("Instance %s verified successfully.", instance['name'])
        print(f"Instance {instance['name']} verified successfully.")
        return True

    except KeyError as e:
        logging.error("Missing key in instance or module template: %s", e)
        print(f"Missing key in instance or module template: {e}")
        raise KeyError(f"Missing key in instance or module template: {e}")

def validate_instances(lines, module_templates):
    """
    Parses instance declarations from a list of netlist lines and verifies each instance.

    This function iterates through each line of the netlist, searching for instance declarations.
    For each instance found, it extracts the instance name, ref_name, and pin connections.
    It then verifies the instance against the provided module templates. If the instance matches
    a module template, it checks if the instance's ports correspond to the template's ports.
    Instances not found in the module templates are considered valid, assuming they are leaf-level
    instances or library cells.

    Args:
        lines (list of str): The lines of the netlist file.
        module_templates (list of dict): A list of parsed module templates. Each template is a dictionary
                                         containing the module name and its ports.

    Returns:
        list of dict: A list of verified instances. Each instance is represented as a dictionary
                      containing the instance name, ref_name, and a list of pins. Each pin is
                      also a dictionary containing the pin name and the connected net.
    
    Raises:
        ValueError: If an instance declaration is malformed or cannot be parsed correctly.

    Note:
        The function prints a message for each invalid instance declaration it encounters.
    """
    # Function Implementation
    
    print('\ndef validate_instances: is called.\n')
    logging.info('defvalidate_instances function called.')

    instances = []  # Initialize an empty list to store instances

    # Iterate through each line in the netlist
    for line in lines:
        # Search for instance declarations in the line
        instance_match = INSTANCE_PATTERN.search(line)
        if instance_match:
            # Extract ref_name and instance name from the match
            ref_name, name = instance_match.groups()

            if ref_name == 'module':
                continue

            try:
                # Find all pin connections for this instance
                pins = PIN_PATTERN.findall(line)

                # Create a dictionary for the instance with its details
                instance = {
                    'name': name,
                    'ref_name': ref_name,
                    'pins': [{'name': pin, 'net': net} for pin, net in pins]
                }

                # Verify the instance against the module templates
                if verify_instance_declaration(instance, module_templates):
                    # If valid, add the instance to the instances list
                    instances.append(instance)
                    logging.info("Verified instance: %s", name)
                    print(f"Verified instance: {name}")
                else:
                    # If invalid, log and print an error message
                    logging.error("Invalid instance declaration: %s", name)
                    print(f"Invalid instance declaration: {name}")
            except Exception as e:
                error_message = f"Error parsing instance declaration in line: '{line}'. Error: {e}"
                logging.error(error_message)
                print(error_message)
                raise ValueError(error_message)

    return instances  # Return the list of verified instances

def determine_cell_type(ref_name, module_templates):
    # Define your logic to determine cell type based on reference name
    # For example, if the reference name matches the module name, it's hierarchical, otherwise, it's leaf-level
    if any(ref_name.lower() == template['name'].lower() for template in module_templates):
        return 'hierarchical'
    else:
        return 'leaf-level'

def parse_netlist_hierarchy_module_template(file_path):
    """
    Parses a Verilog netlist file to extract module templates, including their names and port definitions.

    This function reads a Verilog netlist file and identifies all module definitions within it. For each module,
    it extracts the module's name and its ports, including their names, directions (input/output), and optionally
    their widths. The function constructs a list of module templates, where each template is a dictionary
    containing the module's name and a dictionary of its ports categorized by direction.

    Args:
        file_path (str): The path to the netlist file to be parsed.

    Returns:
        module_templates (list of dict): A list of dictionaries, each representing a module template. 
                                         Each dictionary contains the module's name and a dictionary of its ports. 
                                         The ports dictionary categorizes ports into 'input' and 'output', with each entry being a list of 
                                         port information dictionaries.
                                         Each port information dictionary contains the port's name and optionally its width.

    Raises:
        FileNotFoundError: If the specified file_path does not exist.
        Exception: If the number of 'module' declarations does not match the number of 'endmodule' declarations,
                   indicating a potential syntax error in the netlist file.

    Note:
        The function uses regular expressions to identify module declarations and port definitions. It assumes
        a specific format for these declarations as per standard Verilog syntax. The function also prints the
        name of each module found during the parsing process.
    """
    # Function Implementation
    print('\ndef parse_netlist_hierarchy_module_template: is called.\n')
    logging.info("def parse_netlist_hierarchy_module_template is called.")
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        logging.error("The file at %s was not found.",file_path)
        raise FileNotFoundError(f"The file at {file_path} was not found.")

    module_templates = []  # List to store the module templates
    module_count = 0       # Counter for the number of 'module' declarations
    endmodule_count = 0    # Counter for the number of 'endmodule' declarations
    current_module = None  # Flag to indicate if currently parsing a module
    current_module_ports = {}  # Dictionary to store ports of the current module

    for line in lines:
        line = line.strip()  # Remove leading and trailing whitespaces

        if line.startswith('//') or not line:
            # Skip comments and empty lines
            continue

        module_match = re.search(MODULE_PATTERN, line)
        if module_match:
            module_name = module_match.group(1)  # Extract the module name
            module_count += 1
            current_module = module_name  # Set current module name
            current_module_ports = {}  # Initialize ports dictionary for the new module
            # print(f"Module found: {module_name}")
            logging.info("Module found: %s",module_name)
            continue

        if current_module:
            # Parse ports within the module
            port_matches = PORT_PATTERN.findall(line)
            for direction, width, port_names in port_matches:
                # Split port names by commas and strip whitespace
                port_names = [name.strip() for name in port_names.split(',')]
                for port_name in port_names:
                    logging.info("Port Found : %s", port_name)
                    port_info = {
                        "name": port_name,
                        "width": width.strip() if width else None  # Strip whitespace from width if it exists
                    }
                    # Add the port to the current module's ports dictionary
                    current_module_ports.setdefault(direction, []).append(port_info)


            if line.startswith("endmodule"):
                endmodule_count += 1
                # Add the parsed module to the module templates list
                module_templates.append({
                    "name": current_module,
                    "ports": current_module_ports
                })
                current_module = None  # Reset current module

    # Check if the number of module and endmodule declarations match
    if module_count != endmodule_count:
        logging.error("Mismatch in the number of 'module' and 'endmodule' declarations in the file.")
        raise Exception("Mismatch in the number of 'module' and 'endmodule' declarations in the file.")

    return module_templates

# Function to get the file path using a file selector dialog
def get_file_path():
    while True:
        if os.path.exists('json/parsed_objects.json'):
            file_path = 'json/parsed_objects.json'
            break
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        file_path = filedialog.askopenfilename(
            title="Select Netlist File",
            filetypes=[("Netlist Files", "*.v"), ("All Files", "*.*")]
        )

        # Check if the selected file has a valid extension
        if file_path and not file_path.lower().endswith((".v")):
            error_message = "Invalid file format. Please select a valid netlist file with a '.v' extension."
            messagebox.showerror("Error", error_message)
        else:
            break  # Break out of the loop if a valid file is selected

    return file_path

def update_net_objects_with_connectivity(net_connections, modules):

    for module in modules:

        # Update the connectivity information in VerilogNet objects
        for _, row in net_connections.iterrows():
            net_name = row["Net"]
            startpoint = row["Startpoint"]
            endpoints = row["Endpoint"]

            # print(net_name, startpoint, endpoint)
            # print()

            # Check if the base net name is already a declared and a parsed net
            net_obj = next((net for net in module.nets if net.name == net_name), None)

            if net_obj:
                print(f'Found a net object with the same name as {net_name}')                
                
                # Update the startpoint and endpoint of the net
                print('Add connectivity information to the net object')

                net_obj.connections['startpoint'] = startpoint
                net_obj.connections['endpoints'] = endpoints

            else:
                print('No net obj found. Abort')

            # Find the corresponding VerilogNet object
            # Assume nets are stored in a dictionary with net names as keys
            # if net_name in your_net_dictionary:
            #     verilog_net = your_net_dictionary[net_name]
                
            #     # Update connectivity information
            #     if startpoint:
            #         verilog_net.add_connection("startpoint", startpoint)
            #     elif endpoint:
            #         verilog_net.add_connection("endpoint", endpoint)

    for module in modules:
        for net in module.nets:            
            print(net)