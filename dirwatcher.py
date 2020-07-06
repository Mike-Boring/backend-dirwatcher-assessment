#!/usr/bin/env python2

__author__ = "Mike Boring"

"""
Dirwatcher

Long-Running Program with signal handling and logging.

`dirwatcher.py` program will continually search within all files in the directory
for a "magic string", which is provided as a command line argument.

# Objectives
 - Create a long-running program
 - Demonstrate OS signal handling (SIGTERM, SIGINT)
 - Demonstrate program logging
 - Use exception handling to keep the program running
 - Structure your code repository using best practices
 - Read a set of requirements and deliver on them, asking for clarification if anything is unclear

TODO:

1. accept command line arguments with argparse
        add argument for txt file to monitor, magic word to look for
2. monitor a given directory for text files created in that directory
        timed polling loop with sleep to check directory
3. If the magic string is found in a file, your program should log a message
        indicating which file, and the line number within the file where the magic text
        was found. Just one magic string location logged per line.
4. program should terminate itself when catching SIGTERM or SIGINT signals
        (be sure to log a termination message). OS signal handler
5. Handle and log different exceptions such as "file not found", "directory does not exist",
        as well as handle and report top-level unknown exceptions so that your program stays alive
6. Include a startup and shutdown banner in your logs and report the total runtime (uptime)
        within your shutdown log banner

"""

import os
import sys
import argparse

import signal
import time
import logging
import datetime


def create_parser():
    """Creates an argument parser object."""
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Directory path to watch')
    parser.add_argument('magic', help='String to watch for.')
    parser.add_argument(
        '-e', '--ext', help='Text file extension to watch.')
    parser.add_argument('-i', '--interval', type=int,
                        help='Number of seconds between polling.', default=1)

    return parser


# def main(args):
#     """Parses args, scans for URLs, gets images from URLs."""
#     parser = create_parser()

#     if not args:
#         parser.print_usage()
#         sys.exit(1)

#     parsed_args = parser.parse_args(args)

#     img_urls = read_urls(parsed_args.logfile)

#     if parsed_args.todir:
#         download_images(img_urls, parsed_args.todir)
#     else:
#         print('\n'.join(img_urls))


exit_flag = False
start_time = ''


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    global exit_flag
    global start_time
    # log the associated signal name
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    logger.warning(f'Received Exit Signal: {signal.Signals(sig_num).name}')
    logger2 = logging.getLogger(__name__)
    logger2.setLevel(logging.INFO)
    logger2.info(
        f"""
        ----------------------------------------------------
        \tStopped {sys.argv[0]}
        \tUptime was: {datetime.datetime.now() - start_time}
        ----------------------------------------------------
        """
    )

    exit_flag = True


def start_watch_directory(watch_directory, magic_text, polling_interval, ext):
    """Watch a directory for new files being added and scan for magic word."""
    if not os.path.isdir(f'{watch_directory}'):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.ERROR)
        logger.error(
            f'Directory or file not found:{os.getcwd()}/{watch_directory}')
    else:
        # create dictionary from directory
        logger = logging.getLogger(__name__)
        # logger.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        logger.info(
            f'Watching {watch_directory} for "{magic_text}" now.')

        detect_added_files(watch_directory)
        detect_deleted_file(watch_directory)
    # compare the previous dictionary of directory with current dictionary of directory


def detect_added_files(watch_directory):
    """Detect when a file is added to directory being watched."""
    # if new files , then run scan_single_file()

    pass


def detect_deleted_file(watch_directory):
    """Detect when a logged file is deleted from directory being watched."""
    # if files deleted from directory, then log message
    # logging.basicConfig(level=logging.WARNING)
    # logger = logging.getLogger(__name__)
    # logger.warning('Detected deleted file.')


def scan_single_file(file_name):
    """Scan a file for the specified magic word."""
    pass


def main(args):
    """Parses args, scans directory for magic words then logs results then repeats scan according to interval."""
    global start_time
    start_time = datetime.datetime.now()
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s [%(threadName)-12s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger.setLevel(logging.INFO)
    logger.info(f"""
    ----------------------------------------------------
    \tRunning {sys.argv[0]}
    \tStarted on {start_time}
    ----------------------------------------------------
    """)
    parser = create_parser()
    if not args:
        parser.print_usage()
        sys.exit(1)

    parsed_args = parser.parse_args(args)
    #print('parsed_args', parsed_args)
    ext = parsed_args.ext
    polling_interval = parsed_args.interval
    magic_text = parsed_args.magic
    watch_directory = parsed_args.path

    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    while not exit_flag:
        try:
            # call my directory watching function
            start_watch_directory(
                watch_directory, magic_text, polling_interval, ext)
        except Exception as e:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            logger = logging.getLogger(__name__)
            logger.error('Error Received and Logged.')

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%

        time.sleep(polling_interval)

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start


if __name__ == '__main__':
    main(sys.argv[1:])
