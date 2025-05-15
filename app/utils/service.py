"""Utility functions for game automation"""
import importlib
import time
import os

import app
from app.utils.session import status


# set the app stop flag
class GracefulExit(Exception):
    pass

def import_parseargs(args):
    for key, value in vars(args).items():
        if value is not None:
            os.environ["HM_" + key.upper()] = str(value)

def parse_call_function(call_function):
    """
    Dynamically parse a dotted path like 'a.b.c.d.e' into:
    - importable module path: 'a.b.c.d'
    - classname (optional): 'e', if 'd' is a class
    - method_name: final part
    """

    parts = call_function.split(".")
    for i in range(len(parts) - 1, 0, -1):
        module_path = ".".join(parts[:i])
        attr_chain = parts[i:]

        try:
            module = importlib.import_module(module_path)

            # Walk the attribute chain to reach the method/function
            obj = module
            for attr in attr_chain[:-1]:
                obj = getattr(obj, attr)

            return {
                'package': module_path,
                'classname': attr_chain[-2] if len(attr_chain) > 1 else None,
                'method': attr_chain[-1]
            }
        except (ModuleNotFoundError, AttributeError):
            continue

    raise ImportError(f"Could not resolve call_function path: {call_function}")

def run_package(args: dict, log):
    r = None
    package_name = f"{args['package']}"

    try:
        package = importlib.import_module(package_name)
    except ImportError:
        log.exception(f"run_package: Could not find or import the package '{package_name}'")
        raise

    if args.get('classname'):
        try:
            obj = getattr(package, args['classname'])
            method = getattr(obj, args['method'])
            msg = f"Calling package {package_name} method {args['classname']}::{args['method']}"
            r = method(*args.get('args', []))
        except AttributeError as e:
            log.exception(f"run_package: {e}")
            raise
    else:
        msg = ""
        try:
            func = getattr(package, args['method'])
            msg = f"{package_name}.{args['method']}({args.get('args', [])})"
            r = func(*args.get('args', []))
        except AttributeError as e:
            log.exception(f"run_package: {e}")
            raise
        except TypeError as e:
            log.exception(f"run_package: Function call failed due to argument mismatch. {msg} -> {e}")
            raise
        except KeyboardInterrupt as e:
            log.exception(f"run_package: Exit on user input: Ctrl + C. {msg} -> {e}")
            raise
        except Exception as e:
            log.exception(f"run_package: Exception: {msg} -> {e}")
            raise

    log.info(f"run_package: Call {msg} return: {r}")

    return r

def check_shutdown():
    app.STOP_SIGNALED = status().exists("game:stop")

    if app.STOP_SIGNALED:
        raise GracefulExit(f"{__name__} received shutdown signal.")

    # self.close()
    # self.process.terminate()
    return app.STOP_SIGNALED

def clear_shutdown():
    app.STOP_SIGNALED = False
    status().remove("game:stop")

def wait(seconds):
    """Pauses execution for a specified time"""
    time.sleep(seconds)
