import argparse
import datetime
import regex as re
import itertools

from jinja2 import Template
from commonapi import Interface, Method, Parameter, Broadcast, Attribute

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
                    r"\s*attribute\s+(" + __type_regex + r")\s+(?P<name>\w+)\s*(readonly)?\s*\n"
__attribute = re.compile(__attribute_regex)
__array_regex = __comment_regex + \
                r"\s*array\s+(?P<array_type>\w+)\s+of\s+" + __type_regex + r"\s*\n"
__array = re.compile(__array_regex)
__interface_version_regex = r"version\s*" + \
                            r"{\s*major\s+(?P<major_ver>\d+)\s+minor\s+(?P<minor_ver>\d+)\s*\}\s*"
__interface_version = re.compile(__interface_version_regex)
__interface_regex = __comment_regex + \
                    r"\s*interface\s+(?P<name>\w+)" + \
                    r"\s*(?P<body>\{((?:[^\{\}]|(?&body))*)\})"
__interface = re.compile(__interface_regex)
__package_regex = r"package\s+(?P<name>[\.\w]+)"
__package = re.compile(__package_regex)

__test_fidl = """
package commonapi

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
"""


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
        packages_name_meta = __package.finditer(file_lines)
        for package_name_meta in packages_name_meta:
            package_name = package_name_meta.group("name")
        print("package_name is " + str(package_name))
        interfaces = []
        interfaces_meta = __interface.finditer(file_lines)
        if interfaces_meta:
            for interface_meta in interfaces_meta:
                interface_description = interface_meta.group("comment")
                interface_name = interface_meta.group("name")
                interface_body = interface_meta.group("body")
                interface = Interface(interface_name, interface_description)
                for version_meta in __interface_version.finditer(interface_body):
                    interface.set_major(version_meta.group("major_ver"))
                    interface.set_minor(version_meta.group("minor_ver"))
                    break
                methods = parse_methods(interface_body, interface_name)
                interface.methods = methods
                broadcasts = parse_broadcasts(interface_body, interface_name)
                interface.broadcasts = broadcasts
                attributes = parse_attributes(interface_body, interface_name)
                interface.attributes = attributes
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
            attribute = Attribute(interface_name, attribute_type, attribute_name, attribute_description)
            attributes.append(attribute)
    else:
        print("No attributes !!")
    return attributes


def generate_commonapi_wrappers(templates, fidl_file, dir_to_save, wrappers_names=[]):
    if len(templates) != 2:
        raise ValueError("Size of templates argument should be 2 : CommonAPI Client and CommonAPI Service")

    if len(dir_to_save) == 0:
        raise ValueError("dir_to_save is empty !!")
    elif dir_to_save[len(dir_to_save) - 1] != '/':
        dir_to_save += '/'

    interfaces = parse_interfaces(fidl_file)
    if len(interfaces) == 0:
        raise ValueError("Size of interfaces is zero. No work to do man !?")

    current_datetime = datetime.datetime.now()
    current_date = current_datetime.strftime("%d %b %Y")

    with open(templates[0], 'r') as file:
        lines = file.readlines()
        lines = "".join(lines)
        for interface, wrapper_name in itertools.zip_longest(interfaces, wrappers_names):
            template = Template(lines)
            files_output = template.render(interface=interface,
                                           date=current_date)
            if wrapper_name is None:
                wrapper_name = interface.name
            with open(dir_to_save + wrapper_name + "Client.hpp", mode='w') as file_to_save:
                file_to_save.write(files_output)

    with open(templates[1], 'r') as file:
        lines = file.readlines()
        lines = "".join(lines)
        for interface, wrapper_name in itertools.zip_longest(interfaces, wrappers_names):
            template = Template(lines)
            files_output = template.render(interface=interface,
                                           date=current_date)
            if wrapper_name is None:
                wrapper_name = interface.name
            with open(dir_to_save + wrapper_name + "Service.hpp", mode='w') as file_to_save:
                file_to_save.write(files_output)


if __name__ == '__main__':
    import os
    os.chdir(os.path.dirname(__file__))
    current_dir = os.getcwd()

    parser = argparse.ArgumentParser()
    parser.add_argument("capi_interface",
                        help="CommonAPI interface /<path>/<name>.fidl")
    parser.add_argument("dir_to_save",
                        help="CommonAPI /<path_to_generate>/")
    parser.add_argument("--capi_client",
                        help="Template for generating CommonAPI Client",
                        default=os.path.join(current_dir, "CommonAPIClientDefault.hpp.jinja2"))
    parser.add_argument("--capi_service",
                        help="Template for generating CommonAPI Service",
                        default=os.path.join(current_dir, "CommonAPIServiceDefault.hpp.jinja2"))
    args = parser.parse_args()
    try:
        generate_commonapi_wrappers([args.capi_client, args.capi_service],
                                     args.capi_interface,
                                     args.dir_to_save)
    except Exception as ex:
        print("ex is " + str(ex))
