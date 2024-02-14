import json
import pandas as pd

def net_connectivity():
    
    # Read data from the JSON file
    with open('json/parsed_objects.json', 'r') as file:
        parsed_objects = json.load(file)
    
    # Initialize lists to store data
    rows = []

    # Iterate through each module's instances
    for module_data in parsed_objects:
        module_name = module_data.get("module_name", "")

        # Iterate through instances
        for instance_data in module_data.get("instances", []):
            instance_name = instance_data.get("instance", "")
            ref_name = instance_data.get("ref_name", "")
            instance_name_with_ref = f"{ref_name} {instance_name}"

            # Iterate through pins
            for pin_data in instance_data.get("pins", []):
                pin_name = pin_data.get("name", "")
                pin_net = pin_data.get("net", "")
                pin_identifier = f"{instance_name_with_ref}.{pin_name}"

                # Check if the pin is a startpoint or endpoint
                is_startpoint = pin_name.upper() in ["Z", "Q"]
                is_endpoint = not is_startpoint

                # Append data to the list
                if is_startpoint:
                    rows.append({"Net": pin_net, "Startpoint": pin_identifier, "Endpoint": ""})
                elif is_endpoint:
                    rows.append({"Net": pin_net, "Startpoint": "", "Endpoint": pin_identifier})

        # Iterate through the ports
        for port_type, port_list in module_data.get("ports", {}).items():
            for port_data in port_list:
                port_name = port_data.get("name", "")
                port_direction = port_type

                # Create rows based on port type
                if port_direction == "input":
                    startpoint_identifier = f"{module_name}.{port_name}"
                    rows.append({"Net": port_name, "Startpoint": startpoint_identifier, "Endpoint": ""})
                elif port_direction == "output":
                    endpoint_identifier = f"{module_name}.{port_name}"
                    rows.append({"Net": port_name, "Startpoint": "", "Endpoint": endpoint_identifier})

    # Create a DataFrame from the list of rows
    df_result = pd.DataFrame(rows)

    # Filter out rows with empty values in 'Startpoint' or 'Endpoint'
    df_result_filtered = df_result[(df_result['Startpoint'] != "") | (df_result['Endpoint'] != "")]

    # Group by 'Net' and aggregate non-empty values in 'Startpoint' and 'Endpoint' into lists
    grouped_df = df_result_filtered.groupby('Net')
    aggregated_df = grouped_df.agg(lambda x: list(filter(None, x))).reset_index()

    # Calculate the count of the endpoint list for each net and add the value to the 'Fanout' column for each row
    aggregated_df['Fanout'] = aggregated_df.apply(lambda row: len(row['Endpoint']), axis=1)

    return aggregated_df

def save_to_excel(dataframe):
    
    # Save the DataFrame to Excel files
    # df_result_filtered.to_excel('output/connectivity_df_result_filtered.xlsx', index=False)
    # aggregated_df.to_excel('output_2/connectivity_agg_filtered.xlsx', index=False)
    # aggregated_df.to_json('output_2/connectivity_agg_json.json')

    dataframe.to_excel('output/dataframe.xlsx', index = False)        

def main():

    # Process parsed_objects using the function
    connectivity_table = net_connectivity()

    # Save to excel
    save_to_excel(connectivity_table)      
    
if __name__ == "__main__":
    main()
