#!/usr/bin/env python3
#
# mod_sns.py


import glob
import os, shutil
import mod_import_pr as import_pr
import pandas as pd
import datetime
import numpy as np

import myoutput as out

SNSFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/documents/SNS/' 




SNS_FILE = SNSFOLDER + 'SNS_report_v4.xlsx' 
EXPORT_FILE_PR = SNSFOLDER + 'export.csv' 

def make_sns_report():
    out.menu_header('SNS REPORT')

    out.info_file("Reading Planrrr data", EXPORT_FILE_PR)
    df_pr = pd.read_csv(EXPORT_FILE_PR, delimiter=',', encoding = "ISO-8859-1", keep_default_na=False,dtype={'Opdrachtnummer': object, 'UNITS TOTAL': object})
    df_pr.columns = df_pr.columns.str.replace(' ','_')
    df_pr['UNITS_TOTAL'] = pd.to_numeric(df_pr['UNITS_TOTAL'],errors='coerce')

    out.info_file("Reading SNS data", SNS_FILE)
    xls = pd.ExcelFile(SNS_FILE)
    df_sns = pd.read_excel(xls, 'Data',dtype={'MAINLAMKEY': object})

    df_report = pd.merge(df_sns, df_pr, how='left', left_on='MAINLAMKEY', right_on='Opdrachtnummer',suffixes=('', '_PR'))



    table_fis = pd.pivot_table(df_report,values='FIS',index='ZONE_NAME',columns='Buildingtype',aggfunc=np.sum)
    table_fis_needed = pd.pivot_table(df_report,values='FIS',index='ZONE_NAME',columns='Buildingtype',aggfunc=np.size)



    table_report = pd.merge(table_fis, table_fis_needed, how='left', left_on='ZONE_NAME', right_on='ZONE_NAME',suffixes=('', '_TOTAL'))


    table_report['MDU'] = pd.to_numeric(table_report['MDU'],errors='coerce')
    table_report['MDU_TOTAL'] = pd.to_numeric(table_report['MDU_TOTAL'],errors='coerce')
    table_report['SDU_TOTAL'] = pd.to_numeric(table_report['SDU_TOTAL'],errors='coerce')
    table_report['BUILDINGS_TOTAL'] = table_report['MDU_TOTAL'] + table_report['SDU_TOTAL']
    table_report['FIS_PROCENT'] = table_report['MDU'] / table_report['MDU_TOTAL'] * 100



    table_fts = pd.pivot_table(df_report,values='FTS',index='ZONE_NAME',columns='Quadrant',aggfunc=np.sum)
    table_fts_needed = pd.pivot_table(df_report,values='FTS',index='ZONE_NAME',columns='Quadrant',aggfunc=np.size)

    table_fts = table_fts.fillna(0)
    table_fts_needed = table_fts_needed.fillna(0)
    table_report_fts_count = table_fts['A'] + table_fts['XA'] + table_fts['XC'] + table_fts['C'] + table_fts['B'] + table_fts['E']
    table_report_fts_needed = table_fts_needed['A'] + table_fts_needed['XA'] + table_fts_needed['XC'] + table_fts_needed['C'] + table_fts_needed['B'] + table_fts_needed['E']

    table_report_fts = pd.DataFrame(columns = ['FTS', 'FTS_TOTAL'])
    table_report_fts['FTS'] = table_report_fts_count
    table_report_fts['FTS_TOTAL'] = table_report_fts_needed 
    table_report_fts['FTS_PROCENT'] = table_report_fts['FTS'] / table_report_fts['FTS_TOTAL'] * 100

    table_units = pd.pivot_table(df_report,values='UNITS_TOTAL',index='ZONE_NAME',aggfunc=np.sum)

    df_pr_quadrants = df_report[df_report['Quadrant']!='']
    table_quadrants = pd.pivot_table(df_pr_quadrants,values='Quadrant',index='ZONE_NAME',columns='Buildingtype',aggfunc=np.size)



    table_report = pd.merge(table_report, table_units, how='left', left_on='ZONE_NAME', right_on='ZONE_NAME',suffixes=('', '_TOTAL'))
    table_report = pd.merge(table_report, table_report_fts, how='left', left_on='ZONE_NAME', right_on='ZONE_NAME',suffixes=('', '_TOTAL'))
    table_report = pd.merge(table_report, table_quadrants, how='left', left_on='ZONE_NAME', right_on='ZONE_NAME',suffixes=('', '_SSV'))

    table_report['SSV_PROCENT'] = table_report['MDU_SSV'] / table_report['MDU_TOTAL'] * 100


    table_report = table_report.rename(columns={"MDU": "FIS_MDU", "SDU": "FIS_SDU"})

    filename = SNSFOLDER + 'report.csv'
    out.info_file("Writing report file", filename)
    
    table_report = table_report[['FIS_MDU','FIS_SDU','MDU_TOTAL','SDU_TOTAL','BUILDINGS_TOTAL','FIS_PROCENT','UNITS_TOTAL','FTS','FTS_TOTAL','FTS_PROCENT','MDU_SSV','SDU_SSV','SSV_PROCENT']]


    csv = table_report.to_csv(filename, sep=';')

    out.info_file("Report data", table_report)



