import re

class VerilogModule:
    """
    Verilog Module class to represent a module in the design.
    """
    def __init__(self, name):
        self.name = name
        self.ports = {"input": [], "output": []}
        self.instances = []
        self.nets = []        

    def __str__(self):
        return f"Module: {self.name}"
    
    def print_net_fanout(self):
        for net in self.nets:
            print(f"Net: {net.name}, Fanout: {net.fanout}")

    def to_dict(self):
            return {
                "module_name": self.name,
                "ports": {direction: [port.to_dict() for port in ports] for direction, ports in self.ports.items()},
                "instances": [instance.to_dict() for instance in self.instances],
                "nets": [net.to_dict() for net in self.nets],             
            }

class VerilogInstance:
    '''
    Verilog Instance object that represents an instance of another verilog module or a Library cell such as
    BUFF, XOR etc.
    '''
    def __init__(self, name, cell_type, ref_name):
        self.name = name
        self.cell_type = cell_type
        self.ref_name = ref_name
        self.pins = []

    def __str__(self):
        return f"Instance: {self.name}, Cell Type: {self.cell_type}, Reference: {self.ref_name}"

    def to_dict(self):
        return {
            "instance": self.name,
            "cell_type": self.cell_type,
            "ref_name": self.ref_name,
            "pins": [pin.to_dict() for pin in self.pins]
        }

# class VerilogNet:
#     '''
#     Verilog Net object that represents the connection between a port and an Instance pin or between two different Instances(pins) 
#     '''
#     def __init__(self, name, net_type, width):
#         self.name = name
#         self.net_type = net_type
#         self.width = self.parse_width(width)
#         self.fanout = 0

#     def increment_fanout(self):
#         self.fanout += 1

#     @staticmethod
#     def parse_width(width_str_or_tuple):
#         '''
#         Parses a width specification from a string or tuple into a tuple of integers.

#         It can accept either a string in the format '[x:y]' or a tuple.
#         If the input is a string, it strips the brackets and whitespace, then splits the string
#         at the colon to create a tuple of integers. If the input is already a tuple, it returns
#         it directly. If the input is None or an empty string, it returns None.

#         Args:
#             width_str_or_tuple (str or tuple): The width specification to be parsed. It can be
#                                                a string in the format '[x:y]' or a tuple (x, y).

#         Returns:
#             tuple or None: A tuple of two integers representing the parsed width (x, y) if the
#                            input is a valid width specification. Returns None if the input is
#                            None, an empty string, or an invalid format.

#         Example:
#             parse_width('[3:0]') returns (3, 0)
#             parse_width((5, 1)) returns (5, 1)
#             parse_width(None) returns None
#         '''
#         if isinstance(width_str_or_tuple, tuple):
#             return width_str_or_tuple
#         if width_str_or_tuple:
#             # Strip the brackets and whitespace, then split it
#             return tuple(map(int, width_str_or_tuple.strip('[] ').split(':')))
#         return None

#     def __str__(self):
#         width_str = f"[{self.width[0]}:{self.width[1]}]" if self.width else ""
#         return f"Net: {self.name}, Type: {self.net_type}, Width:{width_str}"

#     def to_dict(self):
#         return {
#             "name": self.name,
#             "net_type": self.net_type,
#             "width": self.width
#         }


class VerilogNet:
    '''
    Verilog Net object that represents the connection between a port and an Instance pin or between two different Instances(pins) 
    '''
    def __init__(self, name, net_type, width):
        self.name = name
        self.net_type = net_type
        self.width = self.parse_width(width)
        self.fanout = 0
        self.connections = {"startpoint": [], "endpoints": []}

    def increment_fanout(self):
        self.fanout += 1

    def add_connection(self, direction, connected_to):
        if direction == "startpoint":
            self.connections["startpoint"].append(connected_to)
        elif direction == "endpoint":
            self.connections["endpoints"].append(connected_to)

    @staticmethod
    def parse_width(width_str_or_tuple):
            '''
            Parses a width specification from a string or tuple into a tuple of integers.

            It can accept either a string in the format '[x:y]' or a tuple.
            If the input is a string, it strips the brackets and whitespace, then splits the string
            at the colon to create a tuple of integers. If the input is already a tuple, it returns
            it directly. If the input is None or an empty string, it returns None.

            Args:
                width_str_or_tuple (str or tuple): The width specification to be parsed. It can be
                                                a string in the format '[x:y]' or a tuple (x, y).

            Returns:
                tuple or None: A tuple of two integers representing the parsed width (x, y) if the
                            input is a valid width specification. Returns None if the input is
                            None, an empty string, or an invalid format.

            Example:
                parse_width('[3:0]') returns (3, 0)
                parse_width((5, 1)) returns (5, 1)
                parse_width(None) returns None
            '''
            if isinstance(width_str_or_tuple, tuple):
                return width_str_or_tuple
            if width_str_or_tuple:
                # Strip the brackets and whitespace, then split it
                return tuple(map(int, width_str_or_tuple.strip('[] ').split(':')))
            return None


    def __str__(self):
        width_str = f"[{self.width[0]}:{self.width[1]}]" if self.width else ""
        return f"Net: {self.name}, Type: {self.net_type}, Width:{width_str}, Connections: {self.connections}"

    def to_dict(self):
        return {
            "name": self.name,
            "net_type": self.net_type,
            "width": self.width,
            "connections": self.connections
        }

class VerilogPin:
    '''
    Verilog Pin objects that represents the pins of a VerilogInstance object,
    which connects the instance to other instances or ports through VerilogNet objects
    '''
    def __init__(self, name, instance, net, direction=None):
        self.name = name
        self.direction = direction
        self.instance = instance
        self.net = net

    def __str__(self):
        net_str = self.net.name if self.net else "None"
        return f"Pin: {self.name}, Connected to: {net_str}"

    def to_dict(self):
        return {
            "name": self.name,
            "direction": self.direction,
            "instance": self.instance.name if self.instance else None,
            "net": self.net.name if self.net else None
        }

class VerilogPort:
    '''
    Verilog Port Objects that represent the ports in a Module, such as input/output.
    '''
    def __init__(self, name, direction, width=None):
        self.name = name
        self.direction = direction
        self.width = VerilogNet.parse_width(width)
        self.net = []

    def __str__(self):
        width_str = f"[{self.width[0]}:{self.width[1]}]" if self.width else ""
        return f"Port: {self.name}, Direction: {self.direction}, Width: {width_str}"

    def to_dict(self):
        return {
            "name": self.name,
            "direction": self.direction,
            "width": self.width
        }

class GraphNode:
    def __init__(self, name, node_type):
        self.name = name
        self.node_type = node_type
        self.edges = set()

# Precompiled regex patterns
MODULE_PATTERN = re.compile(r'module (\w+)\s*\(')
PORT_PATTERN = re.compile(r'(input|output)\s*(?:\[(\d+:\d+)\])?\s*([^;]+);', re.DOTALL)
NET_PATTERN = re.compile(r'wire\s+((?:\[\d+:\d+\])?\s*\w+\s*(?:,\s*\w+\s*)*);', re.DOTALL)
INSTANCE_PATTERN = re.compile(r'^\s*(\w+)\s+(\w+)\s*\((?!\s*input\s|\s*output\s|\s*inout\s)')
PIN_PATTERN = re.compile(r'\.(\w+)\s*\(\s*([^)]+)\s*\)')
