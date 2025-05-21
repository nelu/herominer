import argparse
import os
import sys
from logging import Logger
from typing import Optional
from app.utils.service import GracefulExit, run_package, import_parseargs

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

    # import args into ENV
    import_parseargs(args)

    # building settings
    from app import settings, daemon, result
    from app.utils.log import logger
    settings.check_settings()

    # set logging
    log = logger('cli')
    r = False

    if args.runtests:
        pass
        # from app.tests import session_tests
        # session_tests.run_tests()
    else:
        # Dynamically import and run the specified package
        try:
            args.package = f"app.{args.package}"
            r = run_package(vars(args), log)
            print(r)
        except (KeyboardInterrupt, GracefulExit) as e:
            r = True
        except Exception as e:
            log.exception(f"bootstrap: exception - {e}")
            r = False

    sys.exit(r and 0 or 1)


if __name__ == "__main__":
    main()
