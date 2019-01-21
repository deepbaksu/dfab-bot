import os
import sys
import logging
from logging.handlers import RotatingFileHandler


def logging_file_config(log_filename,
                        log_level=logging.INFO,
                        log_max_size=(5* 1024 * 1024),
                        log_backup_count=5,
                        showlog=True):
    # create log folder
    logfile_fullpath = os.path.abspath(log_filename)
    logdir_fullpath = os.path.dirname(logfile_fullpath)
    if os.path.exists(logdir_fullpath) is False:
        os.makedirs(logdir_fullpath)

    log_handlers = []
    if showlog:
        # add stdout handler
        log_handlers.append(logging.StreamHandler(sys.stdout))

    # add log file handler
    log_handlers.append(RotatingFileHandler(logfile_fullpath,
                                            maxBytes=log_max_size,
                                            backupCount=log_backup_count))

    logging.basicConfig(level=log_level,
                        format='%(asctime)s:%(processName)s[%(process)d],%(threadName)s:%(module)s[%(lineno)s]:%(levelname)s:%(message)s',
                        handlers=log_handlers)
