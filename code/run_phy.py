import sys
from argparse import ArgumentParser, BooleanOptionalAction
from typing import Optional, Sequence, Any
import logging
from pathlib import Path
import time

from phy_utils import copy_most_files, run_phy, copy_changed_files

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


def phy_main(
    data_path: Path,
    results_path: Path,
    params_py_pattern: str,
    temp_path: Path,
    symlink_file_types: list[str],
    interactive: bool
):
    # Locate Phy files.
    logging.info(f"Looking for input data: {data_path}")
    logging.info(f"Looking for Phy params.py matching: {params_py_pattern}")
    params_py_path = list(data_path.glob(params_py_pattern))[0]
    logging.info(f"Found params.py dir: {params_py_path}")

    # Copy Phy files to a writable location.
    # Use symlinks for large binary files.
    phy_path = params_py_path.parent
    phy_temp_path = Path(temp_path, phy_path.relative_to(data_path))
    logging.info(f"Copying Phy dir: {phy_temp_path}")
    copy_most_files(phy_path, phy_temp_path, symlink_file_types)

    # Note the starting time, so we can find files that changed during curation.
    start_time = time.time()

    if interactive:
        # Run Phy.
        run_phy(phy_temp_path)

    # Copy files that changed during curation to a results dir.
    phy_results_path = Path(results_path, phy_path.relative_to(data_path))
    logging.info(f"Copying files that changed to: {phy_results_path}")
    copy_changed_files(phy_temp_path, start_time, phy_results_path)
    
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
        "--results-root", "-r",
        type=str,
        help="Where to write output result files. (default: %(default)s)",
        default="/results"
    )
    parser.add_argument(
        "--params-py-pattern", "-p",
        type=str,
        help="Glob pattern to locate a Phy params.py file within DATA_ROOT. (default: %(default)s)",
        default="**/params.py"
    )
    parser.add_argument(
        "--temp-root", "-t",
        type=str,
        help="Where to write temporary, writable copies of phy files found within DATA_ROOT. (default: %(default)s)",
        default="/tmp"
    )
    parser.add_argument(
        "--symlink_file_types", "-s",
        type=str,
        nargs="*",
        help="List of file types to symlink, instead of copy, when copying read-only files out of DATA_ROOT. (default: %(default)s)",
        default=['.bin', '.dat']
    )
    parser.add_argument(
        "--interactive", "-i",
        help='Whether to bring up the Phy gui interactively (--interactive, the default) or to quietly create cluster_info.tsv (--no-interactive).',
        default=True,
        action=BooleanOptionalAction
    )

    cli_args = parser.parse_args(argv)
    
    results_path = Path(cli_args.results_root)
    run_phy_log = Path(results_path, "run_phy.log")
    run_phy_log.parent.mkdir(exist_ok=True, parents=True)
    set_up_logging(run_phy_log)
    
    data_path = Path(cli_args.data_root)
    temp_path = Path(cli_args.temp_root)
    try:
        phy_main(
            data_path=data_path,
            results_path=results_path,
            params_py_pattern=cli_args.params_py_pattern,
            temp_path=temp_path,
            symlink_file_types=cli_args.symlink_file_types,
            interactive=cli_args.interactive
        )
    except:
        logging.error("Error running Phy.", exc_info=True)
        return -1


if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
