#!/usr/bin/env python3
#
# mod_.planning_tsa.py

import glob
import os, shutil
import pandas as pd
import datetime
import numpy as np

import myoutput as out

EXPORTFOLDER     = os.path.dirname(os.path.realpath(__file__)) + '/selenium/download/backup/' 
FOLDER_PLANNING  = os.path.dirname(os.path.realpath(__file__)) + '/documents/planningsfiles/'
FILE_PLANNING    = FOLDER_PLANNING + 'planningsfiles.csv'
EXPORT_FILE_PR   = EXPORTFOLDER + 'export_back.csv'
FOLDER_IMPORT_PR = FOLDER_PLANNING + 'tsa_import_pr/'

TAB = 'SURVEYOR'
COLUMN_TSA_SIGNED = 'Datum TSA Getekend'
COLUMN_LAMKEY = 'Opdrachtnummer'



def make_tsa_projectindex(project,file_planning):

    out.info_file("Reading Planrrr data", EXPORT_FILE_PR)
    df_pr = pd.read_csv(EXPORT_FILE_PR, delimiter=',', encoding = "ISO-8859-1", parse_dates=['TSA SIGNED'],keep_default_na=False,dtype={'Opdrachtnummer': str})
    df_pr.columns = df_pr.columns.str.replace(' ','_')


    pl_file    = file_planning
    pl_project = project

    out.info_file("Planningsfile",pl_file)
    xls = pd.ExcelFile(pl_file)
    df_pl = pd.read_excel(xls, TAB ,header=2, dtype={'Opdrachtnummer': str, 'BG Name': str })
    df_pl.columns = df_pl.columns.str.replace(' ','_')

    df_pl.rename(columns = {'BG_Key':'BG_KEY'}, inplace = True) 
    

    df_pr_project=df_pr[df_pr['Projectnummer']==pl_project]

   # df_pl['BG_KEY'] = df_pl.apply(
   #     lambda row: row['Opdrachtnummer'] if pd.isnull(row['BG_Name']) else row['BG_Name'],
   #     axis=1
   # )
    df_pr_project['BG_KEY'] = df_pr_project.apply(
        lambda row: row['Opdrachtnummer'] if (row['BG_Name']=='') else row['BG_Name'],
        axis=1
    )

    print(df_pl.columns)
    
    df_pl['VCA'] = df_pl['Datum_TSA_Definitief_Geweigerd'].astype(object)
    df_pl['VCA'] = np.where(pd.isna(df_pl['VCA'])==False, 'NOK', '')
    
    
    df_pr_project_signed = df_pr_project[(df_pr_project['TSA_SIGNED']>pd.to_datetime('1900-1-1'))|(df_pr_project['VCA_Status']=='NOK')]
    df_pr_project_signed = df_pr_project_signed.drop_duplicates(subset=['BG_KEY'])

    print('TSA signed in Planrrr:')
    print(df_pr_project_signed['BG_KEY'].count())

    df_pl_signed = df_pl[(df_pl['Datum_TSA_Getekend']>pd.to_datetime('1900-1-1'))|(df_pl['VCA']=='NOK')] 
    df_pl_signed = df_pl_signed.drop_duplicates(subset=['BG_KEY'])
    print('TSA signed in Planning:')
    print(df_pl_signed['BG_KEY'].count())



    df_pl_pr = df_pr_project_signed.merge(df_pl_signed, how='outer', left_on='BG_KEY', right_on='BG_KEY',suffixes=('', '_PL'))

    df_pl_pr['TSA_DELTA'] = np.where((df_pl_pr['TSA_SIGNED']!=df_pl_pr['Datum_TSA_Getekend'])|(df_pl_pr['VCA']!=df_pl_pr['VCA_Status']), 'yes', 'no')
    df_pl_pr_delta=df_pl_pr[df_pl_pr['TSA_DELTA']=='yes']



#    print(df_pl['VCA'])

    df_pl_pr_delta_full = df_pr_project.merge(df_pl_pr_delta, how='right', left_on='BG_KEY', right_on='BG_KEY',suffixes=('_PR', ''))



    df_pl_pr_delta = df_pl_pr_delta_full.rename(columns={"Opdrachtnummer_PR": "BUILDING KEY", "TSA_SIGNED": "TSA SIGNED Planrrr", "Datum_TSA_Getekend": "TSA SIGNED", "VCA" : "VCA Status", "VCA_Status" : "VCA Planrrr"})

        
    df_pl_pr_delta = df_pl_pr_delta[['BUILDING KEY','BG_KEY','Straat','Huisnummer','Huisnummer_Toevoeging','Quadrant','TSA SIGNED', 'TSA SIGNED Planrrr', 'VCA Status', 'VCA Planrrr']]



    df_pl_pr_delta['TSA SIGNED'] = pd.to_datetime(df_pl_pr_delta['TSA SIGNED'], format='%Y-%m-%d')


    csv = df_pl_pr_delta.to_csv(FOLDER_IMPORT_PR + 'tsa_'+ pl_project +'.csv', sep=';', index=False, date_format='%Y-%m-%d')
    out.info_file("tsa data", df_pl_pr_delta)


out.info_file("Reading Planning data", FILE_PLANNING)
df_planning = pd.read_csv(FILE_PLANNING, delimiter=';', encoding = "ISO-8859-1")


for index,row in df_planning.iterrows():
    print(index, '\t', row['projectnummer'])

index = input("Enter projectnumber:]")

project       = df_planning.loc[int(index),'projectnummer']
file_planning = df_planning.loc[int(index),'file']

make_tsa_projectindex(project,file_planning)



