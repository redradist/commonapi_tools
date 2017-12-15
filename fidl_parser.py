import argparse
import datetime
import regex as re
import itertools

from jinja2 import Template
from commonapi_types import Interface, Method, Parameter, Broadcast, Attribute, TypeCollection

__comment_regex = r"(\<\*\*(?P<comment>(\<\*\*(*PRUNE)(*FAIL)|.|\n)*?)\*\*\>)?"
__comment = re.compile(__comment_regex)
__type_regex = r"(?P<type>([\.\w]+)\s*(\[\])?)"
__parameter_regex = __comment_regex + \
                    r"\s*((" + __type_regex + r")\s+(?P<name>\w+)\s*)\s*"
__parameter = re.compile(__parameter_regex)
__in_parameter_regex = r"in\s*" + \
                       r"\s*(?P<body>\{((?:[^{}])*)\})"
__in_parameter = re.compile(__in_parameter_regex)
__out_parameter_regex = r"out\s*" + \
                        r"\s*(?P<body>\{((?:[^{}])*)\})"
__out_parameter = re.compile(__out_parameter_regex)
__error_parameter_regex = r"\s*error\s*[\{]?\s*(?P<error_type>[\w.]+)\s*[\}]?\s*"
__error_parameter = re.compile(__error_parameter_regex)
__method_regex = __comment_regex + \
                 r"\s*method\s+(?P<name>\w+)\s*(?P<is_reply>fireAndForget)?" + \
                 r"\s*(?P<body>\{((?:[^\{\}]|(?&body))*)\})"
__method = re.compile(__method_regex)
__broadcast_regex = __comment_regex + \
                    r"\s*broadcast\s+(?P<name>\w+)" + \
                    r"\s*(?P<body>\{((?:[^\{\}]|(?&body))*)\})"
__broadcast = re.compile(__broadcast_regex)
__attribute_regex = __comment_regex + \
                    r"\s*attribute\s+(" + __type_regex + r")\s+(?P<name>\w+)\s*(?P<is_readonly>readonly)?\s*\n"
__attribute = re.compile(__attribute_regex)
__array_regex = __comment_regex + \
                r"\s*array\s+(?P<array_type>\w+)\s+of\s+" + __type_regex + r"\s*\n"
__array = re.compile(__array_regex)
__version_regex = r"version\s*" + \
                  r"{\s*major\s+(?P<major_ver>\d+)\s+minor\s+(?P<minor_ver>\d+)\s*\}\s*"
__version = re.compile(__version_regex)
__interface_regex = __comment_regex + \
                    r"\s*interface\s+(?P<name>\w+)" + \
                    r"\s*(?P<body>\{((?:[^\{\}]|(?&body))*)\})"
__interface = re.compile(__interface_regex)
__type_collection_regex = __comment_regex + \
                          r"\s*typeCollection\s+(?P<name>\w+)" + \
                          r"\s*(?P<body>\{((?:[^\{\}]|(?&body))*)\})"
__type_collection = re.compile(__type_collection_regex)
__import_from_regex = r"import\s+(?P<type>([\*\.\w]+))\s+from\s+\"(?P<fidl_file>([\.\w]+))\""
__import_from = re.compile(__import_from_regex)
__import_regex = r"import\s+model\s+\"(?P<fidl_file>([\.\w]+))\""
__import = re.compile(__import_regex)
__package_regex = r"package\s+(?P<name>[\.\w]+)"
__package = re.compile(__package_regex)

__test_fidl = """
package commonapi

import * from "MyBestTypes.fidl"
import model "MyNewTypes.fidl"

<** This is a test comment for HelloWorld interface **>
interface HelloWorld {
  version {major 1 minor 0}
  
    <** This is
      a multi-line comment **>
      
        <** This is
      a multi-line comment **>
  
  <** This is
      a multi-line * comment **>
  method sayHello {
    in {
      String name
    }
    out {
      String result
    }
  }
  method sayHello2 fireAndForget {
    in {
      String name
    }
  }
  method setSettings {
    in {
      Int32 [] setting
    }
    out {
      Int32 result
    }
  }
  method setSettings2 {
    in {
      Int32 [] setting
    }
    out {
      Int32 result
    }
  }
  broadcast NewName {
  out {
    String name
    }
  }
  broadcast NewName2 {
  out {
    String name
    }
  }
  attribute Int32 aa
}
interface HelloWorld2 {
  version {major 1 minor 0}
  method sayHello {
    in {
      String name
    }
    out {
      String result
    }
  }
  method sayHello2 fireAndForget {
    in {
      String name
    }
  }
  method setSettings {
    in {
      Int32 [] setting
    }
    out {
      Int32 result
    }
  }
  method setSettings2 {
    in {
      Int32 [] setting
    }
    out {
      Int32 result
    }
  }
  broadcast NewName {
  out {
    String name
    }
  }
  broadcast NewName2 {
  out {
    String name
    }
  }
  attribute Int32 aa
}

<**
   @description: This is a test comment for MyTypes typeCollection
 **>
typeCollection MyTypes
{
  version {major 1 minor 0}

}
"""


def parse_type_collections(fidl_file, handled_files=None):
    """
    This following function is parsing fidl-file
    :param fidl_file: File to parse
    :param handled_files: Number of handled files with types
    :return: Raw type_collections
    """
    import os
    if handled_files is None:
        handled_files = set()
    head, tail = os.path.split(fidl_file)
    if tail in handled_files:
        return
    handled_files.add(tail)

    with open(fidl_file, 'r') as file:
        dir_path = os.path.dirname(fidl_file)
        file_lines = file.readlines()
        file_lines = "".join(file_lines)
        file_lines = re.sub(r'\/\/.*\n', '', file_lines)
        packages_name_meta = __package.finditer(file_lines)
        for package_name_meta in packages_name_meta:
            package_name = package_name_meta.group("name")
        type_collections = []
        type_collections_meta = __type_collection.finditer(file_lines)
        if type_collections_meta:
            for type_collection_meta in type_collections_meta:
                type_collection_description = type_collection_meta.group("comment")
                type_collection_name = type_collection_meta.group("name")
                type_collection_body = type_collection_meta.group("body")
                type_collection = TypeCollection(type_collection_name, type_collection_description)
                type_collection.set_package_name(package_name)
                for version_meta in __version.finditer(type_collection_body):
                    type_collection.set_major(version_meta.group("major_ver"))
                    type_collection.set_minor(version_meta.group("minor_ver"))
                    break
                type_collections.append(type_collection)
        else:
            print("No type_collections !!")

        imports_from_meta = __import_from.finditer(file_lines)
        for imp in imports_from_meta:
            head, tail = os.path.split(imp.group("fidl_file"))
            if tail in handled_files:
                continue
            collection_file = dir_path + "/" + imp.group("fidl_file")
            new_type_collections = parse_type_collections(collection_file, handled_files)
            if new_type_collections:
                type_collections.extend(new_type_collections)
        imports_meta = __import.finditer(file_lines)
        for imp in imports_meta:
            head, tail = os.path.split(imp.group("fidl_file"))
            if tail in handled_files:
                continue
            collection_file = dir_path + "/" + imp.group("fidl_file")
            new_type_collections = parse_type_collections(collection_file, handled_files)
            if new_type_collections:
                type_collections.extend(new_type_collections)
        return type_collections


def parse_interfaces(fidl_file):
    """
    This following function is parsing fidl-file
    :param fidl_file:
    :return: Raw interfaces
    """
    with open(fidl_file, 'r') as file:
        file_lines = file.readlines()
        file_lines = "".join(file_lines)
        file_lines = re.sub(r'\/\/.*\n', '', file_lines)
        file_lines = re.sub(r'\/\*\*(.|\n)*?\*\/', '', file_lines)
        packages_name_meta = __package.finditer(file_lines)
        for package_name_meta in packages_name_meta:
            package_name = package_name_meta.group("name")
        print("package_name is " + str(package_name))
        type_collections = parse_type_collections(fidl_file)
        interfaces = []
        interfaces_meta = __interface.finditer(file_lines)
        if interfaces_meta:
            for interface_meta in interfaces_meta:
                interface_description = interface_meta.group("comment")
                interface_name = interface_meta.group("name")
                interface_body = interface_meta.group("body")
                interface = Interface(interface_name, interface_description)
                for version_meta in __version.finditer(interface_body):
                    interface.set_major(version_meta.group("major_ver"))
                    interface.set_minor(version_meta.group("minor_ver"))
                    break
                methods = parse_methods(interface_body, interface_name)
                interface.methods = methods
                broadcasts = parse_broadcasts(interface_body, interface_name)
                interface.broadcasts = broadcasts
                attributes = parse_attributes(interface_body, interface_name)
                interface.attributes = attributes
                interface.is_settable_attribute = \
                    any(not attribute.is_read_only for attribute in attributes)
                interface.type_collections = type_collections
                interface.set_package_name(package_name)
                interfaces.append(interface)
        return interfaces


def parse_methods(interface_body, interface_name):
    """
    This following function is parsing fidl-file
    :param interface_body:
    :return: Raw methods
    """
    methods = []
    methods_meta = __method.finditer(interface_body)
    if methods_meta:
        for method_meta in methods_meta:
            method_description = method_meta.group("comment")
            method_name = method_meta.group("name")
            method_without_reply = method_meta.group("is_reply")
            method_body = method_meta.group("body")
            method = Method(method_name, method_description)
            in_parameters = __in_parameter.finditer(method_body)
            for in_parameter in in_parameters:
                if in_parameter.group("body"):
                    parameters = __parameter.finditer(in_parameter.group("body"))
                    for parameter in parameters:
                        parameter_description = parameter.group("comment")
                        parameter_type = parameter.group("type")
                        parameter_name = parameter.group("name")
                        param = Parameter(interface_name, parameter_type, parameter_name, parameter_description)
                        method.inputs.append(param)
            if method_without_reply != "fireAndForget":
                method.outputs = []
                out_parameters = __out_parameter.finditer(method_body)
                for out_parameter in out_parameters:
                    if out_parameter.group("body"):
                        parameters = __parameter.finditer(out_parameter.group("body"))
                        for parameter in parameters:
                            parameter_description = parameter.group("comment")
                            parameter_type = parameter.group("type")
                            parameter_name = parameter.group("name")
                            method.outputs.append(Parameter(interface_name, parameter_type, parameter_name, parameter_description))
            methods.append(method)
    else:
        print("No methods !!")
    return methods


def parse_broadcasts(interface_body, interface_name):
    """

    :param interface_body:
    :return:
    """
    broadcasts = []
    broadcasts_meta = __broadcast.finditer(interface_body)
    if broadcasts_meta:
        for broadcast_meta in broadcasts_meta:
            broadcast_description = broadcast_meta.group("comment")
            broadcast_name = broadcast_meta.group("name")
            broadcast_body = broadcast_meta.group("body")
            broadcast = Broadcast(broadcast_name, broadcast_description)
            out_parameters = __out_parameter.finditer(broadcast_body)
            for out_parameter in out_parameters:
                if out_parameter.group("body"):
                    parameters = __parameter.finditer(out_parameter.group("body"))
                    for parameter in parameters:
                        parameter_description = parameter.group("comment")
                        parameter_type = parameter.group("type")
                        parameter_name = parameter.group("name")
                        broadcast.parameters.append(Parameter(interface_name, parameter_type, parameter_name, parameter_description))
            broadcasts.append(broadcast)
    else:
        print("No broadcasts !!")
    return broadcasts


def parse_attributes(interface_body, interface_name):
    """
    This following function is parsing fidl-file
    :param interface_body:
    :return: Raw methods
    """
    attributes = []
    attributes_meta = __attribute.finditer(interface_body)
    if attributes_meta:
        for attribute_meta in attributes_meta:
            attribute_description = attribute_meta.group("comment")
            attribute_type = attribute_meta.group("type")
            attribute_name = attribute_meta.group("name")
            attribute_is_readonly = attribute_meta.group("is_readonly")
            attribute = Attribute(interface_name, attribute_type, attribute_name, attribute_description)
            attribute.set_is_readonly(attribute_is_readonly == "readonly")
            attributes.append(attribute)
    else:
        print("No attributes !!")
    return attributes
