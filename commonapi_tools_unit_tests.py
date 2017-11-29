import argparse
import regex as re
from os.path import isfile

from commonapi_tools import parse_interfaces

__comments_regex = r"(\<\*\*.*\*\*\>)?"
__comments = re.compile(__comments_regex)
__type_regex = r"[\.\w]+\s*(\[\])?"
__method_regex = r"\s*method\s+(\w+)\s*(fireAndForget)?\s*\{"
__method = re.compile(__method_regex)
__broadcast_regex = r"\s*broadcast\s+(\w+)\s*\{"
__broadcast = re.compile(__broadcast_regex)
__attribute_regex = r"\s*attribute\s+(" + __type_regex + r")\s+(\w+)\s*(readonly)?\s*"
__attribute = re.compile(__attribute_regex)
__array_regex = r"\s*array\s+(\w+)\s+of\s+(" + __type_regex + r")\s*"
__array = re.compile(__array_regex)
__interface_regex = r"\s*interface\s+(\w+)\s*\{"
__interface = re.compile(__interface_regex)


def number_of_interfaces(fidl_file):
    """
    This function calculate number of interfaces in fidl_file
    :param fidl_file: Fidl file for simple parsing
    :return: Number of interfaces
    """
    num = 0
    with open(fidl_file, 'r') as file:
        file_lines = file.readlines()
        file_lines = "".join(file_lines)
        interfaces_meta = __interface.findall(file_lines)
        if interfaces_meta:
            num += len(interfaces_meta)
    return num


def number_of_methods(fidl_file):
    """
    This function calculate number of methods in fidl_file
    :param fidl_file: Fidl file for simple parsing
    :return: Number of methods
    """
    num = 0
    with open(fidl_file, 'r') as file:
        file_lines = file.readlines()
        file_lines = "".join(file_lines)
        methods_meta = __method.findall(file_lines)
        if methods_meta:
            num += len(methods_meta)
    return num


def number_of_broadcasts(fidl_file):
    """
    This function calculate number of broadcasts in fidl_file
    :param fidl_file: Fidl file for simple parsing
    :return: Number of broadcasts
    """
    num = 0
    with open(fidl_file, 'r') as file:
        file_lines = file.readlines()
        file_lines = "".join(file_lines)
        broadcasts_meta = __broadcast.findall(file_lines)
        if broadcasts_meta:
            num += len(broadcasts_meta)
    return num


def number_of_attributes(fidl_file):
    """
    This function calculate number of attributes in fidl_file
    :param fidl_file: Fidl file for simple parsing
    :return: Number of attributes
    """
    num = 0
    with open(fidl_file, 'r') as file:
        file_lines = file.readlines()
        file_lines = "".join(file_lines)
        attributes_meta = __attribute.findall(file_lines)
        if attributes_meta:
            num += len(attributes_meta)
    return num


if __name__ == '__main__':
    import os
    os.chdir(os.path.dirname(__file__))
    current_dir = os.getcwd()

    parser = argparse.ArgumentParser()
    parser.add_argument("dir_with_fidls",
                        help="CommonAPI interface /<path>/ to *.fidl")
    args = parser.parse_args()
    if args.dir_with_fidls:
        fidl_files = [os.path.join(args.dir_with_fidls, file) for file in os.listdir(args.dir_with_fidls) if file.endswith(".fidl") and os.path.isfile(os.path.join(args.dir_with_fidls, file))]
        print("fidl_files is "+str(fidl_files))
        print("len(fidl_files) is " + str(len(fidl_files)))
        num_handled_files = 0
        num_of_errors = []
        for file in fidl_files:
            try:
                num_interfaces = number_of_interfaces(file)
                num_methods = number_of_methods(file)
                num_broadcasts = number_of_broadcasts(file)
                num_attributes = number_of_attributes(file)
                interfaces = parse_interfaces(file)
                interfaces_methods = 0
                for interface in interfaces:
                    interfaces_methods += len(interface.methods)
                interfaces_broadcasts = 0
                for interface in interfaces:
                    interfaces_broadcasts += len(interface.broadcasts)
                interfaces_attributes = 0
                for interface in interfaces:
                    interfaces_attributes += len(interface.attributes)
                num_handled_files += 1
                print("num_handled_files is "+str(num_handled_files))
                print("num_interfaces is " + str(num_interfaces))
                print("num_methods is " + str(num_methods))
                print("num_broadcasts is " + str(num_broadcasts))
                print("num_attributes is " + str(num_attributes))
                print("len(interfaces) is " + str(len(interfaces)))
                assert num_interfaces == len(interfaces), "num_interfaces != len(interfaces)"
                assert num_methods == interfaces_methods, "num_methods == interfaces_methods"
                assert num_broadcasts == interfaces_broadcasts, "num_broadcasts == interfaces_broadcasts"
                assert num_attributes == interfaces_attributes, "num_attributes == interfaces_attributes"
            except Exception as ex:
                print("ex is " + str(ex))
                num_of_errors.append((file, num_interfaces, len(interfaces), num_methods, interfaces_methods))
        print("num_handled_files is " + str(num_handled_files))
        print("len(num_of_errors) is " + str(len(num_of_errors)))
        print("num_of_errors is " + str(num_of_errors))