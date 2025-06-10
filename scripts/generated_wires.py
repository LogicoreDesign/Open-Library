#!/usr/bin/env python3

# generated_wires.py script creates wires and "reg" signals
# To call this script in a Verilog file it should follow one of the following patterns:
#   `include "generated_wires.vs" /*
#             Name1, Size
#             Name2, Size
#             Name3, Size
#             ...
#             */
# Default values are: Size = 1 bit.
# When called from another script an additional argument can passed to create "reg" type signals instead of "wires".

import re
from vt_colours import *

vs_name_suffix = sys.argv[1].removesuffix(".vs")
vs_name = f"generated_wires_{vs_name_suffix}.vs"


class wire:
    def __init__(self, wire_properties) -> None:
        wire_properties = [wire_property.strip() for wire_property in wire_properties]
        self.set_wire_name(wire_properties[0])
        self.set_wire_size(wire_properties[1])

    def set_wire_name(self, wire_name):
        if "name=" in wire_name:
            wire_name = wire_name.split("name=")[1]
        if wire_name == "":
            print_coloured(ERROR, "You should give a name to the wire.")
            exit(1)
        else:
            self.name = wire_name

    def set_wire_size(self, wire_size):
        if "size=" in wire_size:
            wire_size = wire_size.split("=")[1]
        if wire_size == "":
            self.size = "1"
        else:
            self.size = wire_size


# Evaluates and processes an arithmetic expression within a string.
# Args:
#   - input_string (str): A string containing arithmetic expressions to be evaluated.
# Returns:
#   - result (str): The result of the evaluated arithmetic expressions in the input string.
# This function splits the input string into parts based on arithmetic operators (+, -) while preserving the operators. If the parts don't form a valid arithmetic expression, it raises an error indicating an invalid length of the input string. It then iterates through the parts to evaluate the arithmetic expression. The evaluation process continues until it either forms a valid arithmetic expression or, if not valid, appends the remaining parts as they are to the result string.
def string_eval_arithmetic(input_string):
    parts = [part.strip() for part in re.split(r"([-+])", input_string)]

    if len(parts) % 2 != 1:
        print_coloured(ERROR, f"Port does not have a valid length: {input_string}")
        exit(1)

    arithmetic_str = ""
    for index in range(len(parts)):
        arithmetic_str = f"{parts[-(index+1)]}" + arithmetic_str
        try:
            arithmetic = eval(arithmetic_str)
            result = str(arithmetic)
        except (NameError, SyntaxError):
            # If it's not a valid arithmetic expression, add it to the result as is
            if arithmetic > 0:
                result = "".join(parts[:-index]) + f"+{arithmetic}"
            elif arithmetic < 0:
                result = "".join(parts[:-index]) + str(arithmetic)
            else:
                result = "".join(parts[:-index])
            break

    return result


def create_vs(wires):
    vs_content, existing_wires = read_file(vs_name)
    if vs_content == "":
        vs_content = (
            f'  // Automatically generated "wire" and "reg" for {vs_name_suffix}\n'
        )
    # Check if there is already a new line separating the previously generated set of signals from the new one
    elif not vs_content.endswith("\n\n"):
        vs_content += "\n"

    if (len(sys.argv) > 3) and (sys.argv[3] == "variable"):
        signal_type = "reg"
    else:
        signal_type = "wire"

    for wire in wires:
        if wire.name not in existing_wires:
            if wire.size != "1":
                length = string_eval_arithmetic(f"{wire.size}-1")
                vs_content += f"  {signal_type} [{length}:0] {wire.name};\n"
            else:
                vs_content += f"  {signal_type} {wire.name};\n"

    write_vs(vs_content, vs_name)


def find_file_recursive(directory, search_filename):
    # Walk through the directory tree recursively
    for _, _, files in os.walk(directory):
        for filename in files:
            # Check if the filename matches the search pattern
            if filename == search_filename:
                return True

    return False


def write_vs(content, file_name):
    with open(file_name, "w") as file:
        file.write(content)


def read_file(file_name):
    file_path = find_file_under_dir(os.getcwd(), file_name)
    # Regular expression pattern to match variable names
    pattern = r"\b(?:wire|reg)\s+(\[.*?\])?\s*(\w*?)\s*;"
    existing_wires = []
    content = ""

    if file_path != "":
        with open(file_path, "r") as file:
            content = file.read()
        os.remove(file_path)

    # Find all matches in the text using the pattern
    matches = re.findall(pattern, content)

    # Extract variable names from matches
    for match in matches:
        existing_wires.append(match[1])

    return content, existing_wires


def find_file_under_dir(start_directory, file_name):
    file_path = ""
    for root, _, files in os.walk(start_directory):
        if file_name in files:
            # Print the full path of the file
            file_path = os.path.join(root, file_name)
    return file_path


def parse_arguments():
    wires = []
    if len(sys.argv) > 2:
        wires_properties = sys.argv[2].split("\n")
        for wire_properties in wires_properties:
            wire_properties = wire_properties.split(",")
            if wire_properties != [""]:
                wires.append(wire(wire_properties))
    return wires


if __name__ == "__main__":
    wires = parse_arguments()
    create_vs(wires)
