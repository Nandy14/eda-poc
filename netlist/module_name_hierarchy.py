## Read all files from I2C_new folder and generate array of all modules
## Right now it is assumed that module name immediately follows the keyword "module" and is on the same line 

def find_module_name(filename):
    # Read file
    with open(filename, 'r') as file:
        data = file.read().replace('\n', ' ')

    # Regular expression pattern
    pattern = r'module\s+(#\(.*?\))?\s*([a-zA-Z_][a-zA-Z0-9_]*)'
    modules = re.findall(pattern, data)

    # Extract module names
    module_name = [m[1] for m in modules]

    return module_name


### Function to identify module hierarchy from a bunch of verilog files
### Inputs -  verilog files, module name array

import os
import re

def find_module_hierarchy(directory, module_names):
    # Create a dictionary where key=parent module and value=list of child modules
    hierarchy = {name: [] for name in module_names}

    # Regex pattern to find module instantiations, adjusted to also handle parameters
    pattern = r'(' + '|'.join(module_names) + r')\s*(#\(.+\))?\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\('

    # Search each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.v'):
            with open(os.path.join(directory, filename), 'r') as file:
                data = file.read().replace('\n', ' ')

            for match in re.finditer(pattern, data):
                module = match.group(1)
                parent_module = re.search(r'module\s+([a-zA-Z_][a-zA-Z0-9_]*)', data[:match.start()])
                if parent_module:
                    hierarchy[parent_module.group(1)].append(module)

    return hierarchy


###############################
###  Main code
###############################


### First generate an array of module names

import os
files = os.listdir ("/content/drive/MyDrive/RTL_Sizer/I2C_new")
module_name_array = []
root_modules = dict ()
hier_modules = dict ()
for file in files:
   print ("file is", file)
   root_modules[file] = []
   module_name = find_module_name ("/content/drive/MyDrive/RTL_Sizer/I2C_new/"+file)
   if module_name:
      for index in range (0, len(module_name)):
         module_name_array.append (module_name[index])

for index in range (0, len(module_name_array)):
     print ("module name is", module_name_array[index])

### Now generate module hierarchy
directory ='/content/drive/MyDrive/RTL_Sizer/I2C_new'
hierarchy = find_module_hierarchy(directory, module_name_array)

for parent, children in hierarchy.items():
    print(f'Module {parent} has child modules: {children}')
