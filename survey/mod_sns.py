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
import mod_sns_chart as chart


SNSFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/documents/SNS/' 
EXPORTFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/selenium/download/backup/' 




SNS_FILE           = SNSFOLDER + 'SNS_report_v4.xlsx' 
EXPORT_FILE_PR     = EXPORTFOLDER + 'export_back.csv' 

REPORT_FIS_SDU     = SNSFOLDER + 'report_fis_sdu.csv'
REPORT_FIS_MISSING = SNSFOLDER + 'report_fis_mdu_missing.csv'
REPORT             = SNSFOLDER + 'report.csv'


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


    df_report_sts_done = df_report[df_report['Surveyor']!='']
    table_sts_done = pd.pivot_table(df_report_sts_done,values='Surveyor',index='ZONE_NAME',aggfunc=np.size)


    table_fis = pd.pivot_table(df_report,values='FIS',index='ZONE_NAME',columns='Buildingtype',aggfunc=np.sum)
    table_fis_needed = pd.pivot_table(df_report,values='FIS',index='ZONE_NAME',columns='Buildingtype',aggfunc=np.size)


    #report sdu with fis 
    df_fis = df_report[df_report['FIS']==1]     
    df_fis_sdu = df_fis[df_fis['Buildingtype']=='SDU'] 
    #;ZONE_NAME;ZONING_TCHNLGY;MAINLAMKEY;POSTAL_CODE;CITY_NAME;STREET_NAME;HOUSE_NUMBER;DTP;FIC;FIS;FTS;OpdrachtID;Projectnummer;Opdrachtnummer;BG_Name;Blok;Straat;Huisnummer;Huisnummer_Toevoeging;Buildingtype;Quadrant;NR_BU;NR_LU;NR_SU;UNITS_TOTAL;Surveyor;Opdrachttemplate
    
    df_fis_sdu = df_fis_sdu[['ZONE_NAME','MAINLAMKEY','CITY_NAME','DTP','FIC','FIS','FTS','Projectnummer','BG_Name','Blok','Straat','Huisnummer','Huisnummer_Toevoeging','Quadrant']]

    out.info_file("Writing report SDU FIS file", REPORT_FIS_SDU)
    csv = df_fis_sdu.to_csv(REPORT_FIS_SDU, sep=';')

    


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
    table_report = pd.merge(table_report, table_sts_done, how='left', left_on='ZONE_NAME', right_on='ZONE_NAME',suffixes=('', '_STS'))

    table_report['SSV_PROCENT'] = table_report['MDU_SSV'] / table_report['MDU_TOTAL'] * 100
    table_report['STS_PROCENT'] = table_report['Surveyor'] / (table_report['MDU_TOTAL'] + table_report['SDU_TOTAL']) * 100
    table_report['STS_TODO'] = (table_report['MDU_TOTAL'] + table_report['SDU_TOTAL']) - table_report['Surveyor'] 
    table_report['SSV_TODO'] = table_report['MDU_TOTAL'] - table_report['MDU_SSV'] 

    #report mdu with missing fis 
    df_fis_missing = df_report[df_report['FIS']!=1]
    df_fis_missing = df_fis_missing[df_fis_missing['Buildingtype']=='MDU']
    
    
    df_fis_missing = pd.merge(df_fis_missing, table_report, how='left', left_on='ZONE_NAME', right_on='ZONE_NAME',suffixes=('', '_REPORT'))
    
    df_fis_missing = df_fis_missing[df_fis_missing['FIS_PROCENT']>0]
    df_fis_missing = df_fis_missing[['ZONE_NAME','MAINLAMKEY','CITY_NAME','DTP','FIC','FIS','FTS','Projectnummer','BG_Name','Blok','Straat','Huisnummer','Huisnummer_Toevoeging','Quadrant']]
    

    out.info_file("Writing report MDU with missing FIS file", REPORT_FIS_MISSING)
    csv = df_fis_missing.to_csv(REPORT_FIS_MISSING, sep=';')


    table_report = table_report.rename(columns={"MDU": "FIS_MDU", "SDU": "FIS_SDU", "Surveyor": "STS"})

    print(table_report)


    out.info_file("Writing report file", REPORT)
    
    #table_report = table_report[['FIS_MDU','FIS_SDU','MDU_TOTAL','SDU_TOTAL','BUILDINGS_TOTAL','FIS_PROCENT','UNITS_TOTAL','FTS','FTS_TOTAL','FTS_PROCENT','MDU_SSV','SDU_SSV','SSV_PROCENT']]
    table_report = table_report[['FIS_MDU','FIS_SDU','MDU_TOTAL','SDU_TOTAL','BUILDINGS_TOTAL','FIS_PROCENT','UNITS_TOTAL','FTS','FTS_TOTAL','FTS_PROCENT','MDU_SSV','SSV_PROCENT','STS','STS_PROCENT','STS_TODO','SSV_TODO']]
    table_report = table_report.fillna(0)
    table_report['BUILDINGS_TOTAL'] = table_report['BUILDINGS_TOTAL'].astype(int)
    table_report['MDU_TOTAL'] = table_report['MDU_TOTAL'].astype(int)
    table_report['SDU_TOTAL'] = table_report['SDU_TOTAL'].astype(int)
    table_report['FIS_MDU'] = table_report['FIS_MDU'].astype(int)
    table_report['FIS_SDU'] = table_report['FIS_SDU'].astype(int)
    table_report['FIS_PROCENT'] = table_report['FIS_PROCENT'].round(2)
    table_report['FTS_PROCENT'] = table_report['FTS_PROCENT'].round(2)
    table_report['SSV_PROCENT'] = table_report['SSV_PROCENT'].round(2)
    table_report['STS_PROCENT'] = table_report['STS_PROCENT'].round(2)
    table_report['UNITS_TOTAL'] = table_report['UNITS_TOTAL'].astype(int)

    table_report['FTS'] = table_report['FTS'].astype(int)
    table_report['FTS_TOTAL'] = table_report['FTS_TOTAL'].astype(int)
    table_report['MDU_SSV'] = table_report['MDU_SSV'].astype(int)
    table_report['STS'] = table_report['STS'].astype(int)
    table_report['STS_TODO'] = table_report['STS_TODO'].astype(int)
    table_report['SSV_TODO'] = table_report['SSV_TODO'].astype(int)


    csv = table_report.to_csv(REPORT, sep=';')

    out.info_file("Report data", table_report)


    chart.make_site()

#make_sns_report()
