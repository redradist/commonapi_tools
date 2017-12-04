import argparse

from fidl_parser import generate_commonapi_wrappers

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