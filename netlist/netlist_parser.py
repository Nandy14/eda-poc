import os
import re
import traceback
from dotenv import load_dotenv
import logging
# import networkx as nx
# import matplotlib.pyplot as plt
# import numpy as np
import pickle
from netlist_query import add_new_query, view_query, execute_query
from netlist_models import VerilogModule, VerilogInstance, VerilogPort, VerilogPin, VerilogNet, MODULE_PATTERN, INSTANCE_PATTERN, PIN_PATTERN, PORT_PATTERN, NET_PATTERN, GraphNode
from netlist_utils import determine_cell_type, generate_verilog, get_file_path, update_net_objects_with_connectivity, load_from_json, save_to_json_file, parse_netlist_hierarchy_module_template
from collections import defaultdict
from netlist_connectivity import net_connectivity


# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(filename='verilog_parser.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Don't modify this, in case of new feature, copy this and comment it out, create new copy
def parse_netlist_test(file_path, modules_templates):
    """
    Parses a Verilog netlist file and constructs a list of VerilogModule objects.

    This function reads a Verilog netlist file and extracts information about modules,
    ports, nets, and instances within each module. It creates VerilogModule objects,
    each containing details about its ports, nets, and instances. The function handles
    module declarations, port definitions, net declarations, and instance declarations,
    including the connections of instance pins to nets or constants.

    Args:
        file_path (str): The path to the Verilog netlist file.

    Returns:
        List[VerilogModule]: A list of VerilogModule objects representing the modules
                             found in the netlist file. Each module object contains
                             detailed information about its internal structure.
    """

    # Function Implementation
    
    print('\ndef parse_netlist: is called.\n')
    logging.info('def parse_netlist function called.')

    modules = []  # List to store the VerilogModule objects
    current_module = None  # Current module being parsed
    inside_instance = False  # Flag to track if we are parsing inside an instance
    instance = None  # Current instance being parsed

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        modules = []
        current_module = None
        inside_instance = False
        instance = None

        for line in lines:

            if line.strip().startswith('//') or not line:
                continue
            
            # Check for module declaration
            if line.strip().startswith('module'):
                module_name = MODULE_PATTERN.search(line).group(1)
                print(f"Module found : {module_name}")
                logging.info("Module found : %s", module_name)
                current_module = VerilogModule(module_name)
                modules.append(current_module)
                continue  # Skip to the next line

            # If we are inside a module, parse its contents
            if current_module:

                # Parse ports
                port_matches = PORT_PATTERN.findall(line)
                for port_match in port_matches:
                    direction, width, port_names = port_match[0], port_match[1], port_match[2]
                    # Split port names by commas and strip whitespace
                    port_names = [name.strip() for name in port_names.split(',')]
                    for port_name in port_names:
                        if width:
                            print(f"{direction} Port found : {port_name} width {width}")
                            logging.info("%s Port found : %s width %s.", direction, port_name, width)
                        else:
                            print(f"{direction} Port found : {port_name} width None")
                            logging.info("%s Port found : %s width %s.", direction, port_name, width)
                        current_module.ports[direction].append(VerilogPort(port_name, direction, width, ))

                # Parse declared nets
                net_matches = NET_PATTERN.findall(line)
                for net_group in net_matches:
                    # Split the group by commas to get individual net declarations
                    net_declarations = [decl.strip() for decl in net_group.split(',')]
                    prev_width = None  # Variable to store the width from the previous net declaration
                    for net_decl in net_declarations:
                        # Check if the net has a width declaration
                        width_match = re.match(r'(\[\d+:\d+\])?\s*(\w+)', net_decl)
                        if width_match:
                            width, net_name = width_match.groups()
                            if not width and prev_width:
                                # If width is not specified for this net, use the width from the previous net
                                width = prev_width
                                start, end = map(int, re.findall(r'\d+', width))
                                net_obj = VerilogNet(net_name, "wire", (start, end))
                            elif width:
                                # Update the previous width for subsequent nets
                                prev_width = width
                                start, end = map(int, re.findall(r'\d+', width))
                                net_obj = VerilogNet(net_name, "wire", (start, end))
                            else:
                                net_obj = VerilogNet(net_name, "wire", None)
                        else:
                            raise ValueError(f"Error parsing netlist file: invalid net declaration - {net_decl}")

                        print(f"New net created: {net_name}" + (f" with width {width}" if width_match else ""))
                        logging.info("New net created: %s" + (f" with width {width}" if width_match else ""), net_name)
                        current_module.nets.append(net_obj)

                # Parse instance declarations
                instance_match = INSTANCE_PATTERN.search(line)
                if instance_match:
                    ref_name, instance_name = instance_match.groups()
                    print(f"Instance found : {instance_name}")
                    logging.info("Instance found : %s", instance_name)
                    cell_type = determine_cell_type(ref_name, modules_templates)

                    instance = VerilogInstance(instance_name, cell_type , ref_name)
                    current_module.instances.append(instance)
                    inside_instance = True

                # If inside an instance declaration, match pins
                if inside_instance:
                    print(f"Inside instance: {instance_name}")
                    logging.info("Inside instance: %s", instance_name)
                    pin_matches = PIN_PATTERN.findall(line)
                    # Inside instance, after matching pins
                    for pin_match in pin_matches:
                        pin_name, net_name_instance = pin_match
                        print(f"pin found : {pin_name}")
                        logging.info("pin found : %s", pin_name)
                        print(f"net found : {net_name_instance.strip()}")
                        logging.info("net found : %s", net_name_instance.strip())
                        # Remove any surrounding whitespace and parentheses
                        net_name_instance = net_name_instance.strip()

                        net_obj = None

                        # Handle bit-indexed nets and constants
                        # Could also contain port-derived nets
                        if net_name_instance.endswith(']'):
                            # Extract the base net name and index for bit-indexed nets
                            base_net_name_match = re.match(r"([a-zA-Z_]\w*)\[(\d+)(?::(\d+))?\]", net_name_instance)
                            if base_net_name_match:
                                base_net_name = base_net_name_match.group(1)
                                start_index = int(base_net_name_match.group(2))
                                end_index = int(base_net_name_match.group(3)) if base_net_name_match.group(3) else None
                            else:
                                base_net_name = net_name_instance
                                start_index = None
                                end_index = None

                            # Fix variable names in print and logging statements
                            print(f"Extracted net name, start_index, end_index: {base_net_name}, {start_index}, {end_index}")
                            logging.info("Extracted net name, start_index, end_index: %s, %s, %s", base_net_name, start_index, end_index)

                            # Check if the base net name is already a declared and a parsed net
                            net_obj = next((net for net in current_module.nets if net.net_type == 'wire' and net.name == base_net_name), None)
                            
                            # Already declared and parsed net
                            if net_obj:
                                print(f"Already declared and parsed net : {base_net_name}")
                                logging.info("Already declared and parsed net : %s", base_net_name)
                                # This condition is added because some nets have the same name as Ports, 
                                # But they are not port-derived nets, they are explicitly declared nets connected to ports.
                                # For such nets we need to add them to the ports they are connected to
                                # There could be a case mismatch. Comparing by ignoring case
                                port_obj = next((port for port in current_module.ports['input'] + current_module.ports['output'] if port.name.lower() == base_net_name.lower()), None)
                                if port_obj is None:
                                    print(f'No matching port found for declared net {net_name_instance} \nContinue creating pin {pin_name}')
                                    logging.info("No matching port found for declared net %s \nContinue creating pin %s", net_name_instance, pin_name)
                                    net_obj = VerilogNet(f"{net_name_instance}", "wire-single", (1,0))
                                    print(f'Created a VerilogNet object for {net_name_instance}')
                                    logging.info("Created a VerilogNet object for %s", net_name_instance)
                                else:
                                    print(f'Found a port name matching a wire net, connecting and adding the net {net_name_instance} to the port {port_obj}')
                                    logging.info("Found a port name matching a wire net, connecting and adding the net %s to the port %s", net_name_instance, port_obj)
                                    net_obj = VerilogNet(f"{net_name_instance}", "wire-single", (1,0))
                                    print(f'Created a VerilogNet object for {net_name_instance}')
                                    logging.info("Created a VerilogNet object for %s", net_name_instance)
                                    port_obj.net.append(net_obj)
                                    print(f'Added the net object to the module ports')
                                    logging.info("Added the net object to the module ports")
                            else:
                                print(f"Not a declared or parsed net")
                                logging.info("Not a declared or parsed net")
                        elif "'" in net_name_instance:
                            print(f'Net name with a constant found {net_name_instance}')
                            logging.info("Net name with a constant found %s", net_name_instance)
                            # Handle constants like 1'b0
                            print(f"Pin {pin_name} connected to a constant {net_name_instance}")
                            logging.info("Pin %s connected to a constant %s", pin_name, net_name_instance)
                            net_obj = VerilogNet(f"{net_name_instance}", "constant", None)
                            print(f'Created a VerilogNet object for {net_name_instance}')
                            logging.info("Created a VerilogNet object for %s", net_name_instance)
                        else:
                            # Check if the net name is one of the module's ports
                            if net_name_instance in [port.name for port in current_module.ports['input'] + current_module.ports['output']]:
                                # It's a port-derived net
                                print('It is a port-derived net')
                                logging.info("It is a port-derived net")
                                port_obj = next((port for port in current_module.ports['input'] + current_module.ports['output'] if port.name == net_name_instance), None)
                                if port_obj:
                                    net_obj = VerilogNet(net_name_instance, "port-derived", (1,0))
                                    print(f'Created a VerilogNet object : {net_name_instance}')
                                    logging.info("Created a VerilogNet object : %s", net_name_instance)
                                    current_module.nets.append(net_obj)
                                    print(f'Added the net object to the module.nets')
                                    logging.info("Added the net object to the module.nets")
                                    port_obj.net.append(net_obj)
                                    print(f'Added the net object to the module ports')
                                    logging.info("Added the net object to the module ports")
                            else:
                                # Handle regular nets
                                net_obj = next((net for net in current_module.nets if net.name == net_name_instance), None)

                        # If no net object was found, it might be a port-derived net 
                        # Port-derived nets
                        if not net_obj:

                            '''
                            Caution! : This section was commented out due to changes made to the parser. 
                            The following commented code has been commented out to parse nets in pin declarations 
                            of the type X[i:j].
                            '''
                            # base_net_name = re.match(r"([a-zA-Z_]\w*)\[\d+\]", net_name_instance)
                            # if base_net_name:
                            #     base_net_name = base_net_name.group(1)
                            # else:
                            #     base_net_name = net_name_instance

                            # Check for ports with the same name as the net
                            port_obj = next((port for port in current_module.ports["input"] + current_module.ports["output"] if port.name == base_net_name), None)
                            if port_obj:
                                print('It is a port-derived net')
                                logging.info('It is a port-derived net')
                                print(f"{instance_name} Pin {pin_name} connected to port-derived Net {net_name_instance}")
                                logging.info("%s Pin %s connected to port-derived Net %s", instance_name, pin_name, net_name_instance)
                                net_obj = VerilogNet(net_name_instance, "port-derived", (1,0))
                                print(f"New port-derived Net {net_name_instance} created")
                                logging.info("New port-derived Net %s created", net_name_instance)
                                current_module.nets.append(net_obj)
                                print(f'Port-derived Net {net_name_instance} added to current module.nets')
                                logging.info("Port-derived Net %s added to current module.nets", net_name_instance)
                                port_obj.net.append(net_obj)  # Link the port to its derived net
                                print(f' Net {net_name_instance} added to port_obj')
                                logging.info("Net %s added to port_obj", net_name_instance)
                            else:
                                print(f"No net found for {instance_name} Pin {pin_name} connected to {net_name_instance}")
                                logging.info("No net found for %s Pin %s connected to %s", instance_name, pin_name, net_name_instance)                                

                        pin = VerilogPin(pin_name, instance, net_obj)
                        # Increment fanout when connecting a pin to a net
                        if net_obj:
                            if pin_name not in ['Z','Q']:
                                net_obj.increment_fanout()                        
                        instance.pins.append(pin)
                    
                    # Check if this is the end of the instance declaration
                    if ');' in line:
                        inside_instance = False                

            # Check for end of module
            if 'endmodule' in line:
                logging.info("End of module: %s", current_module.name)
                print(f"End of module: {current_module.name}")
                current_module = None

        return modules
    
    except Exception as e:
        error_message = f"Error parsing netlist file: {e}"
        logging.error(error_message)
        print(error_message)
        raise ValueError(error_message)

# def parse_netlist_test(file_path, modules_templates):
#     """
#     Parses a Verilog netlist file and constructs a list of VerilogModule objects.

#     This function reads a Verilog netlist file and extracts information about modules,
#     ports, nets, and instances within each module. It creates VerilogModule objects,
#     each containing details about its ports, nets, and instances. The function handles
#     module declarations, port definitions, net declarations, and instance declarations,
#     including the connections of instance pins to nets or constants.

#     Args:
#         file_path (str): The path to the Verilog netlist file.

#     Returns:
#         List[VerilogModule]: A list of VerilogModule objects representing the modules
#                              found in the netlist file. Each module object contains
#                              detailed information about its internal structure.
#     """

#     # Function Implementation
    
#     print('\ndef parse_netlist: is called.\n')
#     logging.info('def parse_netlist function called.')

#     modules = []  # List to store the VerilogModule objects
#     current_module = None  # Current module being parsed
#     inside_instance = False  # Flag to track if we are parsing inside an instance
#     instance = None  # Current instance being parsed

#     try:
#         with open(file_path, 'r') as f:
#             lines = f.readlines()

#         modules = []
#         current_module = None
#         inside_instance = False
#         instance = None

#         for line in lines:

#             if line.strip().startswith('//') or not line:
#                 continue
            
#             # Check for module declaration
#             if line.strip().startswith('module'):
#                 module_name = MODULE_PATTERN.search(line).group(1)
#                 print(f"Module found : {module_name}")
#                 logging.info("Module found : %s", module_name)
#                 current_module = VerilogModule(module_name)
#                 modules.append(current_module)
#                 continue  # Skip to the next line

#             # If we are inside a module, parse its contents
#             if current_module:
#                 # Parse ports
#                 port_matches = PORT_PATTERN.findall(line)
#                 for port_match in port_matches:
#                     direction, width, port_names = port_match[0], port_match[1], port_match[2]
#                     # Split port names by commas and strip whitespace
#                     port_names = [name.strip() for name in port_names.split(',')]
#                     for port_name in port_names:
#                         if width:
#                             print(f"{direction} Port found : {port_name} width {width}")
#                             logging.info("%s Port found : %s width %s.", direction, port_name, width)
#                         else:
#                             print(f"{direction} Port found : {port_name} width None")
#                             logging.info("%s Port found : %s width %s.", direction, port_name, width)
#                         current_module.ports[direction].append(VerilogPort(port_name, direction, width, ))

#                 # Parse declared nets
#                 net_matches = NET_PATTERN.findall(line)
#                 for net_group in net_matches:
#                     # Split the group by commas to get individual net declarations
#                     net_declarations = [decl.strip() for decl in net_group.split(',')]
#                     prev_width = None  # Variable to store the width from the previous net declaration
#                     for net_decl in net_declarations:
#                         # Check if the net has a width declaration
#                         width_match = re.match(r'(\[\d+:\d+\])?\s*(\w+)', net_decl)
#                         if width_match:
#                             width, net_name = width_match.groups()
#                             if not width and prev_width:
#                                 # If width is not specified for this net, use the width from the previous net
#                                 width = prev_width
#                                 start, end = map(int, re.findall(r'\d+', width))
#                                 net_obj = VerilogNet(net_name, "wire", (start, end))
#                             elif width:
#                                 # Update the previous width for subsequent nets
#                                 prev_width = width
#                                 start, end = map(int, re.findall(r'\d+', width))
#                                 net_obj = VerilogNet(net_name, "wire", (start, end))
#                             else:
#                                 net_obj = VerilogNet(net_name, "wire", None)
#                         else:
#                             raise ValueError(f"Error parsing netlist file: invalid net declaration - {net_decl}")

#                         print(f"New net created: {net_name}" + (f" with width {width}" if width_match else ""))
#                         logging.info("New net created: %s" + (f" with width {width}" if width_match else ""), net_name)
#                         current_module.nets.append(net_obj)

#                 # Parse instance declarations
#                 instance_match = INSTANCE_PATTERN.search(line)
#                 if instance_match:
#                     ref_name, instance_name = instance_match.groups()
#                     print(f"Instance found : {instance_name}")
#                     logging.info("Instance found : %s", instance_name)
#                     cell_type = determine_cell_type(ref_name, modules_templates)

#                     instance = VerilogInstance(instance_name, cell_type , ref_name)
#                     current_module.instances.append(instance)
#                     inside_instance = True

#                 # If inside an instance declaration, match pins
#                 if inside_instance:
#                     print(f"Inside instance: {instance_name}")
#                     logging.info("Inside instance: %s", instance_name)
#                     pin_matches = PIN_PATTERN.findall(line)
#                     # Inside instance, after matching pins
#                     for pin_match in pin_matches:
#                         pin_name, net_name_instance = pin_match
#                         print(f"pin found : {pin_name}")
#                         logging.info("pin found : %s", pin_name)
#                         print(f"net found : {net_name_instance.strip()}")
#                         logging.info("net found : %s", net_name_instance.strip())
#                         # Remove any surrounding whitespace and parentheses
#                         net_name_instance = net_name_instance.strip()

#                         net_obj = None

#                         # Handle bit-indexed nets and constants
#                         # Could also contain port-derived nets
#                         if net_name_instance.endswith(']'):
#                             # Extract the base net name and index for bit-indexed nets
#                             base_net_name_match = re.match(r"([a-zA-Z_]\w*)\[(\d+)(?::(\d+))?\]", net_name_instance)
#                             if base_net_name_match:
#                                 base_net_name = base_net_name_match.group(1)
#                                 start_index = int(base_net_name_match.group(2))
#                                 end_index = int(base_net_name_match.group(3)) if base_net_name_match.group(3) else None
#                             else:
#                                 base_net_name = net_name_instance
#                                 start_index = None
#                                 end_index = None

#                             # Fix variable names in print and logging statements
#                             print(f"Extracted net name, start_index, end_index: {base_net_name}, {start_index}, {end_index}")
#                             logging.info("Extracted net name, start_index, end_index: %s, %s, %s", base_net_name, start_index, end_index)

#                             # Check if the base net name is already a declared and a parsed net
#                             net_obj = next((net for net in current_module.nets if net.net_type == 'wire' and net.name == base_net_name), None)
                            
#                             # Already declared and parsed net
#                             if net_obj:
#                                 print(f"Already declared and parsed net : {base_net_name}")
#                                 logging.info("Already declared and parsed net : %s", base_net_name)
#                                 # This condition is added because some nets have the same name as Ports, 
#                                 # But they are not port-derived nets, they are explicitly declared nets connected to ports.
#                                 # For such nets we need to add them to the ports they are connected to
#                                 # There could be a case mismatch. Comparing by ignoring case
#                                 port_obj = next((port for port in current_module.ports['input'] + current_module.ports['output'] if port.name.lower() == base_net_name.lower()), None)
#                                 if port_obj is None:
#                                     print(f'No matching port found for declared net {net_name_instance} \nContinue creating pin {pin_name}')
#                                     logging.info("No matching port found for declared net %s \nContinue creating pin %s", net_name_instance, pin_name)
#                                     net_obj = VerilogNet(f"{net_name_instance}", "wire-single", (1,0))
#                                     print(f'Created a VerilogNet object for {net_name_instance}')
#                                     logging.info("Created a VerilogNet object for %s", net_name_instance)
#                                 else:
#                                     print(f'Found a port name matching a wire net, connecting and adding the net {net_name_instance} to the port {port_obj}')
#                                     logging.info("Found a port name matching a wire net, connecting and adding the net %s to the port %s", net_name_instance, port_obj)
#                                     # net_obj = VerilogNet(f"{net_name_instance}", "wire-single", (1,0))
#                                     # print(f'Created a VerilogNet object for {net_name_instance}')
#                                     # logging.info("Created a VerilogNet object for %s", net_name_instance)
#                                     port_obj.net.append(net_obj)
#                                     print(f'Added the net object to the module ports')
#                                     logging.info("Added the net object to the module ports")
#                             else:
#                                 print(f"Not a declared or parsed net")
#                                 logging.info("Not a declared or parsed net")
#                         elif "'" in net_name_instance:
#                             print(f'Net name with a constant found {net_name_instance}')
#                             logging.info("Net name with a constant found %s", net_name_instance)
#                             # Handle constants like 1'b0
#                             print(f"Pin {pin_name} connected to a constant {net_name_instance}")
#                             logging.info("Pin %s connected to a constant %s", pin_name, net_name_instance)
#                             net_obj = VerilogNet(f"{net_name_instance}", "constant", None)
#                             print(f'Created a VerilogNet object for {net_name_instance}')
#                             logging.info("Created a VerilogNet object for %s", net_name_instance)
#                         else:
#                             # Check if the net name is one of the module's ports
#                             if net_name_instance in [port.name for port in current_module.ports['input'] + current_module.ports['output']]:
#                                 # It's a port-derived net
#                                 print('It is a port-derived net')
#                                 logging.info("It is a port-derived net")
#                                 port_obj = next((port for port in current_module.ports['input'] + current_module.ports['output'] if port.name == net_name_instance), None)
#                                 if port_obj:
#                                     net_obj = VerilogNet(net_name_instance, "port-derived", (1,0))
#                                     print(f'Created a VerilogNet object : {net_name_instance}')
#                                     logging.info("Created a VerilogNet object : %s", net_name_instance)
#                                     current_module.nets.append(net_obj)
#                                     print(f'Added the net object to the module.nets')
#                                     logging.info("Added the net object to the module.nets")
#                                     port_obj.net.append(net_obj)
#                                     print(f'Added the net object to the module ports')
#                                     logging.info("Added the net object to the module ports")
#                             else:
#                                 # Handle regular nets
#                                 net_obj = next((net for net in current_module.nets if net.name == net_name_instance), None)

#                         # If no net object was found, it might be a port-derived net 
#                         # Port-derived nets
#                         if not net_obj:
#                             '''
#                             Caution! : This section was commented out due to changes made to the parser. 
#                             The following commented code has been commented out to parse nets in pin declarations 
#                             of the type X[i:j].
#                             '''
#                             # base_net_name = re.match(r"([a-zA-Z_]\w*)\[\d+\]", net_name_instance)
#                             # if base_net_name:
#                             #     base_net_name = base_net_name.group(1)
#                             # else:
#                             #     base_net_name = net_name_instance

#                             # Check for ports with the same name as the net
#                             port_obj = next((port for port in current_module.ports["input"] + current_module.ports["output"] if port.name == base_net_name), None)
#                             if port_obj:
#                                 print('It is a port-derived net')
#                                 logging.info('It is a port-derived net')
#                                 print(f"{instance_name} Pin {pin_name} connected to port-derived Net {net_name_instance}")
#                                 logging.info("%s Pin %s connected to port-derived Net %s", instance_name, pin_name, net_name_instance)
#                                 net_obj = VerilogNet(net_name_instance, "port-derived", (1,0))
#                                 print(f"New port-derived Net {net_name_instance} created")
#                                 logging.info("New port-derived Net %s created", net_name_instance)
#                                 current_module.nets.append(net_obj)
#                                 print(f'Port-derived Net {net_name_instance} added to current module.nets')
#                                 logging.info("Port-derived Net %s added to current module.nets", net_name_instance)
#                                 port_obj.net.append(net_obj)  # Link the port to its derived net
#                                 print(f' Net {net_name_instance} added to port_obj')
#                                 logging.info("Net %s added to port_obj", net_name_instance)
#                             else:
#                                 print(f"No net found for {instance_name} Pin {pin_name} connected to {net_name_instance}")
#                                 logging.info("No net found for %s Pin %s connected to %s", instance_name, pin_name, net_name_instance)                                

#                         pin = VerilogPin(pin_name, instance, net_obj)
#                         # Increment fanout when connecting a pin to a net
#                         if net_obj:
#                             if pin_name not in ['Z','Q']:
#                                 net_obj.increment_fanout()                        
#                         instance.pins.append(pin)
                    
#                     # Check if this is the end of the instance declaration
#                     if ');' in line:
#                         inside_instance = False                

#             # Check for end of module
#             if 'endmodule' in line:
#                 logging.info("End of module: %s", current_module.name)
#                 print(f"End of module: {current_module.name}")
#                 current_module = None

#         return modules

#     except Exception as e:
#         error_message = f"Error parsing netlist file: {e}"
#         logging.error(error_message)
#         print(error_message)
#         raise ValueError(error_message)

###################
# This is a test code. Not working. "COUT)" is getting parsed. ")" should be absent.
###################
# def parse_netlist_test(file_path, modules_templates):
#     """
#     Parses a Verilog netlist file and constructs a list of VerilogModule objects.

#     This function reads a Verilog netlist file and extracts information about modules,
#     ports, nets, and instances within each module. It creates VerilogModule objects,
#     each containing details about its ports, nets, and instances. The function handles
#     module declarations, port definitions, net declarations, and instance declarations,
#     including the connections of instance pins to nets or constants.

#     Args:
#         file_path (str): The path to the Verilog netlist file.

#     Returns:
#         List[VerilogModule]: A list of VerilogModule objects representing the modules
#                              found in the netlist file. Each module object contains
#                              detailed information about its internal structure.
#     """

#     # Function Implementation

#     print('\ndef parse_netlist: is called.\n')
#     logging.info('def parse_netlist function called.')

#     modules = []  # List to store the VerilogModule objects
#     current_module = None  # Current module being parsed
#     inside_instance = False  # Flag to track if we are parsing inside an instance
#     instance = None  # Current instance being parsed

#     try:
#         with open(file_path, 'r') as f:
#             lines = f.readlines()

#         modules = []
#         current_module = None
#         inside_instance = False
#         instance = None
#         file_iterator = iter(lines)  # Define the file iterator

#         for line in lines:

#             if line.strip().startswith('//') or not line:
#                 continue
            
#             # Check for module declaration
#             if line.strip().startswith('module'):
#                 # Check if the module declaration is on a single line or spans multiple lines
#                 module_declaration = line.strip()
#                 while not module_declaration.endswith(');'):
#                     line = next(file_iterator).strip()
#                     module_declaration += line

#                 # Extract the module name using the updated MODULE_PATTERN
#                 module_name = MODULE_PATTERN.search(module_declaration).group(1)
#                 print(f"Module found : {module_name}")
#                 logging.info("Module found : %s", module_name)
#                 current_module = VerilogModule(module_name)
#                 modules.append(current_module)
#                 continue  # Skip to the next line

#             # If we are inside a module, parse its contents
#             if current_module:
#                 # Check if the line contains an opening parenthesis
#                 if '(' in line:
#                     # Concatenate lines until the closing parenthesis is found
#                     while ')' not in line:
#                         line += next(file_iterator).strip()

#                 # Parse ports using the updated PORT_PATTERN
#                 port_matches = PORT_PATTERN.findall(line)
#                 if not port_matches:
#                     # If there are no matches, check the next line for ports defined separately
#                     line = next(file_iterator).strip()
#                     port_matches = PORT_PATTERN.findall(line)

#                 for port_match in port_matches:
#                     direction, width, port_names = port_match[0], port_match[1], port_match[2]
#                     # Split port names by commas and strip whitespace
#                     port_names = [name.strip() for name in port_names.split(',')]
#                     for port_name in port_names:
#                         if width:
#                             print(f"{direction} Port found : {port_name} width {width}")
#                             logging.info("%s Port found : %s width %s.", direction, port_name, width)
#                         else:
#                             print(f"{direction} Port found : {port_name} width None")
#                             logging.info("%s Port found : %s width %s.", direction, port_name, width)
#                         current_module.ports[direction].append(VerilogPort(port_name, direction, width, ))

#                 # Parse declared nets
#                 net_matches = NET_PATTERN.findall(line)
#                 for net_group in net_matches:
#                     # Split the group by commas to get individual net declarations
#                     net_declarations = [decl.strip() for decl in net_group.split(',')]
#                     prev_width = None  # Variable to store the width from the previous net declaration
#                     for net_decl in net_declarations:
#                         # Check if the net has a width declaration
#                         width_match = re.match(r'(\[\d+:\d+\])?\s*(\w+)', net_decl)
#                         if width_match:
#                             width, net_name = width_match.groups()
#                             if not width and prev_width:
#                                 # If width is not specified for this net, use the width from the previous net
#                                 width = prev_width
#                                 start, end = map(int, re.findall(r'\d+', width))
#                                 net_obj = VerilogNet(net_name, "wire", (start, end))
#                             elif width:
#                                 # Update the previous width for subsequent nets
#                                 prev_width = width
#                                 start, end = map(int, re.findall(r'\d+', width))
#                                 net_obj = VerilogNet(net_name, "wire", (start, end))
#                             else:
#                                 net_obj = VerilogNet(net_name, "wire", None)
#                         else:
#                             raise ValueError(f"Error parsing netlist file: invalid net declaration - {net_decl}")

#                         print(f"New net created: {net_name}" + (f" with width {width}" if width_match else ""))
#                         logging.info("New net created: %s" + (f" with width {width}" if width_match else ""), net_name)
#                         current_module.nets.append(net_obj)

#                 # Parse instance declarations
#                 instance_match = INSTANCE_PATTERN.search(line)
#                 if instance_match:
#                     ref_name, instance_name = instance_match.groups()
#                     print(f"Instance found : {instance_name}")
#                     logging.info("Instance found : %s", instance_name)
#                     cell_type = determine_cell_type(ref_name, modules_templates)

#                     instance = VerilogInstance(instance_name, cell_type , ref_name)
#                     current_module.instances.append(instance)
#                     inside_instance = True

#                 # If inside an instance declaration, match pins
#                 if inside_instance:
#                     print(f"Inside instance: {instance_name}")
#                     logging.info("Inside instance: %s", instance_name)
#                     pin_matches = PIN_PATTERN.findall(line)
#                     # Inside instance, after matching pins
#                     for pin_match in pin_matches:
#                         pin_name, net_name_instance = pin_match
#                         print(f"pin found : {pin_name}")
#                         logging.info("pin found : %s", pin_name)
#                         print(f"net found : {net_name_instance.strip()}")
#                         logging.info("net found : %s", net_name_instance.strip())
#                         # Remove any surrounding whitespace and parentheses
#                         net_name_instance = net_name_instance.strip()

#                         net_obj = None

#                         # Handle bit-indexed nets and constants
#                         # Could also contain port-derived nets
#                         if net_name_instance.endswith(']'):
#                             # Extract the base net name and index for bit-indexed nets
#                             base_net_name_match = re.match(r"([a-zA-Z_]\w*)\[(\d+)(?::(\d+))?\]", net_name_instance)
#                             if base_net_name_match:
#                                 base_net_name = base_net_name_match.group(1)
#                                 start_index = int(base_net_name_match.group(2))
#                                 end_index = int(base_net_name_match.group(3)) if base_net_name_match.group(3) else None
#                             else:
#                                 base_net_name = net_name_instance
#                                 start_index = None
#                                 end_index = None

#                             # Fix variable names in print and logging statements
#                             print(f"Extracted net name, start_index, end_index: {base_net_name}, {start_index}, {end_index}")
#                             logging.info("Extracted net name, start_index, end_index: %s, %s, %s", base_net_name, start_index, end_index)

#                             # Check if the base net name is already a declared and a parsed net
#                             net_obj = next((net for net in current_module.nets if net.net_type == 'wire' and net.name == base_net_name), None)
                            
#                             # Already declared and parsed net
#                             if net_obj:
#                                 print(f"Already declared and parsed net : {base_net_name}")
#                                 logging.info("Already declared and parsed net : %s", base_net_name)
#                                 # This condition is added because some nets have the same name as Ports, 
#                                 # But they are not port-derived nets, they are explicitly declared nets connected to ports.
#                                 # For such nets we need to add them to the ports they are connected to
#                                 # There could be a case mismatch. Comparing by ignoring case
#                                 port_obj = next((port for port in current_module.ports['input'] + current_module.ports['output'] if port.name.lower() == base_net_name.lower()), None)
#                                 if port_obj is None:
#                                     print(f'No matching port found for declared net {net_name_instance} \nContinue creating pin {pin_name}')
#                                     logging.info("No matching port found for declared net %s \nContinue creating pin %s", net_name_instance, pin_name)
#                                     net_obj = VerilogNet(f"{net_name_instance}", "wire-single", (1,0))
#                                     print(f'Created a VerilogNet object for {net_name_instance}')
#                                     logging.info("Created a VerilogNet object for %s", net_name_instance)
#                                 else:
#                                     print(f'Found a port name matching a wire net, connecting and adding the net {net_name_instance} to the port {port_obj}')
#                                     logging.info("Found a port name matching a wire net, connecting and adding the net %s to the port %s", net_name_instance, port_obj)
#                                     # net_obj = VerilogNet(f"{net_name_instance}", "wire-single", (1,0))
#                                     # print(f'Created a VerilogNet object for {net_name_instance}')
#                                     # logging.info("Created a VerilogNet object for %s", net_name_instance)
#                                     port_obj.net.append(net_obj)
#                                     print(f'Added the net object to the module ports')
#                                     logging.info("Added the net object to the module ports")
#                             else:
#                                 print(f"Not a declared or parsed net")
#                                 logging.info("Not a declared or parsed net")
#                         elif "'" in net_name_instance:
#                             print(f'Net name with a constant found {net_name_instance}')
#                             logging.info("Net name with a constant found %s", net_name_instance)
#                             # Handle constants like 1'b0
#                             print(f"Pin {pin_name} connected to a constant {net_name_instance}")
#                             logging.info("Pin %s connected to a constant %s", pin_name, net_name_instance)
#                             net_obj = VerilogNet(f"{net_name_instance}", "constant", None)
#                             print(f'Created a VerilogNet object for {net_name_instance}')
#                             logging.info("Created a VerilogNet object for %s", net_name_instance)
#                         else:
#                             # Check if the net name is one of the module's ports
#                             if net_name_instance in [port.name for port in current_module.ports['input'] + current_module.ports['output']]:
#                                 # It's a port-derived net
#                                 print('It is a port-derived net')
#                                 logging.info("It is a port-derived net")
#                                 port_obj = next((port for port in current_module.ports['input'] + current_module.ports['output'] if port.name == net_name_instance), None)
#                                 if port_obj:
#                                     net_obj = VerilogNet(net_name_instance, "port-derived", (1,0))
#                                     print(f'Created a VerilogNet object : {net_name_instance}')
#                                     logging.info("Created a VerilogNet object : %s", net_name_instance)
#                                     current_module.nets.append(net_obj)
#                                     print(f'Added the net object to the module.nets')
#                                     logging.info("Added the net object to the module.nets")
#                                     port_obj.net.append(net_obj)
#                                     print(f'Added the net object to the module ports')
#                                     logging.info("Added the net object to the module ports")
#                             else:
#                                 # Handle regular nets
#                                 net_obj = next((net for net in current_module.nets if net.name == net_name_instance), None)

#                         # If no net object was found, it might be a port-derived net 
#                         # Port-derived nets
#                         if not net_obj:
#                             '''
#                             Caution! : This section was commented out due to changes made to the parser. 
#                             The following commented code has been commented out to parse nets in pin declarations 
#                             of the type X[i:j].
#                             '''
#                             # base_net_name = re.match(r"([a-zA-Z_]\w*)\[\d+\]", net_name_instance)
#                             # if base_net_name:
#                             #     base_net_name = base_net_name.group(1)
#                             # else:
#                             #     base_net_name = net_name_instance

#                             # Check for ports with the same name as the net
#                             port_obj = next((port for port in current_module.ports["input"] + current_module.ports["output"] if port.name == base_net_name), None)
#                             if port_obj:
#                                 print('It is a port-derived net')
#                                 logging.info('It is a port-derived net')
#                                 print(f"{instance_name} Pin {pin_name} connected to port-derived Net {net_name_instance}")
#                                 logging.info("%s Pin %s connected to port-derived Net %s", instance_name, pin_name, net_name_instance)
#                                 net_obj = VerilogNet(net_name_instance, "port-derived", (1,0))
#                                 print(f"New port-derived Net {net_name_instance} created")
#                                 logging.info("New port-derived Net %s created", net_name_instance)
#                                 current_module.nets.append(net_obj)
#                                 print(f'Port-derived Net {net_name_instance} added to current module.nets')
#                                 logging.info("Port-derived Net %s added to current module.nets", net_name_instance)
#                                 port_obj.net.append(net_obj)  # Link the port to its derived net
#                                 print(f' Net {net_name_instance} added to port_obj')
#                                 logging.info("Net %s added to port_obj", net_name_instance)
#                             else:
#                                 print(f"No net found for {instance_name} Pin {pin_name} connected to {net_name_instance}")
#                                 logging.info("No net found for %s Pin %s connected to %s", instance_name, pin_name, net_name_instance)                                

#                         pin = VerilogPin(pin_name, instance, net_obj)
#                         # Increment fanout when connecting a pin to a net
#                         if net_obj:
#                             if pin_name not in ['Z','Q']:
#                                 net_obj.increment_fanout()                        
#                         instance.pins.append(pin)
                    
#                     # Check if this is the end of the instance declaration
#                     if ');' in line:
#                         inside_instance = False                

#             # Check for end of module
#             if 'endmodule' in line:
#                 logging.info("End of module: %s", current_module.name)
#                 print(f"End of module: {current_module.name}")
#                 current_module = None

#         return modules

#     except Exception as e:
#         error_message = f"Error parsing netlist file: {e}"
#         logging.error(error_message)
#         traceback.print_exc()  # This will print the traceback information to the console
#         print(error_message)
#         raise ValueError(error_message)

def create_graph(modules):
    graph_nodes = defaultdict(lambda: GraphNode("", ""))

    for module in modules:
        graph_nodes[module.name] = GraphNode(module.name, "Module")
        
        for port in module.ports['input'] + module.ports['output']:
            graph_nodes[port.name] = GraphNode(port.name, "Port")
            
        for net in module.nets:
            graph_nodes[net.name] = GraphNode(net.name, "Net")
            
        for instance in module.instances:
            graph_nodes[instance.name] = GraphNode(instance.name, "Instance")

    # for module in modules:
    #     # Connect VerilogPorts to VerilogNets
    #     for port in module.ports['input'] + module.ports['output']:
    #         for net in port.net:
    #             graph_nodes[port.name].edges.add(graph_nodes[net.name])

    #     # Connect VerilogNets to VerilogPins (instances)
    #     for net in module.nets:
    #         for pin in net.pins:
    #             graph_nodes[net.name].edges.add(graph_nodes[pin.instance.name])

    return graph_nodes

def main(input_netlist_file_path):
    """
    Main function to parse and verify a Verilog netlist file.

    This function orchestrates the parsing of a Verilog netlist file. It first extracts module templates,
    then parses instances, and finally parses the entire netlist into VerilogModule objects. It also
    verifies the parsed data for correctness.

    Args:
        file_path (str): Path to the Verilog netlist file.

    Returns:
        None
    """

    # Function Implementation
    logging.info('Main function called with file path: %s', input_netlist_file_path)
    print('\nMain function called with file path: %s\n', input_netlist_file_path)

    try:
        # Parse module templates from the netlist
        logging.info('Parsing module templates from the netlist.')
        modules_templates = parse_netlist_hierarchy_module_template(input_netlist_file_path)
        option = 0
        modules = []
        while True:
            print()
            print('###########################################################')
            print()
            print('######################## EDA POC ##########################')
            print()
            print('###########################################################')
            print()
            print()

            print('Choose from below : ')
            print()
            print('1. POC READ')
            print()
            print('2. POC WRITE')
            print()
            print('3. POC QUERY (Note: This feature will not work if executed before POC READ)')
            print()
            print('4. QUIT')
            print()
            option = int(input('Select option 1, 2, 3 or 4 : '))

            if option == 1:
                print('POC READ')
                
                if os.path.exists('json/parsed_objects.json'):
                    modules = load_from_json('json/parsed_objects.json')
                    print()
                    print('Modules were parsed and loaded from json, please proceed to POC WRITE\n')                    
                
                elif not os.path.exists('json/parsed_objects.json') and os.path.exists('pickle/netlist_pickle.pkl'):
                    print('Previous database not found, pickle file found, unpickling and parsing')
                    # Unpickle all lines from the pickled file
                    with open('pickle/netlist_pickle.pkl', 'rb+') as pickle_file:
                        unpickled_data = pickle.load(pickle_file)
                        # Save the unpickled data to a separate file
                        with open('input/netlist_unpickled.v.txt', 'w') as unpickled_file:
                            unpickled_file.writelines(unpickled_data)
                    print('Unpickling completed, Parsing file')
                    # modules = parse_netlist('pickle/netlist_unpickled.v.txt',modules_templates)
                    print('Generating json')
                    # After parsing is complete
                    for module in modules:
                        module.print_net_fanout()
                    save_to_json_file(modules)
                    print('Modules were parsed from pickled netlist file, JSON generated, please proceed to POC WRITE\n')

                elif not os.path.exists('json/parsed_objects.json') and not os.path.exists('pickle/netlist_pickle.pkl') and os.path.exists(input_netlist_file_path):
                    print('Previous database not found, pickle version not found, proceeding with input netlist file ')
                    # modules = parse_netlist(input_netlist_file_path,modules_templates)
                    modules = parse_netlist_test(input_netlist_file_path, modules_templates)
                    # Example usage
                    # fanout_table = create_fanout_table(input_netlist_file_path)
                    # print(fanout_table)
                    print()
                    print('Generating json')
                    # After parsing is complete
                    # for module in modules:
                    #     module.print_net_fanout()                    
                    save_to_json_file(modules)
                    print('Modules were written to json')                    
                    # imported the function from netlist_connectivity
                    # Let's call it
                    # net_connections = net_connectivity()
                    # updated_modules = update_net_objects_with_connectivity(net_connections,modules)
                    print('Modules were parsed from input netlist file, please proceed to POC WRITE\n')                    
                    # Creating Graph
                    # graph = create_graph(modules)
                    # print(graph)
                    # # Pickle the data
                    # pickled_data = '\n'.join(modules)
                    # with open('netlist_pickle.pkl', 'wb') as pickle_file:
                    #     pickle.dump(pickled_data, pickle_file)                                   
                else:
                    print('No appropriate netlist file found. Exiting')
                    break
            elif option == 2:
                print('POC WRITE')
                if modules:
                    # Generate the input file from the parsed objects
                    verilog_code = generate_verilog(modules)
                    with open("output/output_netlist_file.v", "w") as file:
                        file.write(verilog_code)                
                    print('Recreated input netlist from modules, file generated : output_netlist_file.v')             
                else:
                    print('Modules are not initialized, please run POC READ first\n')
            
            elif option == 3:
                print('3. POC QUERY')
                # Ensure the indentation is correct for the following code
                queries_list = []

                while True:
                    print("\nOptions:")
                    print("1. Query")
                    print("2. Quit")

                    option = input("Choose an option (1/2): ")

                    if option == '1':
                        while True:
                            print("\nSub-options:")
                            print("1. Add new query")
                            print("2. View queries")
                            print("3. Execute query")
                            print("4. Back to main menu")

                            sub_option = input("Choose a sub-option (1/2/3/4): ")

                            if sub_option == '1':
                                add_new_query(queries_list)
                                print('ADD')
                            elif sub_option == '2':
                                view_query(queries_list)
                                print('VIEW')
                            elif sub_option == '3':
                                execute_query(queries_list, modules)
                                print('EXECUTE')
                            elif sub_option == '4':
                                print('EXIT')
                                break
                            else:
                                print("Invalid sub-option! Please try again.")

                    elif option == '2':
                        print("Exiting program. Goodbye!")
                        break
                    else:
                        print("Invalid option! Please try again.")
                
            else:
                print('QUIT')
                break
        
        logging.info('Main function completed successfully.')
        print('Main function completed successfully.')

    except FileNotFoundError:
        logging.error("FileNotFoundError: The file '%s' was not found.", input_netlist_file_path)
        print(f"Error: The file '{input_netlist_file_path}' was not found.")
    except Exception as e:
        logging.error("Exception occurred: %s", e)
        print(f"An error occurred: {e}")

# Main Execution starts here
if __name__ == "__main__":
    
    # Use file selector to get the input file
    input_netlist_file_path = get_file_path()

    # Call the main function with the file path.
    main(input_netlist_file_path)

    # Summary report and logging functionality to be added
    # Action items regarding multiple sub designs.
    # 