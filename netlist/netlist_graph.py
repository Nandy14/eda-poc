# import networkx as nx
# import matplotlib.pyplot as plt
# from netlist_utils import get_file_path
# from netlist_parser import parse_netlist, parse_netlist_hierarchy_module_template

# def build_graph(verilog_module):
#     G = nx.DiGraph()

    
#     # Add nodes for ports
#     for direction, ports in verilog_module.ports.items():
#         for port in ports:
#             G.add_node(port.name, node_type='port', direction=direction)

#     # Add nodes for instances
#     for instance in verilog_module.instances:
#         G.add_node(instance.name, node_type='instance', cell_type=instance.cell_type)

    # # Add nodes for pins
    # for instance in verilog_module.instances:
    #     for pin in instance.pins:
    #         G.add_node(pin.name, node_type='pin')

#     # # Add edges for connections
#     # for instance in verilog_module.instances:
#     #     for pin in instance.pins:
#     #         if pin.net:
#     #             G.add_edge(pin.name, pin.net.name)

#     return G

# # Example usage:
# # Assuming you have already parsed your netlist into a VerilogModule instance
# netlist_content = get_file_path()
# module_templates = parse_netlist_hierarchy_module_template(netlist_content)
# verilog_modules = parse_netlist(netlist_content, module_templates)  # Replace with your actual parsing logic

# # Build the graph
# # graph = build_graph(verilog_module)

# # Build the graph
# for module in verilog_modules:
#     graph = build_graph(module)
#     pos = nx.spring_layout(graph)

#     # Draw the graph with nodes and labels
#     nx.draw(graph, pos, with_labels=True, font_weight='bold', node_color='skyblue', node_size=3000, font_size=12, arrowsize=10)

#     # Add external labels outside the nodes
#     external_labels = {}
#     for node in graph.nodes:
#         node_type = graph.nodes[node]['node_type']
#         if node_type == 'port':
#             direction = graph.nodes[node]['direction']
#             external_labels[node] = f"{node_type}-{direction}"
#         else:
#             external_labels[node] = f"{node_type}"

#     pos_labels = {k: (v[0], v[1] - 0.10) for k, v in pos.items()}  # Adjust the label positions
#     nx.draw_networkx_labels(graph, pos_labels, labels=external_labels, font_size=5, font_color='black')

#     # Add title with module name
#     plt.title(module.name)

#     plt.show()

import networkx as nx
import matplotlib.pyplot as plt
from netlist_utils import get_file_path
from netlist_parser import parse_netlist, parse_netlist_hierarchy_module_template

def build_graph(verilog_module):
    G = nx.DiGraph()

    # Add nodes for ports
    for direction, ports in verilog_module.ports.items():
        for port in ports:
            G.add_node(port.name, node_type='port', direction=direction)

    # Add nodes for instances
    for instance in verilog_module.instances:
        G.add_node(instance.name, node_type='instance', cell_type=instance.cell_type)

    # Add nodes for pins
    for instance in verilog_module.instances:
        for pin in instance.pins:
            G.add_node(pin.name, node_type='pin')
            G.add_edge(pin.name, instance.name)

    # Add nodes for nets
    for net in verilog_module.nets:
        if net.net_type == 'wire':
            G.add_node(net.name,node_type='net - '+net.net_type,width = net.width, net_type = net.net_type)

    return G

netlist_content = get_file_path()
module_templates = parse_netlist_hierarchy_module_template(netlist_content)
verilog_modules = parse_netlist(netlist_content, module_templates)  # Replace with your actual parsing logic

# Build the graph
for module in verilog_modules:
    graph = build_graph(module)
    pos = nx.kamada_kawai_layout(graph)

    # Draw the graph with nodes and labels
    nx.draw(graph, pos, with_labels=True, font_weight='bold', node_color='skyblue', node_size=2000, font_size=10, arrowsize=10)

    # Add external labels outside the nodes
    external_labels = {}
    for node in graph.nodes:
        node_type = graph.nodes[node]['node_type']
        if node_type == 'port':
            direction = graph.nodes[node]['direction']
            external_labels[node] = f"{node_type}-{direction}"
        else:
            external_labels[node] = f"{node_type}"

    # Add title with module name
    plt.title(module.name)

    pos_labels = {k: (v[0], v[1] - 0.089) for k, v in pos.items()}  # Adjust the label positions
    nx.draw_networkx_labels(graph, pos_labels, labels=external_labels, font_size=8, font_color='black')


    plt.show()
