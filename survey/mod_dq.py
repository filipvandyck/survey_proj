#!/usr/bin/env python3
#
#check pr for dataquality
#
#
# mod_dq.py

ENCODING = 'utf8'

import myoutput as out
import os
import pandas as pd
import numpy as np

import mod_import_pr_fr as imp_fr

import datetime




TEST_IFH = os.path.dirname(os.path.realpath(__file__)) + '/dq/exports/import_pr_ifh.csv'
TEST_PR = os.path.dirname(os.path.realpath(__file__)) + '/dq/pr/pr_export.xlsx'

DIF_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/dq/output/'
TEST_OUTPUT = DIF_FOLDER + 'diff.csv'

pd.set_option('mode.chained_assignment', None)

f = TEST_IFH
f_pr = TEST_PR

def make_diff_pr_ifh(f,f_pr):
    global ENCODING

    survey = imp_fr.make_survey_import(f, imp_fr.OUTPUTFOLDER, imp_fr.INPUT_STREET_FILE_FR, imp_fr.INPUT_CITY_FILE_FR)
   # survey = imp.make_survey_import(f, '', imp.INPUT_STREET_FILE, imp.INPUT_CITY_FILE)


    #survey = pd.read_csv(f, delimiter=';',encoding = "ISO-8859-1", keep_default_na=False,dtype={'LAM MK': object,'TOTAAL': object})
    survey.columns = survey.columns.str.replace(' ','_')
    survey = survey.drop_duplicates(subset='LAM_MK', keep='first')
    pr = pd.read_excel(f_pr,  keep_default_na=False,dtype={'Opdrachtnummer': object, 'NR BU': object, 'NR LU': object, 'NR SU': object, 'UNITS TOTAL': object} , encoding = ENCODING )
    pr.columns = pr.columns.str.replace(' ','_')
    
    survey = survey.astype(str)




    out.menu_header("check pr for data quality")

    #blocks

    pr['errors'] = 'NA'

    rows = pr.shape[0]

    df_blok = pr[pr['Blok']=='']
    df_blok['errors'] = 'MISSING BLOK'
    if df_blok.shape[0] == rows:
        print('All blocks missing')
        df_blok['errors'] = 'NO BLOCKS'
    

    #clusters

    df_cluster = pr[pr['Cluster_NR']=='']
    df_cluster['errors'] = 'MISSING CLUSTER'

    if df_cluster.shape[0] == rows: 
        print('All clusters missing')
        df_cluster['errors'] = 'NO CLUSTERS'





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
   
    #units bu

    pr['test_Units_BU'] = pr['Opdrachtnummer'] + '_' + pr['NR_BU']
    survey['test_BU'] = survey['LAM_MK'] + '_' + survey['BU']
    df_bu = pr[~pr['test_Units_BU'].isin(survey['test_BU'])]
    df_bu['errors'] = 'Units bu diff'


    df_bu = pd.merge(df_bu, survey, how='left', left_on='Opdrachtnummer', right_on='LAM_MK',suffixes=('', '_IFH'))

    #units lu

    pr['test_Units_LU'] = pr['Opdrachtnummer'] + '_' + pr['NR_LU']
    survey['test_LU'] = survey['LAM_MK'] + '_' + survey['LU']
    df_lu = pr[~pr['test_Units_LU'].isin(survey['test_LU'])]
    df_lu['errors'] = 'Units lu diff'


    df_lu = pd.merge(df_lu, survey, how='left', left_on='Opdrachtnummer', right_on='LAM_MK',suffixes=('', '_IFH'))

    #units su

    pr['test_Units_SU'] = pr['Opdrachtnummer'] + '_' + pr['NR_SU']
    survey['test_SU'] = survey['LAM_MK'] + '_' + survey['SU']
    df_su = pr[~pr['test_Units_SU'].isin(survey['test_SU'])]
    df_su['errors'] = 'Units su diff'


    df_su = pd.merge(df_su, survey, how='left', left_on='Opdrachtnummer', right_on='LAM_MK',suffixes=('', '_IFH'))

    #quadrant
    survey['Q_IFH'] = survey['VC_Method'].str[:1]

    pr['test_Q'] = pr['Quadrant'].str.replace('XC','C')
    pr['test_Q'] = pr['test_Q'].str.replace('XA','A')



    pr['test_Q'] = pr['Opdrachtnummer'] + '_' + pr['test_Q']
    survey['test_Q'] = survey['LAM_MK'] + '_' + survey['Q_IFH']
    df_q = pr[~pr['test_Q'].isin(survey['test_Q'])]
    df_q['errors'] = 'Quadrant diff'


    df_q = pd.merge(df_q, survey, how='left', left_on='Opdrachtnummer', right_on='LAM_MK',suffixes=('', '_IFH'))

    #wall mount

    pr['test_WM'] = pr['Opdrachtnummer'] + '_' + pr['Wall_Mount']
    survey['WM'] = survey['LAM_MK'] + '_' + survey['Wall_Mount']
    df_WM = pr[~pr['test_WM'].isin(survey['WM'])]
    df_WM['errors'] = 'Wall Mount diff'


    df_WM = pd.merge(df_WM, survey, how='left', left_on='Opdrachtnummer', right_on='LAM_MK',suffixes=('', '_IFH'))



    #missing building in IFH

    df_LAM = pr[~pr['Opdrachtnummer'].isin(survey['LAM_MK'])]
    df_LAM['errors'] = 'Building Missing in IFH'
    print('missing building IFH')
    print(df_LAM)
  #  df_LAM = pd.merge(df_LAM, survey, how='left', left_on='Opdrachtnummer', right_on='LAM_MK',suffixes=('', '_IFH'))

    #missing building in PR

    df_Opdrachtnummer = survey[~survey['LAM_MK'].isin(pr['Opdrachtnummer'])]
    df_Opdrachtnummer['errors'] = 'Building Missing in PR'
    df_Opdrachtnummer['Straat'] = survey['Street']
    df_Opdrachtnummer['Huisnummer'] = survey['Nr']

    print('missing building PR')
    print(df_Opdrachtnummer)

    # blok diff in bg

    df_dif=pd.concat([df_cluster, df_blok,df_buildingfid,df_bg,df_bt,df_units_total,df_bu,df_lu,df_su,df_q,df_WM,df_LAM,df_Opdrachtnummer], join='outer', axis=0)


    if df_blok.shape[0] != rows: 
        table_bg_blok = pd.pivot_table(pr,index='BG_Name',values='Blok',aggfunc=lambda x: len(x.unique()))
        df_bg_blok = table_bg_blok[table_bg_blok['Blok']>1] 
        df_bg_blok['BG_Name_test'] = df_bg_blok.index
        df_bg_blok = df_bg_blok[df_bg_blok['BG_Name_test']!=''] 

        df_bg_blok = df_bg_blok.rename(columns={"Blok": "blok_diff"})



        df_bg_blok = pd.merge(df_bg_blok, pr, how='inner', left_on='BG_Name', right_on='BG_Name',suffixes=('', '_PR'))
        df_bg_blok['errors'] = 'BG Blok diff'
        print('BG Blok')
        print(df_bg_blok)


        df_dif=pd.concat([df_dif, df_bg_blok], join='outer', axis=0)

    
        
    # cluster diff in bg

    if df_cluster.shape[0] != rows: 
        table_bg_cluster = pd.pivot_table(pr,index='BG_Name',values='Cluster_NR',aggfunc=lambda x: len(x.unique()))
        df_bg_cluster = table_bg_cluster[table_bg_cluster['Cluster_NR']>1] 
        df_bg_cluster['BG_Name_test'] = df_bg_cluster.index
        df_bg_cluster = df_bg_cluster[df_bg_cluster['BG_Name_test']!=''] 

        df_bg_cluster = df_bg_cluster.rename(columns={"Cluster_NR": "cluster_diff"})
        print("df cluster")
        print(df_bg_cluster)
        if df_bg_cluster.empty == False:
            df_bg_cluster = pd.merge(df_bg_cluster, pr, how='inner', left_on='BG_Name', right_on='BG_Name',suffixes=('', '_PR'))
            df_bg_cluster['errors'] = 'BG Cluster diff'
            print('BG Cluster')
            print(df_bg_cluster)

        df_dif=pd.concat([df_dif, df_bg_cluster], join='outer', axis=0)


   

    df_dif=df_dif.sort_values(by=['Opdrachtnummer'])

    out.print_df(df_dif)



    df_dif=df_dif[['Projectnummer','errors','Opdrachtnummer','Blok','Cluster_NR','Building_FID','LAM_MK','BG_Id','BG_Name','BG_Name_IFH','Straat','Huisnummer','Huisnummer_Toevoeging','Quadrant','Q_IFH', 'SSV_Date','Surveyor','Buildingtype','NR_BU','NR_LU','NR_SU','UNITS_TOTAL','BU','LU','SU','TOTAAL','Wall_Mount','Wall_Mount_IFH','Opdrachttemplate']]


    df_dif.columns = df_dif.columns.str.replace('_',' ')
    df_dif = df_dif.rename(columns={"BU": "IFH_BU", "LU": "IFH_LU","SU": "IFH_SU","TOTAAL": "IFH_TOTAAL"})


    df_dif['LAM MK'] = df_dif['LAM MK'].astype(int, errors = 'ignore')
    df_dif['Building FID'] = df_dif['Building FID'].astype(int, errors = 'ignore')
    df_dif['Huisnummer'] = df_dif['Huisnummer'].astype(int, errors = 'ignore')
 #   df_dif['Cluster'] = df_dif['Cluster'].astype(int, errors = 'ignore')

    if df_dif['Projectnummer'].count() > 0 :    

        project = df_dif['Projectnummer'].iloc[0]
        datum = datetime.datetime.now().strftime("%Y%m%d%H%M")



        filename = DIF_FOLDER + 'diff_' + project + '_' + datum 
        csv = df_dif.to_csv(filename + '.csv',sep=';',index=False, encoding = ENCODING)
        out.info_file('diff csv written',filename)

        df_dif.to_excel (filename + '.xlsx', index = False, header=True, encoding = ENCODING)
        out.info_file('diff xlsx written',filename)
    else :
        out.info_file ('ifh and PR in sync', df_dif)

    
    



   
#make_diff_pr_ifh(f,f_pr)
