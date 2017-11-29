import argparse
import datetime
import regex as re
import itertools

from jinja2 import Template
from commonapi import Interface, Method, Parameter, Broadcast, Attribute

__comments_regex = r"(\<\*\*((.\n?)*?)\*\*\>)?"
__comments = re.compile(__comments_regex)
__type_regex = r"[\.\w]+\s*(\[\])?"
__parameter_regex = r"\s*" + __comments_regex + r"\s*((" + __type_regex + r")\s+(\w+)\s*)\s*"
__parameter = re.compile(__parameter_regex)
__in_parameter_regex = r"\s*in\s*\{(\s*(" + __parameter_regex + r")*\s*)?\}\s*"
__in_parameter = re.compile(__in_parameter_regex)
__out_parameter_regex = r"\s*out\s*\{(\s*(" + __parameter_regex + r")*\s*)?\}\s*"
__out_parameter = re.compile(__out_parameter_regex)
__error_parameter_regex = r"\s*error [\{]?\s*([\w.]+)\s*[\}]?\s*"
__error_parameter = re.compile(__error_parameter_regex)
__method_regex = r"\s*" + __comments_regex + r"\s*method\s+(\w+)\s*(fireAndForget)?" + \
                 r"\s*\{\s*(" + \
                 r"(" + __in_parameter_regex + r")?" + \
                 r"(" + __out_parameter_regex + r")?" + \
                 r"(" + __error_parameter_regex + r")?" + \
                 r")\s*\}\s*"
__method = re.compile(__method_regex)
__broadcast_regex = r"\s*" + __comments_regex + r"\s*broadcast\s+(\w+)" + \
                    r"\s*\{\s*(" + \
                    r"(" + __out_parameter_regex + r")?" + \
                    r")\s*\}\s*"
__broadcast = re.compile(__broadcast_regex)
__attribute_regex = r"\s*" + __comments_regex + r"\s*attribute\s+(" + __type_regex + r")\s+(\w+)\s*(readonly)?\s*"
__attribute = re.compile(__attribute_regex)
__array_regex = r"\s*" + __comments_regex + r"\s*array\s+(\w+)\s+of\s+(" + __type_regex + r")\s*"
__array = re.compile(__array_regex)
__interface_version_regex = r"\s*version\s*\{\s*major\s+(\d+)\s+minor\s+(\d+)\s*\}\s*"
__interface_version = re.compile(__interface_version_regex)
__interface_regex = r"\s*" + __comments_regex + r"\s*(interface)?\s+(\w+)" + \
                    r"\s*\{((?:[^{}]|(?R))*)}"
__interface = re.compile(__interface_regex)
__package_regex = r"package\s+([\.\w]+)"
__package = re.compile(__package_regex)

__test_fidl = """
package commonapi
interface HelloWorld {
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
        package_name = __package.findall(file_lines)
        interfaces = []
        interfaces_meta = __interface.findall(file_lines)
        if interfaces_meta:
            for interface_meta in interfaces_meta:
                if interface_meta[3] == 'interface':
                    interface_description = None
                    comments_meta = __comments.findall(interface_meta[0])
                    for comment_meta in comments_meta:
                        if len(comment_meta[1]) > 0:
                            interface_description = comment_meta[1]
                    interface_name = interface_meta[4]
                    interface_body = interface_meta[5]
                    interface = Interface(interface_name, interface_description)
                    version_meta = __interface_version.findall(interface_body)
                    if version_meta:
                        interface.set_major(version_meta[0][0])
                        interface.set_minor(version_meta[0][1])
                    methods = parse_methods(interface_body)
                    interface.methods = methods
                    broadcasts = parse_broadcasts(interface_body)
                    interface.broadcasts = broadcasts
                    attributes = parse_attributes(interface_body)
                    interface.attributes = attributes
                    interface.set_package_name(package_name[0])
                    interfaces.append(interface)
        return interfaces


def parse_methods(interface_body):
    """
    This following function is parsing fidl-file
    :param interface_body:
    :return: Raw methods
    """
    methods = []
    methods_meta = __method.findall(interface_body)
    if methods_meta:
        for method_meta in methods_meta:
            method_description = None
            comments_meta = __comments.findall(method_meta[0])
            for comment_meta in comments_meta:
                if len(comment_meta[1]) > 0:
                    method_description = comment_meta[1]
            method_name = method_meta[3]
            method_without_reply = method_meta[4]
            method_body = method_meta[5]
            method = Method(method_name, method_description)
            in_parameters = __in_parameter.findall(method_body)
            for in_parameter in in_parameters:
                if in_parameter[0]:
                    parameters = __parameter.findall(in_parameter[0])
                    for parameter in parameters:
                        parameter_description = None
                        comments_meta = __comments.findall(parameter[0])
                        for comment_meta in comments_meta:
                            if len(comment_meta[1]) > 0:
                                parameter_description = comment_meta[1]
                        parameter_type = parameter[4]
                        parameter_name = parameter[6]
                        param = Parameter(parameter_type, parameter_name, parameter_description)
                        method.inputs.append(param)

            if method_without_reply != "fireAndForget":
                method.outputs = []
                out_parameters = __out_parameter.findall(method_body)
                for out_parameter in out_parameters:
                    if out_parameter[0]:
                        parameters = __parameter.findall(out_parameter[0])
                        for parameter in parameters:
                            parameter_description = None
                            comments_meta = __comments.findall(parameter[0])
                            for comment_meta in comments_meta:
                                if len(comment_meta[1]) > 0:
                                    parameter_description = comment_meta[1]
                            parameter_type = parameter[4]
                            parameter_name = parameter[6]
                            method.outputs.append(Parameter(parameter_type, parameter_name, parameter_description))
            methods.append(method)
    else:
        print("No methods !!")
    return methods


def parse_broadcasts(interface_body):
    """

    :param interface_body:
    :return:
    """
    broadcasts = []
    broadcasts_meta = __broadcast.findall(interface_body)
    if broadcasts_meta:
        for broadcast_meta in broadcasts_meta:
            broadcast_description = None
            comments_meta = __comments.findall(broadcast_meta[0])
            for comment_meta in comments_meta:
                if len(comment_meta[1]) > 0:
                    broadcast_description = comment_meta[1]
            broadcast_name = broadcast_meta[3]
            broadcast_body = broadcast_meta[4]
            broadcast = Broadcast(broadcast_name, broadcast_description)
            out_parameters = __out_parameter.findall(broadcast_body)
            for out_parameter in out_parameters:
                if out_parameter[0]:
                    parameters = __parameter.findall(out_parameter[0])
                    for parameter in parameters:
                        parameter_description = None
                        comments_meta = __comments.findall(parameter[0])
                        for comment_meta in comments_meta:
                            if len(comment_meta[1]) > 0:
                                parameter_description = comment_meta[1]
                        parameter_type = parameter[4]
                        parameter_name = parameter[6]
                        broadcast.parameters.append(Parameter(parameter_type, parameter_name, parameter_description))
            broadcasts.append(broadcast)
    else:
        print("No broadcasts !!")
    return broadcasts


def parse_attributes(interface_body):
    """
    This following function is parsing fidl-file
    :param interface_body:
    :return: Raw methods
    """
    attributes = []
    attributes_meta = __attribute.findall(interface_body)
    if attributes_meta:
        for attribute_meta in attributes_meta:
            attribute_description = None
            comments_meta = __comments.findall(attribute_meta[0])
            for comment_meta in comments_meta:
                if len(comment_meta[1]) > 0:
                    attribute_description = comment_meta[1]
            attribute_type = attribute_meta[3]
            attribute_name = attribute_meta[5]
            attribute = Attribute(attribute_type, attribute_name, attribute_description)
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
