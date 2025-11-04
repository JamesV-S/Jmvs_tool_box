
import maya.cmds as cmds

dictionary = {
    "James": ['Vilela-Slater', '20', 'blond', '5ft 9inch'], 
    "Lilirose": ['Kent', '19', 'redhead', '5ft 7inch'], 
    "Thuki": ['Ragesvaran', '20', 'black', '5ft 9inch']
}

print("----------------------------------")
print(1)
# Accessing a specific value by key
print(dictionary['Lilirose']) # output: ['Kent', '19', 'redhead', '5ft 7inch'] 

print("----------------------------------")
print(2)
# Iterating over keys
for key in dictionary.keys():
    print(f"key: {key}")
    # output: key: James
            # key: Lilirose
            # key: Thuki
'''print(f"key: {dictionary[key]}") gives me the value sof the keys! '''
                         
print("----------------------------------")
print(3)
# Iterating over the values
for value in dictionary.values():
    print(f"Value: {value}") 
# Output:
    # Value: ['Vilela-Slater', '20', 'blond', '5ft 9inch']
    # Value: ['Kent', '19', 'redhead', '5ft 7inch']
    # Value: ['Ragesvaran', '20', 'black', '5ft 9inch']

print("----------------------------------")
print(4)
# Iterating over key-value pairs
for key, value in dictionary.items():
    print(f"key: {key} / Value: {value}")
# Output:    
    # key: James / Value: ['Vilela-Slater', '20', 'blond', '5ft 9inch']
    # key: Lilirose / Value: ['Kent', '19', 'redhead', '5ft 7inch']
    # key: Thuki / Value: ['Ragesvaran', '20', 'black', '5ft 9inch']

print("----------------------------------")
print(5)
# Unpacking a specific entry
name, details = 'James', dictionary['James']
print(f"{name}: {details}")
# Output: 
    # James: ['Vilela-Slater', '20', 'blond', '5ft 9inch']

print("----------------------------------")
print(6)

# Using tuple unpacking in a loop
for name, (last_name, age, hair_colour, height) in dictionary.items():
    print(f"{name} {last_name} is {age} years old, has {hair_colour} hair, and is {height} tall")
# Output:
# James Vilela-Slater is 20 years old, has blond hair, and is 5ft 9inch tall
# Lilirose Kent is 19 years old, has redhead hair, and is 5ft 7inch tall
# Thuki Ragesvaran is 20 years old, has black hair, and is 5ft 9inch tall

print("----------------------------------")
print(7)

# Accessing individual attributes
for name, details in dictionary.items():
    last_name = details[0]
    age = details[1]
    hair_colour = details[2]
    height = details[3]
    print(f"{name} {last_name}, Age: {age}, Hair: {hair_colour}, Height: {height}")
# Output:
# James Vilela-Slater, Age: 20, Hair: blond, Height: 5ft 9inch
# Lilirose Kent, Age: 19, Hair: redhead, Height: 5ft 7inch
# Thuki Ragesvaran, Age: 20, Hair: black, Height: 5ft 9inch

# Using get method to handle missing keys
print(dictionary.get('Noneexistent', 'Key not found')) # output: Key not found

print("FUNCTIONS: ----------------------------------")
print(1)

def get_details_by_key(key):
    return dictionary.get(key, 'key not')
print(get_details_by_key('Thuki')) 
# Output: ['Ragesvaran', '20', 'black', '5ft 9inch']

print("FUNCTIONS: ----------------------------------")
print(2)

# Functions to get all keys
def get_all_keys():
    return list(dictionary.keys())
print(get_all_keys())
# Output: 
    #['James', 'Lilirose', 'Thuki']

print("FUNCTIONS: ----------------------------------")
print(3)

# Function to unpack and format details
def format_details(key):
    details = dictionary.get(key)
    if details:
        last_name, age, hair_colour, height = details
        return f"{key} {last_name}, Age: {age}, Hair: {hair_colour}, Height: {height}"
    return 'Name not found'

print(format_details('Thuki'))
# Output: 
    # Thuki Ragesvaran, Age: 20, Hair: black, Height: 5ft 9inch

print("FUNCTIONS: ----------------------------------")
print(4)
# Function to return a list of formatted strings for all entries
def get_all_fornatted_details():
    return [format_details(key) for key in dictionary]
print(get_all_fornatted_details())
# Output: 
    # ['James Vilela-Slater, Age: 20, Hair: blond, Height: 5ft 9inch', 
    # 'Lilirose Kent, Age: 19, Hair: redhead, Height: 5ft 7inch', 
    # 'Thuki Ragesvaran, Age: 20, Hair: black, Height: 5ft 9inch']


# Access keys & values from two dicts simultaniously using a for loop:
def access_items_from_two_dicts():
    dict1 = {'a': 1, 'b': 2}
    dict2 = {'x': 10, 'y': 20}

    for (key1, value1), (key2, value2) in zip(dict1.items(), dict2.items()):
        print(f"Dict1 - Key: {key1}, Value: {value1}")
        print(f"Dict2 - Key: {key2}, Value: {value2}")



dict2 = {'x': 10, 'y': 20, 'z':30}
def reverse_values_in_dict(dictionary):
    # get a list of the current keys, then reverse it.
    value_list = [value for value in dictionary.values()]
    value_list.reverse()
    # cr new dictionary now
    rev_dict = {key: values for key, values in zip(dictionary.keys(), value_list)}
    print(f"rev_dict = {rev_dict}")
    return rev_dict
# Output: 
    # new_dict = {'x': 20, 'y': 10}

dict3 = {'x': 10, 'y': 20, 'z':30}
# Skip an item in the dictionary to do operatons on.
for key, val in dict2.itmes():
    print(f"key = {key}")
    print(f"val = {val}")