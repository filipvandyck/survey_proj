#!/usr/bin/env python3
#
# mod_backup.py

import os
import time
import shutil

REPORT_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/documents/SNS/'
BACKUP_REPORT_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/documents/SNS/reports/'


REPORT_FILE = REPORT_FOLDER + 'report.csv'


def make_backup_report():

    modificationDate = time.strftime('%Y%m%d', time.localtime(os.path.getmtime(REPORT_FILE)))
    print("The report: ", REPORT_FILE )
    print("Last Modified date : ", modificationDate )


    report_file_backup = BACKUP_REPORT_FOLDER + 'report_' + modificationDate + '.csv'

    print("Backup written : ", report_file_backup )


    shutil.copy2(REPORT_FILE, report_file_backup)


#make_backup_report()
