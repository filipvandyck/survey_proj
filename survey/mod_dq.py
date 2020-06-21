#!/usr/bin/env python3
#
#check pr for dataquality
#
#
# mod_dq.py
import myoutput as out
import os
import pandas as pd

import mod_import_pr as imp


TEST_IFH = os.path.dirname(os.path.realpath(__file__)) + '/dq/exports/import_pr_ifh.csv'
TEST_PR = os.path.dirname(os.path.realpath(__file__)) + '/dq/pr/pr_export.xlsx'


TEST_OUTPUT = os.path.dirname(os.path.realpath(__file__)) + '/dq/diff.csv'

pd.set_option('mode.chained_assignment', None)

f = TEST_IFH
f_pr = TEST_PR

def make_diff_pr_ifh(f,f_pr):

    survey = imp.make_survey_import(f, imp.OUTPUTFOLDER, imp.INPUT_STREET_FILE, imp.INPUT_CITY_FILE)
   # survey = imp.make_survey_import(f, '', imp.INPUT_STREET_FILE, imp.INPUT_CITY_FILE)


    #survey = pd.read_csv(f, delimiter=';',encoding = "ISO-8859-1", keep_default_na=False,dtype={'LAM MK': object,'TOTAAL': object})
    survey.columns = survey.columns.str.replace(' ','_')
    survey = survey.drop_duplicates(subset='LAM_MK', keep='first')
    pr = pd.read_excel(f_pr,  keep_default_na=False,dtype={'Opdrachtnummer': object, 'UNITS TOTAL': object})
    pr.columns = pr.columns.str.replace(' ','_')
    
    survey = survey.astype(str)


    out.menu_header("check pr for data quality")

    #blocks

    pr['errors'] = 'NA'

    df_blok = pr[pr['Blok']=='']
    df_blok['errors'] = 'MISSING BLOK'




    #clusters

    df_cluster = pr[pr['Cluster_NR']=='']
    df_cluster['errors'] = 'MISSING CLUSTER'






    #building fid

    df_buildingfid = pr[pr['Building_FID']=='']
    df_buildingfid['errors'] = 'MISSING BUILDING FID'




    #building groups
    pr['test_BG_Name'] = pr['Opdrachtnummer'] + '_' + pr['BG_Name']
    survey['test_BG_Name'] = survey['LAM_MK'] + '_' + survey['BG_Name']
    df_bg_1 = pr[~pr['test_BG_Name'].isin(survey['test_BG_Name'])]
    df_bg_1['errors'] = 'BG Name diff'

    df_bg = pd.merge(df_bg_1, survey, how='left', left_on='Opdrachtnummer', right_on='LAM_MK',suffixes=('', '_IFH'))


    #mdu/sdu

    pr['test_BT'] = pr['Opdrachtnummer'] + '_' + pr['Buildingtype']
    survey['test_BT'] = survey['LAM_MK'] + '_' +  survey['BT']
    df_bt = pr[~pr['test_BT'].isin(survey['test_BT'])]
    df_bt['errors'] = 'Buildingtype diff'

    #units total

    pr['test_Units_total'] = pr['Opdrachtnummer'] + '_' + pr['UNITS_TOTAL']
    survey['test_Units_total'] = survey['LAM_MK'] + '_' + survey['TOTAAL']
    df_units_total = pr[~pr['test_Units_total'].isin(survey['test_Units_total'])]
    df_units_total['errors'] = 'Units total diff'


    df_units_total = pd.merge(df_units_total, survey, how='left', left_on='Opdrachtnummer', right_on='LAM_MK',suffixes=('', '_IFH'))

    #print(df_units_total)


    #units total
    df_dif=pd.concat([df_cluster, df_blok,df_buildingfid,df_bg,df_bt,df_units_total], join='outer', axis=0)
    df_dif=df_dif.sort_values(by=['Opdrachtnummer'])

    out.print_df(df_dif)

    df_dif=df_dif[['Projectnummer','errors','Opdrachtnummer','Blok','Cluster_NR','Building_FID','LAM_MK','BG_Id','BG_Name','BG_Name_IFH','Straat','Huisnummer','Huisnummer_Toevoeging','Quadrant','SSV_Date','Surveyor','Buildingtype','NR_BU','NR_LU','NR_SU','UNITS_TOTAL','LU','BU','SU','TOTAAL','Opdrachttemplate']]


    filename = TEST_OUTPUT
    csv = df_dif.to_csv(filename,sep=';',index=False)
    out.info_file('diff csv written',filename)


#make_diff_pr_ifh(f,f_pr)
