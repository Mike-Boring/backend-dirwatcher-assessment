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

DONE 1. accept command line arguments with argparse
        add argument for txt file to monitor, magic word to look for
DONE 2. monitor a given directory for text files created in that directory
        timed polling loop with sleep to check directory
3. If the magic string is found in a file, your program should log a message
        indicating which file, and the line number within the file where the magic text
        was found. Just one magic string location logged per line.
DONE 4. program should terminate itself when catching SIGTERM or SIGINT signals
        (be sure to log a termination message). OS signal handler
5. Handle and log different exceptions such as "file not found", "directory does not exist",
        as well as handle and report top-level unknown exceptions so that your program stays alive
DONE 6. Include a startup and shutdown banner in your logs and report the total runtime (uptime)
        within your shutdown log banner

"""

import os
import sys
import argparse

import signal
import time
import logging
import datetime

exit_flag = False
start_time = ''
current_directory_dict = {}


def create_parser():
    """Creates an argument parser object."""
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Directory path to watch')
    parser.add_argument('magic', help='String to watch for.')
    parser.add_argument(
        '-e', '--ext', help='Text file extension to watch.')
    parser.add_argument('-i', '--interval', type=int,
                        help='Number of seconds between polling.', default=3)

    return parser


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
    logger.warning(
        f'Received OS Process Signal, {signal.Signals(sig_num).name}')
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
        scan_full_directory(watch_directory, ext, magic_text)
        detect_deleted_file(watch_directory)
        detect_added_files(watch_directory, ext, magic_text)


def detect_added_files(watch_directory, ext, magic_text):
    """Detect when a file is added to directory being watched."""
    global current_directory_dict
    new_directory_list = os.listdir(watch_directory)
    if len(new_directory_list) == 0:
        return
    else:
        for f in new_directory_list:
            if f.endswith(ext) and f not in current_directory_dict:
                print(f'New file detected: {f}')
                current_directory_dict[f] = 0
                # print('new current dictionary: ', current_directory_dict)
                scan_single_file(watch_directory, f, magic_text)
            else:
                continue


def detect_deleted_file(watch_directory):
    """Detect when a logged file is deleted from directory being watched."""
    global current_directory_dict
    new_directory_list = os.listdir(watch_directory)
    if len(new_directory_list) == 0:
        return
    else:
        for dict_entry in current_directory_dict:
            if dict_entry not in new_directory_list:
                del current_directory_dict[dict_entry]
                print('Deleted File Detected and Removed from Directory Dict')
    # if files deleted from directory, then log message
    # logging.basicConfig(level=logging.WARNING)
    # logger = logging.getLogger(__name__)
    # logger.warning('Detected deleted file.')


def scan_single_file(watch_directory, file_name, magic_text):
    """Scan a file for the specified magic word."""
    with open(f'{watch_directory}/{file_name}') as f:  # open individual file
        #text = f.read()
        for i, line in enumerate(f):
            # loop thru and read line by line looking for magic word, then keep track of line in overall wtched dictionary. enumerate
            if magic_text in line.lower():
                logger = logging.getLogger(__name__)
                logger.setLevel(logging.INFO)
                logger.info(f'Magic Word found in {file_name} on line {i+1}')
                global current_directory_dict
                current_directory_dict[file_name] = i+1
            else:
                #print('scan found no magic text')
                continue


def scan_full_directory(watch_directory, ext, magic_text):
    """Scan a full directory for the specified magic word and new text with magic words."""
    global current_directory_dict
    if os.path.isdir(f'{watch_directory}'):  # confirm directory exists
        # creates list of directory contents
        new_directory_list = os.listdir(watch_directory)
        if not len(new_directory_list) == 0:  # confirm there is a file on the directory
            #print('new directory list ln 155: ', new_directory_list)
            for single_file in new_directory_list:
                if single_file.endswith(ext):  # sort files ending in ext
                    with open(f'{watch_directory}/{single_file}') as f:  # open individual file
                        # print(
                        #     f'current global directory dict ln 160: {current_directory_dict} - {datetime.datetime.now()}')
                        #text = f.read()
                        for i, line in enumerate(f):
                            # loop thru and read line by line looking for magic word, then keep track of line in overall wtched dictionary. enumerate
                            if magic_text in line.lower():
                                if single_file in current_directory_dict:
                                    # print(
                                    #     f'current_directory_dict[single_file]: ', current_directory_dict[single_file])
                                    if current_directory_dict[single_file] < i+1:
                                        logger = logging.getLogger(__name__)
                                        logger.setLevel(logging.INFO)
                                        logger.info(
                                            f'Magic Word found in {single_file} on line {i+1}')
                                        current_directory_dict[single_file] = i+1
                                else:
                                    current_directory_dict[single_file] = i+1
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
    magic_text = parsed_args.magic.lower()
    watch_directory = parsed_args.path

    global current_directory_dict
    if not os.path.isdir(f'{watch_directory}'):
        pass
    else:
        current_directory_list = os.listdir(watch_directory)
        if len(current_directory_list) != 0:
            for f in current_directory_list:
                if f.endswith(ext):                 # first scan of directory and add
                    # those with right ext to global current_directory_dict
                    current_directory_dict[f] = 0
                    print(f'New file detected: {f}')
                    # scan individual file for magic text
                    scan_single_file(watch_directory, f, magic_text)

    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    while not exit_flag:
        try:
            start_watch_directory(
                watch_directory, magic_text, polling_interval, ext)
        except ValueError:
            logger = logging.getLogger(__name__)
            logger.error('Value Error Received and Logged.')
            # raise
        except TypeError:
            logger = logging.getLogger(__name__)
            logger.error('Type Error Received and Logged.')
            # raise
        except RuntimeError:
            logger = logging.getLogger(__name__)
            logger.error('RunTime Error Received and Logged.')
            # raise
        except Exception as e:
            # This is an UNHANDLED exception
            logger = logging.getLogger(__name__)
            logger.error('Error Received and Logged.')
            raise
        time.sleep(polling_interval)


if __name__ == '__main__':
    main(sys.argv[1:])
