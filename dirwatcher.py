#!/usr/bin/env python2

__author__ = "Mike Boring"

"""
Dirwatcher

Long-Running Program with signal handling and logging.

`dirwatcher.py` program will continually search within all files in the directory
for a "magic string", which is provided as a command line argument.

### Objectives
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


def create_parser():
    """Creates an argument parser object."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--todir',
                        help='destination directory for downloaded images')
    parser.add_argument('logfile', help='apache logfile to extract urls from')

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


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    global exit_flag
    # log the associated signal name
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)
    logger.warning(f'Received signal {signal.Signals(sig_num).name}')
    #logger.warning('Received Exit Signal')
    exit_flag = True


def watch_directory():
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)
    logger.warning(f'[{os.getpid()}] Watch directory now.')
    #print(f'[{os.getpid()}] Watch directory now.')


def main():
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    while not exit_flag:
        try:
            # call my directory watching function
            watch_directory()
        except Exception as e:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            logger = logging.getLogger(__name__)
            logger.error('Error Received and Logged.')

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%

        # time.sleep(polling_interval)
        time.sleep(2)

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start


if __name__ == '__main__':
    main()
