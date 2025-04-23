import argparse
import importlib
import os
import sys
from logging import Logger
from typing import Optional
from app.utils.service import GracefulExit

log: Optional[Logger] = None

def main():
    # """Run administrative tasks."""
    selfname = os.path.basename(sys.argv[0])
    # Create the parser
    parser = argparse.ArgumentParser(
        description="A Python application where arguments specify Python packages, classes, and methods to use.",
        epilog=(
            "Examples of usage:\n"
            f" {selfname} --classname MyClass --method my_method --args arg1 arg2 mypackage1\n"
            f" {selfname} mypackage2 standalone_function --args val1 val2\n"
            "\n"
            "Replace 'mypackage1' and 'mypackage2' with actual Python package names available in your environment.\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-v', "--verbosity",
        action="store",
        type=int,
        choices=range(0, 5),  # Allow 0-4 (adjusted for DEBUG mode)
        help="Verbosity level: 0=NOTSET, 1=DEBUG, 2=INFO, 3=WARNING, 4=ERROR, 5=CRITICAL",
        default=1  # Default to DEBUG
    )

    parser.add_argument(
        "--log-file",
        required=False,
        type=str,
        help="Specify log file. Default: stdout",
        default=None
    )

    parser.add_argument(
        "--data-dir",
        required=False,
        type=str,
        help="Specify application data directory. Default: <app>/data",
        default=None
    )

    parser.add_argument(
        "--share-dir",
        required=False,
        type=str,
        help="Specify application data share directory. Default: <app>/share",
        default=None
    )

    parser.add_argument(
        "--driver-path",
        required=False,
        type=str,
        help="Specify driver binary path. Default: <app>/bins/drivers/MacroRecorder/MacroRecorder.exe",
        default=None
    )

    # Add arguments
    parser.add_argument(
        "package",
        type=str,
        help="The name of the Python package to import and use. Must be installed or available in the environment.",
    )
    parser.add_argument(
        "--runtests",
        help="Run the unit tests.",
        action="store_true"
    )

    # parser.add_argument(
    #     "-c", "--console",
    #     help="Show a console with output. "
    #         "By default the app runs hidden in the background not to interfere with other apps.",
    #     action="store_true"
    # )
    parser.add_argument(
        "--classname",
        type=str,
        help="The name of the class to instantiate in the package. If omitted, calls a standalone function."
    )

    # Create a mutually exclusive group
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "method",
        nargs="?",
        type=str,
        help=(
            "The name of the method to call on the class object, "
            "or the standalone function to call if --classname is not specified."
        )
    )
    group.add_argument(
        "--method",  # ✅ Optional argument
        type=str,
        dest="method",  # ✅ Ensures both options store in `args.method`
        help="Alias for the positional 'method' argument."
    )

    parser.add_argument(
        "--args", '-a',
        type=str,
        nargs="*",
        help="Arguments to pass to the method or function. Provide space-separated values.",
        default=[]
    )

    # Parse the arguments
    args = parser.parse_args()
    # args = lambda: None
    # args.package = 'utils.session'
    # args.method = 'write_session'
    # args.args = ["run-action-done", 1]
    # args.verbosity = 1
    # args.runtests = False
    # args.classname = False
    bootstrap(args)

def bootstrap(args):
    global log

    # import args into session
    import_parseargs(args)

    # building settings
    from app import settings, daemon, result
    from app.utils.log import logger
    settings.check_settings()

    # set logging
    log = logger('cli')

    if args.runtests:
        pass
        # from app.tests import session_tests
        # session_tests.run_tests()
    else:
        run_package(args)


def import_parseargs(args):
    for key, value in vars(args).items():
        if value is not None:
            os.environ["HM_" + key.upper()] = str(value)

def run_package(args):
    global log
    #log = settings.logger('cli')

    # Dynamically import the specified package
    try:
        package = importlib.import_module(f"app.{args.package}")
    except ImportError:
        log.error(f"Error: Could not find or import the package '{args.package}'.")
        sys.exit(1)

    # If a class is specified, instantiate it and call the method
    if args.classname:
        try:
            cls = getattr(package, args.classname)
            obj = cls()  # Assumes the class has a no-argument constructor
            method = getattr(obj, args.method)
            log.info(
                f"Calling method '{args.method}' on an instance of class '{args.classname}' from package '{args.package}'...")

            r = method(*args.args)

            log.info(f"Result:{r}")
            print(f"{r}")

        except AttributeError as e:
            log.error(f"Error: {e}")
            sys.exit(1)
    else:
        # Otherwise, call the standalone function
        try:
            func = getattr(package, args.method)
            log.debug(f"Call: {args.package}.{args.method}({args.args})")

            r = func(*args.args)

            log.debug(f"Result: {r}")
            print(f"{r}")

            sys.exit(r and 0 or 2)
        except AttributeError as e:
            log.exception(f"Error: {e}")
            raise
            #sys.exit(1)
        except TypeError as e:
            log.exception(f"Error: Function call failed due to argument mismatch. {e}")
            raise
            #sys.exit(1)
        except KeyboardInterrupt as e:
            log.exception(f"Exit on user input: Ctrl + C. {e}")
            sys.exit()
        except GracefulExit as e:
            log.exception(f"Exit on signal. {e}")
            sys.exit()
        except Exception as e:
            log.exception(f"{e}")
            raise


if __name__ == "__main__":
    main()
