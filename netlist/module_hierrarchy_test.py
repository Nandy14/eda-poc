from netlist_parser import parse_netlist_hierarchy_module_template, parse_netlist
from netlist_models import VerilogInstance, VerilogModule, VerilogNet, VerilogPin, VerilogPort
from netlist_utils import get_file_path


input_file = get_file_path()

module_templates = parse_netlist_hierarchy_module_template(input_file)

modules = parse_netlist(input_file, module_templates)


def update_hierarchical_names(module_obj, parent_instance_name=""):
    
    # Set hierarchical names for ports, nets, instances, and pins
    for port_type, port_list in module_obj.ports.items():
        for port in port_list:
            port.hierarchical_name = f"{module_obj.name}.{port.name}"

    for net in module_obj.nets:
        net.hierarchical_name = f"{module_obj.name}.{net.name}"

    for instance in module_obj.instances:
        instance.hierarchical_name = f"{module_obj.name}.{instance.name}"

        for pin in instance.pins:
            pin.hierarchical_name = f"{module_obj.name}.{instance.name}.{pin.name}"

for module in modules:
    update_hierarchical_names(module)


def display_hierarchical_names(module_obj):
    print()
    print()
    print()
    print()
    print('#################################################')    
    print('#################################################')    
    print('#################################################')    
    print('#################################################')    
    print('#################################################')    
    print('#################################################')    
    print('#################################################')    
    print()
    print()
    print()
    print(f"Hierarchical names for module {module_obj.name}:")

    # Display hierarchical names for ports
    print()
    print(f"Hierarchical names for ports")
    for port_type, port_list in module_obj.ports.items():
        for port in port_list:
            print(f"{port.name}: {port.hierarchical_name}")

    print()
    print(f"Hierarchical names for nets")
    # Display hierarchical names for nets
    for net in module_obj.nets:
        print(f"{net.name}: {net.hierarchical_name}")

    print()
    print(f"Hierarchical names for instances")
    # Display hierarchical names for instances and their pins
    for instance in module_obj.instances:
        print(f"{instance.name}: {instance.hierarchical_name}")

        print()
        print(f"Hierarchical names for pins")
        for pin in instance.pins:
            print(f"  {pin.name}: {pin.hierarchical_name}")

for module in modules:
    display_hierarchical_names(module)