import subprocess
import json
import datetime
from core.config import logger
import argparse


def parse_date(datestr: str):
    try:
        return datetime.date.fromisoformat(datestr)
    except ValueError:
        raise ValueError(f"Invalid date format '{datestr}'. Should be YYYY-MM-DD.")


def send_command(command: str):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    logger.debug(f'Executed: {command}')

    if error:
        logger.warning(f"stderr: {error.decode('utf-8').strip()}")

    decoded = output.decode('utf-8').strip()
    if not decoded:
        logger.warning("Empty command output.")
        return []

    try:
        return json.loads(decoded)
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON: {decoded}")
        return []


def create_argument_parser():
    parser = argparse.ArgumentParser(
        prog='Djangonauts Statistics',
        description='Pulls info about the PRs open and merged and open Issue from last week.',
        epilog=''
    )
    parser.add_argument(
        '-s',
        '--start_date',
        type=parse_date,
        help='Filters PRs and Issues starting from `start_date`.'
             'e.g. 2024-01-28',
        default=None
    )
    parser.add_argument(
        '-e',
        '--end_date',
        type=parse_date,
        help='Filters PRs and Issues ending on `start_date`.'
             'e.g. 2024-01-28',
        default=None
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true'
    )
    return parser
