import datetime
import re

import logging

class Report:
    def __init__(self) -> None:
        self.report_type = ''
        self.path_type = ''
        self.delay_type = ''
        self.nworst = ''
        self.max_paths = ''
        self.slacks_lesser_than = ''
        self.report_by = ''
        self.nosplits = ''
        self.input_pins = ''
        self.nets = ''
        self.transition_time = ''
        self.capacitance = ''
        self.design = ''
        self.version = ''
        self.date = ''
        self.paths = []  # List of Path objects

class Path:
    def __init__(self):
        self.startpoint = ''
        self.endpoint = ''
        self.mode = ''
        self.corner = ''
        self.scenario = ''
        self.path_group = ''
        self.path_type = ''
        self.points = []  # List of Point objects

class Point:
    def __init__(self):
        self.point = ''
        self.fanout = ''
        self.cap = ''
        self.trans = ''
        self.incr = ''
        self.path = ''

# Define regex patterns
report_type_pattern = re.compile(r'Report\s*:\s*(\w+)')
path_type_pattern = re.compile(r'-path_type\s*([^\s]+)')
delay_type_pattern = re.compile(r'-delay_type\s*([^\s]+)')
nworst_pattern = re.compile(r'-nworst\s*(\d+)')
max_paths_pattern = re.compile(r'-max_paths\s*(\d+)')
slack_lesser_than_pattern = re.compile(r'-slack_lesser_than\s*([\d.]+)')
report_by_pattern = re.compile(r'-report_by\s*([^\s]+)')
nosplits_pattern = re.compile(r'-nosplit')
input_pins_pattern = re.compile(r'-input_pins')
nets_pattern = re.compile(r'-nets')
transition_time_pattern = re.compile(r'-transition_time')
capacitance_pattern = re.compile(r'-capacitance')
design_pattern = re.compile(r'Design\s*:\s*([^\s]+)')
version_pattern = re.compile(r'Version:\s*([^\s]+)')
date_pattern = re.compile(r'Date\s*:\s*(.+)')

# Point patterns
point_pattern = re.compile(r'\s*([\w\d_/]+(?:\s*\(.*\))?)(?:\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*([rf])?\s*(\S*))?')

def parse_timing_report(file_path):
    try:
        report = Report()
        current_path = None
        current_point = None        

        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if line.strip().startswith('//') or line.strip().startswith('*') or not line:
                continue

            # Report type match
            report_type_match = report_type_pattern.search(line)
            if report_type_match:
                report.report_type = report_type_match.group(1)

            # Path type match
            path_type_match = path_type_pattern.search(line)
            if path_type_match:
                report.path_type = path_type_match.group(1)

            # Delay type match
            delay_type_match = delay_type_pattern.search(line)
            if delay_type_match:
                report.delay_type = delay_type_match.group(1)

            # nworst match
            nworst_match = nworst_pattern.search(line)
            if nworst_match:
                report.nworst = nworst_match.group(1)

            # max_paths match
            max_paths_match = max_paths_pattern.search(line)
            if max_paths_match:
                report.max_paths = max_paths_match.group(1)

            # slack_lesser_than match
            slack_lesser_than_match = slack_lesser_than_pattern.search(line)
            if slack_lesser_than_match:
                report.slacks_lesser_than = slack_lesser_than_match.group(1)

            # report_by match
            report_by_match = report_by_pattern.search(line)
            if report_by_match:
                report.report_by = report_by_match.group(1)

            # nosplits match
            if nosplits_pattern.search(line):
                report.nosplits = True

            # input_pins match
            if input_pins_pattern.search(line):
                report.input_pins = True

            # nets match
            if nets_pattern.search(line):
                report.nets = True

            # transition_time match
            if transition_time_pattern.search(line):
                report.transition_time = True

            # capacitance match
            if capacitance_pattern.search(line):
                report.capacitance = True

            # Design match
            design_match = design_pattern.search(line)
            if design_match:
                report.design = design_match.group(1)

            # Version match
            version_match = version_pattern.search(line)
            if version_match:
                report.version = version_match.group(1)

            # Date match and conversion
            date_match = date_pattern.search(line)
            if date_match:
                date_str = date_match.group(1)
                try:
                    report.date = datetime.datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y')
                except ValueError:
                    # Handle the case where the date string format is incorrect
                    print(f"Error parsing date: {date_str}")

            # Parse the paths in the report and add it to the report object
                    
            # Startpoint match
            startpoint_match = re.search(r'Startpoint:\s*([\w\d_]+)', line)
            if startpoint_match:
                current_path = Path()
                current_path.startpoint = startpoint_match.group(1)

            # Endpoint match
            endpoint_match = re.search(r'Endpoint:\s*([\w\d_]+)', line)
            if endpoint_match and current_path:
                current_path.endpoint = endpoint_match.group(1)

            # Mode match
            mode_match = re.search(r'Mode:\s*([\w\d_]+)', line)
            if mode_match and current_path:
                current_path.mode = mode_match.group(1)

            # Corner match
            corner_match = re.search(r'Corner:\s*([\w\d_]+)', line)
            if corner_match and current_path:
                current_path.corner = corner_match.group(1)

            # Scenario match
            scenario_match = re.search(r'Scenario:\s*([\w\d_]+)', line)
            if scenario_match and current_path:
                current_path.scenario = scenario_match.group(1)

            # Path Group match
            path_group_match = re.search(r'Path Group:\s*([\w\d_]+)', line)
            if path_group_match and current_path:
                current_path.path_group = path_group_match.group(1)

            # Path Type match
            path_type_match = re.search(r'Path Type:\s*([\w\d_]+)', line)
            if path_type_match and current_path:
                current_path.path_type = path_type_match.group(1)
                report.paths.append(current_path)

            # Point match
            point_match = point_pattern.match(line)
            if point_match and current_path:
                current_point = Point()
                current_point.point = point_match.group(1)
                current_point.fanout = point_match.group(2)
                current_point.cap = point_match.group(3)
                current_point.trans = point_match.group(4)
                current_point.incr = point_match.group(5)
                current_point.path = point_match.group(6)
                current_path.points.append(current_point)

            # Handling multiline points
            elif current_point and line.strip() and not line.strip().startswith(('Startpoint:', 'Endpoint:')):
                # Assuming a continuation of the current point data
                line_parts = line.strip().split()
                if len(line_parts) == 6:
                    current_point.path += line_parts[5]

        return report

    except Exception as e:
        error_message = f"Error parsing timing report file: {e}"
        logging.error(error_message)
        print(error_message)
        raise ValueError(error_message)

# Example usage:
file_path = 'timing_report_2.txt'
parsed_report = parse_timing_report(file_path)

# Verification
print(f"Design: {parsed_report.design}")
print(f"Version: {parsed_report.version}")
print(f"Date: {parsed_report.date}")
# Add more print statements for other fields in the Report class