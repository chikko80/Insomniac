import argparse
import json

import insomniac.__version__ as __version__
from insomniac import network
from insomniac.activation import activation_controller
from insomniac.network import HTTP_OK
from insomniac.params import parse_arguments, load_param
from insomniac.utils import *


ACTIVATION_CODE_ARG_NAME = "activation_code"


def run(activation_code="", starter_conf_file_path=None):
    if not __version__.__debug_mode__:
        print_timeless(COLOR_OKGREEN + __version__.__logo__ + COLOR_ENDC)
        print_version()

    activation_code_from_args = get_arg_value(
        ACTIVATION_CODE_ARG_NAME, starter_conf_file_path
    )
    if activation_code_from_args is not None:
        activation_code = activation_code_from_args

    activation_controller.validate(activation_code)
    if not activation_controller.is_activated:
        from insomniac.session import get_insomniac_session

        print_timeless("Using insomniac session-manager without extra-features")
        insomniac_session = get_insomniac_session(starter_conf_file_path)
    else:
        from insomniac.extra_features.session import (
            get_insomniac_extended_features_session,
        )

        insomniac_session = get_insomniac_extended_features_session(
            starter_conf_file_path
        )

    insomniac_session.run()


def is_newer_version_available():
    current_version = __version__.__version__
    latest_version = _get_latest_version("insomniac")
    if latest_version is not None and versiontuple(latest_version) > versiontuple(
        current_version
    ):
        return True, latest_version

    return False, None


def print_version():
    print_timeless_ui(COLOR_HEADER + f"Engine v{__version__.__version__}" + COLOR_ENDC)
    is_new_version_available, latest_version = is_newer_version_available()
    if is_new_version_available and insomniac_globals.is_insomniac():
        print_timeless(
            COLOR_HEADER
            + f"Newer version is available (v{latest_version}). Please run"
            + COLOR_ENDC
        )
        print_timeless(
            COLOR_HEADER
            + COLOR_BOLD
            + "python3 -m pip install insomniac --upgrade"
            + COLOR_ENDC
        )
    print_timeless("")


def _get_latest_version(package):
    latest_version = None
    code, body, _ = network.get(f"https://pypi.python.org/pypi/{package}/json")
    if code == HTTP_OK and body is not None:
        json_package = json.loads(body)
        latest_version = json_package["info"]["version"]
    return latest_version


def get_arg_value(arg_name, conf_path):
    arg_from_cli = get_arg_value_from_cli(arg_name)

    if arg_from_cli is not None:
        return arg_from_cli

    return get_arg_value_from_config_file(arg_name, conf_path)


def get_arg_value_from_cli(arg_name):
    parser = ArgumentParser(add_help=False)
    parser.add_argument(f'--{arg_name.replace("_", "-")}')
    try:
        args, _ = parser.parse_known_args()
    except (argparse.ArgumentError, TypeError):
        return None
    return getattr(args, arg_name)


def get_arg_value_from_config_file(arg_name, conf_file_path):
    if conf_file_path is None:
        return None

    return load_param(conf_file_path, arg_name)


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        pass
