import sys
import os
from argparse import ArgumentParser
from typing import Optional, Sequence
import logging
from pathlib import Path

from phy.apps.template import template_gui


def set_up_logging(log_path: Path):
    logging.root.handlers = []
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_path)
    ]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=handlers
    )


def phy_gui(
    params_py: Path
):
    """Run phy itself, similar to command line: phy template-gui params.py"""

    # Disable Chromium "sandboxing" to allow running Phy as root.
    # We don't want to run as root!
    # But misconfigured Docker containers or Code Ocean capsules might force us to be root.
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

    logging.info(f"Running Phy for {params_py}")
    template_gui(params_py)
    logging.info("OK")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = ArgumentParser(description="Launch Phy and copy files that changed during curation.")

    parser.add_argument(
        "--data-root", "-d",
        type=str,
        help="Where to find and read input data files. (default: %(default)s)",
        default="/data"
    )
    parser.add_argument(
        "--params-py-pattern", "-p",
        type=str,
        help="Glob pattern to locate a Phy params.py file within DATA_ROOT. (default: %(default)s)",
        default="**/params.py"
    )

    cli_args = parser.parse_args(argv)

    data_path = Path(cli_args.data_root)
    logging.info(f"Looking for Phy params.py matching: {cli_args.params_py_pattern}")
    params_py_path = list(data_path.glob(cli_args.params_py_pattern))[0]
    logging.info(f"Found params.py: {params_py_path}")

    run_phy_log = Path(params_py_path.parent, "run_phy.log")
    set_up_logging(run_phy_log)

    try:
        phy_gui(params_py_path)
    except:
        logging.error("Error running Phy.", exc_info=True)
        return -1


if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
