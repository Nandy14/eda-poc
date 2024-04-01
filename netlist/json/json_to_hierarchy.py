import json
import tkinter
from tkinter import filedialog, messagebox
from collections import defaultdict
import uuid

class VerilogModule:
    """
    Verilog Module class to represent a module in the design.
    """

    def __init__(self, name, hierarchical_name="", unique_id=None):
        """
        Initialize a VerilogModule object.

        Parameters:
        - name (str): The name of the module.
        - hierarchical_name (str): The hierarchical name of the module.
        - unique_id (str): The unique identifier of the module.
        """
        self.name = name
        self.ports = {"input": [], "output": []}  # each list has objects of type VerilogPort
        self.instances = []  # has objects of type VerilogInstance
        self.nets = []  # has objects of type VerilogNet
        self.hierarchical_name = hierarchical_name
        self.unique_id = unique_id

    def __str__(self, indent=0):
        result = f"{' ' * indent}Module: {self.name}, Unique ID: {self.unique_id}\n"
        result += ''.join(instance.__str__(indent + 2) for instance in self.instances)
        result += ''.join(net.__str__(indent + 2) for net in self.nets)
        return result

    def print_net_fanout(self):
        for net in self.nets:
            print(f"Net: {net.name}, Fanout: {net.fanout}")

    def to_dict(self):
        """
        Convert the VerilogModule object to a dictionary.

        Returns:
        dict: A dictionary representation of the VerilogModule object.
        """
        return {
            "module_name": self.name,
            "hierarchical_name": self.hierarchical_name,
            "unique_id": self.unique_id,
            "ports": {direction: [port.to_dict() for port in ports] for direction, ports in self.ports.items()},
            "instances": [instance.to_dict() for instance in self.instances],
            "nets": [net.to_dict() for net in self.nets],
        }

class VerilogInstance:
    """
    Verilog Instance object that represents an instance of another Verilog module or a Library cell.
    """

    def __init__(self, name, cell_type, ref_name, hierarchical_name="", unique_id=None):
        """
        Initialize a VerilogInstance object.

        Parameters:
        - name (str): The name of the instance.
        - cell_type (str): The type of cell (e.g., 'hierarchical' or 'leaf-level').
        - ref_name (str): The reference name of the instance.
        - hierarchical_name (str): The hierarchical name of the instance.
        - unique_id (str): The unique identifier of the instance.
        """
        self.name = name
        self.cell_type = cell_type
        self.ref_name = ref_name
        self.pins = []  # has objects of type VerilogPin
        self.hierarchical_name = hierarchical_name
        self.unique_id = unique_id

    def __str__(self, indent=0):
        result = f"{' ' * indent}Instance: {self.name}, Cell Type: {self.cell_type}, Reference: {self.ref_name}, Unique ID: {self.unique_id} "
        result += f"{self.hierarchical_name}\n"
        result += ''.join(pin.__str__(indent + 2) for pin in self.pins)
        return result

    def to_dict(self):
        """
        Convert the VerilogInstance object to a dictionary.

        Returns:
        dict: A dictionary representation of the VerilogInstance object.
        """
        return {
            "instance": self.name,
            "cell_type": self.cell_type,
            "ref_name": self.ref_name,
            "hierarchical_name": self.hierarchical_name,
            "unique_id": self.unique_id,
            "pins": [pin.to_dict() for pin in self.pins]
        }

class VerilogNet:
    """
    Verilog Net object that represents the connection between a port and an Instance pin
    or between two different Instances(pins)
    """

    def __init__(self, name, net_type, width=None, hierarchical_name="", unique_id=None):
        """
        Initialize a VerilogNet object.

        Parameters:
        - name (str): The name of the net.
        - net_type (str): The type of net.
        - width (tuple): The width of the net.
        - hierarchical_name (str): The hierarchical name of the net.
        - unique_id (str): The unique identifier of the net.
        """
        self.name = name
        self.net_type = net_type
        self.width = self.parse_width(width)
        self.fanout = 0
        self.hierarchical_name = hierarchical_name
        self.unique_id = unique_id

    def increment_fanout(self):
        self.fanout += 1

    @staticmethod
    def parse_width(width_str_or_tuple):
        if isinstance(width_str_or_tuple, tuple):
            return width_str_or_tuple
        if width_str_or_tuple:
            if isinstance(width_str_or_tuple, list):
                # If width is a list, take the first element
                width_str_or_tuple = width_str_or_tuple[0]

            # Check if width is a string before processing
            if isinstance(width_str_or_tuple, str):
                # Strip the brackets and whitespace, then split it
                return tuple(map(int, width_str_or_tuple.strip('[] ').split(':')))
        return None

    def __str__(self, indent=0):
        width_str = f"[{self.width[0]}:{self.width[1]}]" if self.width else ""
        return f"{' ' * indent}Net: {self.name}, Type: {self.net_type}, Width:{width_str}\n"

    def to_dict(self):
        """
        Convert the VerilogNet object to a dictionary.

        Returns:
        dict: A dictionary representation of the VerilogNet object.
        """
        return {
            "name": self.name,
            "net_type": self.net_type,
            "width": self.width,
            "hierarchical_name": self.hierarchical_name,
            "unique_id": self.unique_id
        }

class VerilogPin:
    """
    Verilog Pin objects that represent the pins of a VerilogInstance object,
    which connects the instance to other instances or ports through VerilogNet objects
    """

    def __init__(self, name, instance, net, direction=None, hierarchical_name="", unique_id=None):
        """
        Initialize a VerilogPin object.

        Parameters:
        - name (str): The name of the pin.
        - instance (VerilogInstance): The associated VerilogInstance.
        - net (VerilogNet or str): The associated VerilogNet or its name.
        - direction (str): The direction of the pin.
        - hierarchical_name (str): The hierarchical name of the pin.
        - unique_id (str): The unique identifier of the pin.
        """
        self.name = name
        self.direction = direction
        self.instance = instance
        self.net = net
        self.hierarchical_name = hierarchical_name
        self.unique_id = unique_id

    def __str__(self, indent=0):
        net_str = self.net if isinstance(self.net, str) else (self.net.name if self.net else "None")
        return f"{' ' * indent}Pin: {self.name}, Connected to: {net_str}\n"

    def to_dict(self):
        """
        Convert the VerilogPin object to a dictionary.

        Returns:
        dict: A dictionary representation of the VerilogPin object.
        """
        return {
            "name": self.name,
            "direction": self.direction,
            "instance": self.instance.name if self.instance else None,
            "net": self.net if isinstance(self.net, str) else (self.net.name if self.net else None),
            "unique_id": self.unique_id
        }

class VerilogPort:
    """
    Verilog Port Objects that represent the ports in a Module, such as input/output.
    """

    def __init__(self, name, direction, width=None, hierarchical_name="", unique_id=None):
        """
        Initialize a VerilogPort object.

        Parameters:
        - name (str): The name of the port.
        - direction (str): The direction of the port (e.g., 'input', 'output').
        - width (tuple): The width of the port.
        - hierarchical_name (str): The hierarchical name of the port.
        - unique_id (str): The unique identifier of the port.
        """
        
        self.name = name
        self.width = VerilogNet.parse_width(width)
        self.net = []  # VerilogNet object
        self.hierarchical_name = hierarchical_name
        self.unique_id = unique_id

    def __str__(self, indent=0):
        hierarchical_info = f"{self.hierarchical_name}." if self.hierarchical_name else ""
        width_str = f"[{self.width[0]}:{self.width[1]}]" if self.width else ""
        return f"{' ' * indent}{hierarchical_info}Port: {self.name}, Width: {width_str}, Unique ID: {self.unique_id}"

    def to_dict(self):
        """
        Convert the VerilogPort object to a dictionary.

        Returns:
        dict: A dictionary representation of the VerilogPort object.
        """
        return {
            "name": self.name,
            "width": self.width,
            "hierarchical_name": self.hierarchical_name,
            "unique_id": self.unique_id
        }

class VerilogHandler:
    """
    Verilog Handler class to handle the creation and manipulation of Verilog objects.
    """

    def __init__(self):
        self.modules = []

    def generate_unique_id(self):
        """
        Generate a unique identifier.

        Returns:
        str: A unique identifier.
        """
        return str(uuid.uuid4())

    def create_verilog_objects_from_json(self, json_file):
        """
        Create VerilogModule objects from a JSON file.

        Parameters:
        - json_file (str): The path to the JSON file.
        """
        with open(json_file, 'r') as file:
            data = json.load(file)

        # Extract modules from JSON data
        module_data_list = data if isinstance(data, list) else [data]

        # Create VerilogModule objects
        for module_data in module_data_list:
            verilog_module = VerilogModule(
                name=module_data["module_name"],
                hierarchical_name="",  # Initially empty for top-level module
                unique_id=self.generate_unique_id()
            )

            # Assign hierarchical names and unique IDs to ports
            for direction, ports_data in module_data["ports"].items():
                for index, port_data in enumerate(ports_data):
                    port = VerilogPort(
                        name=port_data["name"],
                        direction=direction,
                        width=port_data.get("width"),
                        hierarchical_name=f"{verilog_module.hierarchical_name}.{verilog_module.name}.{port_data['name']}",
                        unique_id=self.generate_unique_id()
                    )
                    verilog_module.ports[direction].append(port)

            # Assign hierarchical names and unique IDs to instances
            for index, instance_data in enumerate(module_data["instances"]):
                verilog_instance = VerilogInstance(
                    name=instance_data["instance"],
                    cell_type=instance_data["cell_type"],
                    ref_name=instance_data["ref_name"],
                    hierarchical_name=f"{verilog_module.hierarchical_name}.{verilog_module.name}.{instance_data['instance']}",
                    unique_id=self.generate_unique_id()
                )

                # Assign hierarchical names and unique IDs to pins
                for pin_index, pin_data in enumerate(instance_data["pins"]):
                    pin = VerilogPin(
                        name=pin_data["name"],
                        instance=verilog_instance,
                        net=pin_data.get("net"),
                        direction=pin_data.get("direction"),
                        hierarchical_name=f"{verilog_instance.hierarchical_name}.{verilog_instance.name}.{pin_data['name']}",
                        unique_id=self.generate_unique_id()
                    )
                    verilog_instance.pins.append(pin)

                verilog_module.instances.append(verilog_instance)

            # Assign hierarchical names and unique IDs to nets
            for index, net_data in enumerate(module_data["nets"]):
                verilog_net = VerilogNet(
                    name=net_data["name"],
                    net_type=net_data["net_type"],
                    width=net_data.get("width"),
                    hierarchical_name=f"{verilog_module.hierarchical_name}.{verilog_module.name}.{net_data['name']}",
                    unique_id=self.generate_unique_id()
                )
                verilog_module.nets.append(verilog_net)

            self.modules.append(verilog_module)

    def visualize_modules(self, indent=0):
        """
        Visualize the VerilogModules.

        Parameters:
        - indent (int): The current indentation level.
        """
        for verilog_module in self.modules:
            print(verilog_module)

    def create_module_hierarchy(self):
        """
        Create a hierarchical representation of Verilog modules.

        Returns:
        dict: Hierarchical representation of Verilog modules.
        """
        hierarchy = defaultdict(dict)

        for verilog_module in self.modules:
            # Additional processing to build hierarchy based on your specific object structure
            pass

        return dict(hierarchy)

    def create_module_hierarchy_json(self, hierarchy):
        # Dump the hierarchy to a JSON file
        output_file_path = 'module_hierarchy.json'
        with open(output_file_path, 'w') as output_file:
            json.dump(hierarchy, output_file, indent=2)

        print(f"Hierarchical structure saved to {output_file_path}")

    def get_file_path_json(self):
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
                filetypes=[("All Files", "*.*")]
            )

            # Check if the selected file has a valid extension
            if file_path and not file_path.lower().endswith((".json")):
                error_message = "Invalid file format. Please select a valid JSON file with a '.json' extension."
                messagebox.showerror("Error", error_message)
            else:
                break  # Break out of the loop if a valid file is selected

        return file_path

if __name__ == "__main__":

    #  Create an instance of the class
    verilog_handler = VerilogHandler()

    # Get the path to the JSON file using a file dialog
    file_path = verilog_handler.get_file_path_json()

    # Generate VerilogModule objects from the JSON file
    verilog_handler.create_verilog_objects_from_json(file_path)

    # Visualize the VerilogModules
    verilog_handler.visualize_modules()

    # Create a hierarchical representation of Verilog modules
    module_hierarchy = verilog_handler.create_module_hierarchy()

    # Generate a json file for the module hierarchy
    verilog_handler.create_module_hierarchy_json(module_hierarchy)

