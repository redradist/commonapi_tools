import argparse
import datetime
import itertools

from jinja2 import Template
from fidl_parser import parse_interfaces


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

    if templates[0]:
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

    if templates[1]:
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
    parser.add_argument("--default",
                        action='store_true',
                        help="Choose default templates if --capi_client or --capi_service was not set")
    parser.add_argument("--capi_client",
                        help="Template for generating CommonAPI Client")
    parser.add_argument("--capi_service",
                        help="Template for generating CommonAPI Service")
    args = parser.parse_args()
    if args.default:
        if not args.capi_client:
            args.capi_client = os.path.join(current_dir, "CommonAPIClientDefault.hpp.jinja2")
        if not args.capi_service:
            args.capi_service = os.path.join(current_dir, "CommonAPIServiceDefault.hpp.jinja2")
    try:
        generate_commonapi_wrappers([args.capi_client, args.capi_service],
                                     args.capi_interface,
                                     args.dir_to_save)
    except Exception as ex:
        print("ex is " + str(ex))
