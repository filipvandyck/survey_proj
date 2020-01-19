#!/usr/bin/env python3
#
# mod_stats.py


import glob
import os, shutil
import mod_import_pr as import_pr
import pandas as pd
import datetime

import myoutput as out

STATSFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/stats/' 
EXPORTFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/stats/export/' 





def writecsvcorrection(df,df_ifh,importnaam):
    f_begin = df_ifh['Area Name'][0] + '-'

    d = datetime.date.today()
    f_end = '-' + str(d.year) + '%02d' % d.month + '%02d' % d.day + '.csv'

    filename = CORRECTIONSFOLDER + f_begin + importnaam + f_end

    csv = df.to_csv(filename,sep=';',index=False)
    out.info_file('import csv written',filename)



def getcsvfile(directory):
     files = [f for f in glob.glob(directory + "*.csv")]
     if len(files) > 0 :
         return(files[0])
     else:
         print('no csv file found in: ' + directory)
         return(0)

def get_sts_stats(exportfile):
    out.info_file('Processing for stats',exportfile)




    df = pd.read_csv(exportfile, delimiter=',', encoding = "ISO-8859-1", keep_default_na=False)

    df = df.applymap(str)
    df = df.astype({"UNITS TOTAL": int})



    df['STS_COMPLETED'] = df['STS COMPLETED DATE'] + df['SSV Date'] + df['Building exists']
    df.loc[(df.STS_COMPLETED != ''),'STS_COMPLETED']='Y'

    df_completed = df[df['STS_COMPLETED']!=''] 
    df_todo = df[df['STS_COMPLETED']==''] 
    df_deleted = df[df['Building exists']=='N'] 
    

    
    STS_COMPLETED = df_completed['STS_COMPLETED'].count()
    STS_TODO =  df_todo['STS_COMPLETED'].count()
    STS_TOTAL = df['STS_COMPLETED'].count()

    STS_PROCENT_DONE = int((STS_COMPLETED / STS_TOTAL) * 100)

    

    STS_SURVEYED_UNITS = df_completed['UNITS TOTAL'].sum() - df_deleted['UNITS TOTAL'].sum() 
    STS_UNITS_TO_SURVEY = df_todo['UNITS TOTAL'].sum()
    STS_UNITS_TOTAL = STS_SURVEYED_UNITS + STS_UNITS_TO_SURVEY
    
    STS_PROCENT_UNITS_DONE = int((STS_SURVEYED_UNITS / STS_UNITS_TOTAL) * 100)



    out.info_file('STS TOTAL', STS_TOTAL)
    out.info_file('STS COMPLETED', STS_COMPLETED)
    out.info_file('STS TODO', STS_TODO)
    out.info_file('STS PROCENT BUIDINGS DONE', str(STS_PROCENT_DONE) + '%')


    out.info_file('STS SURVEYED UNITS', STS_SURVEYED_UNITS)
    out.info_file('STS UNITS TO SURVEY', STS_UNITS_TO_SURVEY)
    out.info_file('STS PROCENT UNITS DONE', str(STS_PROCENT_UNITS_DONE) + '%')


f = getcsvfile(EXPORTFOLDER)
get_sts_stats(f)
