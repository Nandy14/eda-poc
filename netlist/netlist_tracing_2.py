import pandas as pd


# Assuming df is your DataFrame
df = pd.read_excel('output/connectivity_agg_filtered.xlsx')

# Convert the fanout column to a dictionary for faster lookups
fanout_dict = df.set_index('Startpoint')['Endpoint'].to_dict()

def trace_path(node, path=[]):
    """
    Recursive function to trace paths in the dataframe
    """
    # Append the current node to the path
    path.append(node)
    
    # Get the endpoints for the current node
    endpoints = fanout_dict.get(node, [])
    
    # Check if endpoints start with the module name (e.g., 'fulladdder')
    if any(endpoint.startswith('fulladdder') for endpoint in endpoints):
        print(" -> ".join(path))
        return
    
    # Continue tracing paths for each endpoint
    for endpoint in endpoints:
        trace_path(endpoint, path.copy())

# Starting node
start_node = 'n4'

# Call the trace_path function for the given start_node
print(f"Paths for {start_node}:")
trace_path(start_node)
