import os
from netlist_models import VerilogNet

# Define the retrieve_all_modules function
def retrieve_all_modules(modules):
    with open('query_output_retrieve_all_modules.txt', 'w') as file:
        for module in modules:
            output = f"Module Name: {module.name}\n"
            print(output, end='')
            file.write(output)

# Similarly, modify other functions in the same way
        
def retrieve_ports_and_their_nets_with_port_derived_nets(modules):
    module_name = input("Enter the name of the module to retrieve ports and their nets: ")
    module = next((mod for mod in modules if mod.name == module_name), None)

    if module:
        print(f"Module: {module.name}")
        for direction, ports in module.ports.items():
            print(f"  Relationships for {direction} Port:")
            for port in ports:
                print(f"    Port: {port.name}")
                if port.net:
                    if isinstance(port.net, list):
                        print(f"    Connected Nets:")
                        for connected_net in port.net:
                            print(f"      Net: {connected_net.name}")
                    else:
                        print(f"    Connected Net: {port.net.name}")
                else:
                    print("    No connected nets.")
    else:
        print(f"Error: Module '{module_name}' not found.")

def retrieve_ports_and_their_nets_with_relationships_and_port_derived_nets(modules):
    module_name = input("Enter the name of the module to retrieve ports and their nets: ")
    module = next((mod for mod in modules if mod.name == module_name), None)

    with open('query_output_retrieve_ports_and_their_nets_with_relationships_and_port_derived_nets.txt', 'w') as file:
        if module:
            output = f"Module: {module.name}\n"
            file.write(output)
            print(output, end='')

            for direction, ports in module.ports.items():
                output = f"  Relationships for {direction} Port:\n"
                file.write(output)
                print(output, end='')

                for port in ports:
                    output = f"    Port: {port.name}\n"
                    file.write(output)
                    print(output, end='')

                    if port.net:
                        if isinstance(port.net, list):
                            output = f"    Connected Nets:\n"
                            file.write(output)
                            print(output, end='')

                            for connected_net in port.net:
                                output = f"      Net: {connected_net.name}\n"
                                file.write(output)
                                print(output, end='')
                        else:
                            output = f"    Connected Net: {port.net.name}\n"
                            file.write(output)
                            print(output, end='')
                    else:
                        output = "    No connected nets.\n"
                        file.write(output)
                        print(output, end='')
        else:
            output = f"Error: Module '{module_name}' not found.\n"
            file.write(output)
            print(output, end='')

def retrieve_modules_and_their_ports(modules):
    with open('query_retrieve_modules_and_their_ports','w') as file:
        for module in modules:
            output = f"\nModule: {module.name}"
            file.write(output)
            print(output)

            # Print Relationships
            f"\n  Ports:"
            for port_type, ports in module.ports.items():
                for port in ports:
                    print(f"    {port_type} Port: {port.name}")
                    # for net in port.net:
                    #     print(f"      Connected to Net: {net.name}")

def retrieve_modules_and_their_instances_with_pins(modules):
    for module in modules:
        print(f"\nModule: {module.name}")

        # Print Relationships
        print("  Instances:")
        for instance in module.instances:
            print(f"    Instance: {instance.name}")
            for pin in instance.pins:
                print(f"      Pin: {pin.name} (Connected to Net: {pin.net.name})")

def retrieve_modules_and_their_ports_and_nets(modules):
    for module in modules:
        print(f"\nModule: {module.name}")
        
        # Print Ports
        print("  Ports:")
        for port_direction, ports in module.ports.items():
            for port in ports:
                print(f"    {port_direction} Port: {port.name}")
        
        # Print Nets
        print("  Nets:")
        for net in module.nets:
            print(f"    Net: {net.name} ({net.net_type})")
        
        # # Print Relationships
        # print("  Instances and Pins:")
        # for instance in module.instances:
        #     print(f"    Instance: {instance.name}")
        #     for pin in instance.pins:
        #         print(f"      Pin: {pin.name} (Connected to Net: {pin.net.name})")

def retrieve_ports_and_their_connected_nets(modules):
    for module in modules:
        print(f"\nModule: {module.name}")
        for port_direction, ports in module.ports.items():
            for port in ports:
                print(f"  Port ({port_direction}): {port.name}")
                for net in port.net:
                    net_type = net.net_type
                    net_name = net.name
                    print(f"    Connected Net ({net_type}): {net_name}")

def retrieve_instances_and_their_connected_nets(modules):
    for module in modules:
        print(f"\nModule: {module.name}")
        for instance in module.instances:
            print(f"  Instance: {instance.name}")
            for pin in instance.pins:
                print(f"    Pin: {pin.name}")
                if pin.net:
                    net_type = pin.net.net_type
                    net_name = pin.net.name
                    print(f"      Connected Net ({net_type}): {net_name}")

# def retrieve_modules_and_their_ports_and_nets(modules):
#     for module in modules:
#         print(f"\nModule: {module.name}")
#         print("  Ports:")
#         for direction, ports in module.ports.items():
#             for port in ports:
#                 print(f"    {direction} {port.name}")
#         print("  Nets:")
#         for net in module.nets:
#             print(f"    {net.name}")

def retrieve_modules_with_specific_net(modules):
    net_name = input("Enter the name of the net to retrieve modules: ").strip()

    found_modules = [module.name for module in modules if any(net.name == net_name for net in module.nets)]
    
    if found_modules:
        print(f"Modules with net '{net_name}':")
        for module_name in found_modules:
            print(f"  {module_name}")
    else:
        print(f"No modules found with net '{net_name}'.")

def retrieve_modules_with_specific_port(modules):
    print("Retrieve Modules with a Specific Port:")

    # Ask the user to enter the port name
    port_name = input("Enter the name of the port to search for: ")

    # List to store module names with the specified port
    modules_with_port = []

    for module in modules:
        # Check if the port exists in the module
        if any(port.name == port_name for port_list in module.ports.values() for port in port_list):
            modules_with_port.append(module.name)

    if modules_with_port:
        print(f"Modules with port '{port_name}':")
        for module_name in modules_with_port:
            print(f"  {module_name}")
    else:
        print(f"No modules found with port '{port_name}'.")
    
# Update the retrieve_nets_connected_to_specific_pin function
def retrieve_nets_connected_to_specific_pin(modules):
    print("Retrieve Nets Connected to a Specific Pin:")

    # Ask the user to choose a module
    module_name = input("Enter the name of the module to retrieve instances: ")

    # Find the module in the list of modules
    module = next((mod for mod in modules if mod.name == module_name), None)

    if module:
        # Ask the user to choose an instance
        instance_name = input(f"Enter the name of the instance in module '{module_name}': ")
        instance = next((inst for inst in module.instances if inst.name == instance_name), None)

        if instance:
            # Ask the user to choose a pin
            pin_name = input(f"Enter the name of the pin in instance '{instance_name}': ")
            pin = next((p for p in instance.pins if p.name == pin_name), None)

            if pin:
                print(f"Nets connected to pin '{pin_name}' in instance '{instance_name}' of module '{module_name}':")
                # Check if pin.net is a single VerilogNet object
                if isinstance(pin.net, VerilogNet):
                    print(f"  {pin.net.name}")
                elif isinstance(pin.net, list):
                    # Iterate over the list of VerilogNet objects
                    for net in pin.net:
                        print(f"  {net.name}")
                else:
                    print("Error: Unexpected format for pin.net.")
            else:
                print(f"Error: Pin '{pin_name}' not found in instance '{instance_name}' of module '{module_name}'.")
        else:
            print(f"Error: Instance '{instance_name}' not found in module '{module_name}'.")
    else:
        print(f"Error: Module '{module_name}' not found.")

def retrieve_instances_and_connected_nets_in_module(modules):
    print("Instances and Connected Nets in Modules:")
    for module in modules:
        print(f"Module: {module.name}")
        for instance in module.instances:
            print(f"  Instance: {instance.name}")
            for pin in instance.pins:
                print(f"    Pin: {pin.name} - Connected Net: {pin.net.name}")

def retrieve_all_nets_in_module(modules):
    print("All Nets in Modules:")
    for module in modules:
        print(f"Module: {module.name}")
        for net in module.nets:
            print(f"  Net: {net.name}")
   
def retrieve_all_pins_in_module(modules):
    print("All Pins in Modules:")
    for module in modules:
        print(f"Module: {module.name}")
        for instance in module.instances:
            print(f"  Instance: {instance.name}")
            for pin in instance.pins:
                print(f"    Pin: {pin.name}")

def retrieve_port_derived_nets_connected_to_port(modules):
    print("Port-Derived Nets Connected to Ports:")
    for module in modules:
        for direction, ports in module.ports.items():
            for port in ports:
                if port.net and port.net[0].net_type == 'port-derived':
                    print(f"  Module: {module.name}, Port: {port.name}, Port-Derived Net: {port.net[0].name}")

def retrieve_ports_in_module(modules):
    print("Ports in all modules:")
    for module in modules:
        print(f"\nModule '{module.name}':")
        for direction, ports in module.ports.items():
            for port in ports:
                print(f"  {direction} {port.name}")

def retrieve_all_nets_connected_to_instance(modules):
    print("All Nets Connected to Instances:")
    
    for module in modules:
        for instance in module.instances:
            print(f"Nets connected to instance '{instance.name}' in module '{module.name}':")
            for pin in instance.pins:
                if pin.net:
                    print(f"  Connected Net: {pin.net.name}")
                else:
                    print("  Not Connected to a Net")
            print()  # Add a newline for better readability between instances

def retrieve_all_instances_in_module(modules):
    for module in modules:
        print(f"Instance names for module '{module.name}':")
        if module.instances:
            for instance in module.instances:
                print(f"  {instance.name}")
        else:
            print("  No instances found.")
        print()  # Add a newline for better readability between modules

def add_new_query(queries_list):
    file_name = input("Enter the file name: ")
    
    if os.path.isfile(file_name):
        with open(file_name, 'r') as file:
            query_content = file.read()
            queries_list.append((file_name, query_content.splitlines()))
            print(f"Query added successfully from file '{file_name}'!")
    else:
        print(f"File '{file_name}' does not exist.")

def view_query(queries_list):
    for i, (file_name, query_content) in enumerate(queries_list, 1):
        print(f"{i}. {file_name}:")
        for j, line in enumerate(query_content, 1):
            print(f"   {j}. {line}")

# Update the execute_query function
def execute_query(queries_list, modules):
    view_query(queries_list)
    choice_file = int(input("Enter the number to choose a file: "))

    if 1 <= choice_file <= len(queries_list):
        _, query_content = queries_list[choice_file - 1]

        print("Options:")
        for i, line in enumerate(query_content, 1):
            print(f"   {i}. {line}")

        choice_line = int(input("Enter the line number to execute query: "))

        if 1 <= choice_line <= len(query_content):
            selected_option = query_content[choice_line - 1]

            if selected_option == "Retrieve All Modules:":
                retrieve_all_modules(modules)
            elif selected_option == "Retrieve All Instances in a Module:":
                retrieve_all_instances_in_module(modules)
            elif selected_option == "Retrieve All Nets Connected to an Instance:":
                retrieve_all_nets_connected_to_instance(modules)
            elif selected_option == "Retrieve Ports in a Module:":
                retrieve_ports_in_module(modules)
            elif selected_option == "Retrieve Port-Derived Nets Connected to a Port:":
                retrieve_port_derived_nets_connected_to_port(modules)
            elif selected_option == "Retrieve All Pins in a Module:":
                retrieve_all_pins_in_module(modules)
            elif selected_option == "Retrieve All Nets in a Module:":
                retrieve_all_nets_in_module(modules)
            elif selected_option == "Retrieve Instances and Their Connected Nets in a Module:":
                retrieve_instances_and_connected_nets_in_module(modules)
            elif selected_option == "Retrieve Nets Connected to a Specific Pin:":
                retrieve_nets_connected_to_specific_pin(modules)
            elif selected_option == "Retrieve Modules with a Specific Port:":
                retrieve_modules_with_specific_port(modules)
            elif selected_option == "Retrieve Modules with a Specific Net:":
                retrieve_modules_with_specific_net(modules)
            elif selected_option == "Retrieve Modules and Their Ports and Nets:":
                retrieve_modules_and_their_ports_and_nets(modules)
            elif selected_option == "Retrieve Instances and Their Connected Nets in a Module":
                retrieve_instances_and_their_connected_nets(modules)
            elif selected_option == "Retrieve Ports and Their Connected Nets in a Module:":
                retrieve_ports_and_their_connected_nets(modules)
            elif selected_option == "Retrieve Modules and Their Nets with Relationships:":
                print('retrieve_modules_and_their_nets_with_relationships(modules) is in-progress. Please wait for further developments')
            elif selected_option == "Retrieve Modules and Their Ports, Nets:":
                print('retrieve_modules_and_their_ports_nets(modules) in progress')
            elif selected_option == "Retrieve Modules and Their Instances with Pins:":
                retrieve_modules_and_their_instances_with_pins(modules)
            elif selected_option == "Retrieve Modules and Their Ports:":
                retrieve_modules_and_their_ports(modules)
            elif selected_option == "Retrieve Ports and Their Connected Nets in a Module with Port-Derived Nets:":
                retrieve_ports_and_their_nets_with_relationships_and_port_derived_nets(modules)
            else:
                print(f"Executing query: {selected_option}")
                # Add your code to execute the selected query here
        else:
            print("Invalid line number!")
    else:
        print("Invalid choice!")

