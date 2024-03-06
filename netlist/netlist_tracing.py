# Constructing a netlist tracer

# take input = dataframe.xlsx

# pass input = startpoint 
#  
# Begin the tracing.
# 
# For a given startpoint, stack all the endpoints related and add them to a stack

# Pop each endpoint one after another. 

# For each endpoint, find the corresponding row which has the Z pin for it.

# Once the row is found, add the endpoints belonging to it.

# Pop each endpoint one after the other.

# Find corresponding startpoint for each endpoint encountered.

# Repeat process until reached a primary output

# Save the path as a list/graph.

import pandas as pd
import ast  # Import the ast module for literal_eval

df = pd.read_excel('output/connectivity_agg_filtered.xlsx')

# Take input for the net from which you want to trace forward
net = input('Enter the net from which you want to trace forward: ')

# Find the row corresponding to the net in the dataframe
row = df.loc[df['Net'] == net]

# Extract the endpoint_list as a string from the DataFrame
endpoint_list_str = row['Endpoint'].values[0]

# Use ast.literal_eval to safely convert the string representation to a list
endpoint_list = ast.literal_eval(endpoint_list_str)
print(f'\nselected Net {net} has endpoints : {endpoint_list}')

endpoint1 = endpoint_list[0]

print(f'\nLet\'s consider the first endpoint {endpoint1}, and let\'s find the cell\'s Startpoint row')

cell_info = endpoint1.split('.')

print(f'The cell is {cell_info[0]}')
print()
print(f'We need to find the startpoint row for this cell')
print()

# Apply the function to filter rows using a lambda function
startpoint_row = df[df['Startpoint'].apply(lambda x: any(startpoint.startswith(cell_info[0]) for startpoint in ast.literal_eval(x)))]

print(f'We found the startpoint row for the cell {cell_info} :\n\n{startpoint_row}')

print('\nWe need to grab the endpoints for this\n')








# matching_rows_z = df[df['Startpoint'].apply(lambda x: startpoint_z_match in ast.literal_eval(x))]['Endpoint'].values[0]
# endp = df[df['Startpoint'].apply(lambda x: str(x).startswith(cell_info))]['Endpoint'].values[0]

# print(endp)


# # Iterate through each endpoint in the endpoint_list
# for endpoint in endpoint_list:
#     # Extract the pin type (e.g., 'A', 'B', 'Z') from the endpoint
#     pin_type = endpoint.split('.')[-1]

#     # Construct the corresponding startpoint name by replacing the pin type
#     startpoint_z_match = endpoint.replace(f'.{pin_type}', '.Z')
#     # startpoint_q_match = endpoint.replace(f'.{pin_type}', '.Q')


#     # Find the row corresponding to the startpoint in the dataframe
#     # Check if the startpoint exists in the 'Startpoint' column (assuming it's a list)
#     matching_rows_z = df[df['Startpoint'].apply(lambda x: startpoint_z_match in ast.literal_eval(x))]['Endpoint'].values[0]
#     # matching_rows_q = df[df['Startpoint'].apply(lambda x: startpoint_q_match in ast.literal_eval(x))]['Endpoint'].values
    
#     print(f'The endpoint {endpoint} for the net {net} has endpoints {matching_rows_z}')
        
#     # print()
#     # print(matching_rows_q)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # # Check if the startpoint exists in the dataframe
    # if matching_rows:
    #     # Extract the startpoint's endpoint_list as a string from the DataFrame
    #     startpoint_endpoint_list_str = matching_rows['Endpoint'].values[0]

    #     # Use ast.literal_eval to safely convert the string representation to a list
    #     startpoint_endpoint_list = ast.literal_eval(startpoint_endpoint_list_str)

    #     # Now you have the endpoint_list for the startpoint
    #     print(f"Startpoint: {startpoint}, Endpoints: {startpoint_endpoint_list}")
    # else:
    #     print(f"Startpoint {startpoint} not found in the dataframe.")





# point1 = endpoint_list[0]

# pin = point1.split(".")[-1]

# startpoint = point1.replace(f'.{pin}','.Z')

# # Check if the startpoint exists in the 'Startpoint' column (assuming it's a list)
# matching_rows = df[df['Startpoint'].apply(lambda x: startpoint in ast.literal_eval(x))]['Endpoint'].values[0]

# print(matching_rows)
