#!/usr/bin/env python3
#
#Make GCT upload from power_bi data (b1 en b2)
#based on rft yes and no
#
# mod_frost.py
import myoutput as out
import os
import pandas as pd
import numpy as np

import mod_import_pr as imp

from datetime import datetime
from time import strftime

FOLDER_FROST     = os.path.dirname(os.path.realpath(__file__)) + '/frost/'
TEST_POWER_BI    = os.path.dirname(os.path.realpath(__file__)) + '/frost/power_bi/data.xlsx'
TEST_PR          = os.path.dirname(os.path.realpath(__file__)) + '/frost/power_bi/area.xlsx'

EXPORTFOLDER     = os.path.dirname(os.path.realpath(__file__)) + '/selenium/download/backup/'
EXPORT_FILE_PR   = EXPORTFOLDER + 'export_back.csv'

TEST_OUTPUT      = os.path.dirname(os.path.realpath(__file__)) + '/frost/gct.csv'

pd.set_option('mode.chained_assignment', None)

f = TEST_POWER_BI
f_pr = TEST_PR


def make_gct():
   
    
    
    
    areas = pd.read_excel(f_pr,  keep_default_na=False)
    areas.columns = areas.columns.str.replace(' ','_')

    pbi = pd.read_excel(f,  keep_default_na=False, skiprows=range(0,2),header=0)
    pbi.columns = pbi.columns.str.replace(' ','_')
    pbi.columns = pbi.columns.str.replace('[','')
    pbi.columns = pbi.columns.str.replace(']','')
    pbi.columns = pbi.columns.str.replace("'",'')


    pbi = pbi.rename(columns={"Building_Unitsmainkey": "Lamkey"})
    
    pbi['Lamkey'] = pbi['Lamkey'].astype('str') 
    pbi['Lu_Key'] = pbi['Lu_Key'].astype('str') 
   

    pbi_rft_yes = pbi[pbi['RFT']=='Yes']
    pbi_rft_no  = pbi[pbi['RFT']=='No']

    pbi_rft_yes_future = pbi_rft_yes[pbi_rft_yes['B2']>pd.to_datetime('today')]


    pbi_rft_yes_future['B2_new'] = pd.to_datetime('today')

    pbi_rft_no_past = pbi_rft_no[pbi_rft_no['B2']<(pd.to_datetime('today')+pd.DateOffset(days=20))]


    handover_date = pbi['Handover_Date'][1]



    #check if handover between now in 2 months in Powerbi
    #if shorter the we take now + 6 months

    dif = handover_date - pd.to_datetime('today')

    b2_future = pd.to_datetime('today')+pd.DateOffset(months=6)

    if dif >  pd.Timedelta(days=60):
        b2_future = handover_date


    pbi_rft_no_past['B2_new'] = b2_future

    # empty b1 b2

    pbi_b2_no = pbi[pd.isnull(pd.to_datetime(pbi.B2))]


    pbi_b2_no['B1'] = pd.to_datetime('today')
    pbi_b2_no['B2_new'] = b2_future

    pbi_rft_to_do = pd.concat([pbi_rft_yes_future, pbi_rft_no_past,pbi_b2_no], join="inner")
    
    
    
    area = pbi['Block_Name'][1]
    area = area.split('_')[0]
    area_upper = area.upper()
  
    areas = areas[areas['Zoning_Name']==area]
    print(areas)    
    zoning_fid = areas['Zoning_FID'].iloc[0]
    zoning_id = areas['Zoning_ID'].iloc[0]
    projectnummer = areas['Projectnummer'].iloc[0]
#    print(zoning_fid)
#    print(zoning_id)


    #get VCA from export pr

    print(projectnummer)

    out.info_file("Reading Planrrr data", EXPORT_FILE_PR)
    df_pr = pd.read_csv(EXPORT_FILE_PR, delimiter=',', encoding = "ISO-8859-1", parse_dates=['TSA SIGNED'],keep_default_na=False,dtype={'Opdrachtnummer': str})
    df_pr.columns = df_pr.columns.str.replace(' ','_')

    
    df_pr=df_pr[df_pr['Projectnummer']==projectnummer]

    
    df_pr['TSA_SIGNED_TEST'] = df_pr['TSA_SIGNED'].astype(object)

    df_pr['VCA'] = df_pr.apply(
        lambda row: 'OK' if (pd.isna(row['TSA_SIGNED_TEST'])==False)&(row['VCA_Status']!='NOK') else row['VCA_Status'] ,
        axis=1
    )


    df_pr['PENDING'] = df_pr.apply(
        lambda row: 'PENDING' if (((row['Quadrant'])=='C')|(row['Quadrant']=='XC')|(row['Quadrant']=='A')|(row['Quadrant']=='XA')|(row['Quadrant']=='E')|(row['Quadrant']=='F')|(row['Quadrant']=='B'))&(row['VCA']=='') else '' ,
        axis=1
    )
    df_pr['VCA_Status'] = df_pr['VCA'] + df_pr['PENDING'] 

    df_pbi_pr = pbi.merge(df_pr, how='left', left_on='Lamkey', right_on='Opdrachtnummer',suffixes=('', '_PR'))

    df_pbi_pr['VCA_DELTA'] = np.where((df_pbi_pr['VCA']!=df_pbi_pr['VCA_Status']), 'yes', 'no')
    df_pbi_pr_delta=df_pbi_pr[df_pbi_pr['VCA_DELTA']=='yes']


    print(df_pbi_pr_delta[['Lamkey','Lu_Key','VCA','VCA_Status','Quadrant','Quadrant_PR']])

    
    df_vca_todo_manualy = df_pbi_pr_delta[df_pbi_pr_delta['VCA_Status']=='']
    df_vca_todo_manualy = df_vca_todo_manualy.drop_duplicates(subset=['Lamkey'])


    out.info_file('VCA Frost to do Manualy',df_vca_todo_manualy)




    pbi_vca_todo = pbi_rft_to_do.merge(df_pbi_pr_delta, how='outer', left_on='Lu_Key', right_on='Lu_Key',suffixes=('', '_PR'))

    print(pbi_vca_todo)


    total_rft_todo = len(pbi_rft_to_do.B2_new)
    total_rft_no = len(pbi_rft_no_past.B2)
    total_rft_yes = len(pbi_rft_yes_future.B2)
    total_b2_no = len(pbi_b2_no['B2_new'])

    out.menu_header("GCT Power BI update")
    out.info_file('Total RFT No B2 past',total_rft_no)
    out.info_file('Total RFT Yes B2 future',total_rft_yes)
    out.info_file('Total B2 empty',total_b2_no)
    out.info_file('Total changes B1 B2',total_rft_todo)

    pbi_rft_to_do['B2_new'] = pbi_rft_to_do['B2_new'].dt.strftime('%Y%m%d')
    pbi_rft_to_do['B2'] = pbi_rft_to_do['B2'].dt.strftime('%Y%m%d')
    pbi_rft_to_do['B1'] = pbi_rft_to_do['B1'].dt.strftime('%Y%m%d')

    #GCT_upload_W03-C-ANTWERPEN-WEST-FH01_20200705_101804
    print(area)

    pbi_vca_todo['B2_new'] = pbi_vca_todo['B2_new'].astype(object)
    pbi_vca_todo['B2_FINAL'] = pbi_vca_todo.apply(
        lambda row: row['B2_new'] if (pd.isna(row['B2_new'])==False) else row['B2_PR'] ,
        axis=1
    )
 
    pbi_vca_todo['B1'] = pbi_vca_todo['B1'].astype(object)
    pbi_vca_todo['B1_FINAL'] = pbi_vca_todo.apply(
        lambda row: row['B1'] if (pd.isna(row['B1'])==False) else row['B1_PR'] ,
        axis=1
    )
 
    pbi_vca_todo['Lamkey_FINAL'] = pbi_vca_todo.apply(
        lambda row: row['Lamkey'] if (pd.isna(row['Lamkey'])==False) else row['Lamkey_PR'] ,
        axis=1
    )
 


    pbi_vca_todo['B2_FINAL'] = pbi_vca_todo['B2_FINAL'].dt.strftime('%Y%m%d')
    pbi_vca_todo['B1_FINAL'] = pbi_vca_todo['B1_FINAL'].dt.strftime('%Y%m%d')



    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    pbi_rft_to_do = pbi_rft_to_do.assign(Zoning_FID=zoning_fid)
    pbi_rft_to_do = pbi_rft_to_do.assign(Zoning_ID=zoning_id)
    pbi_rft_to_do = pbi_rft_to_do.assign(Area=area)
    pbi_rft_to_do = pbi_rft_to_do.assign(E="")

    pbi_vca_todo = pbi_vca_todo.assign(Zoning_FID=zoning_fid)
    pbi_vca_todo = pbi_vca_todo.assign(Zoning_ID=zoning_id)
    pbi_vca_todo = pbi_vca_todo.assign(Area=area)
    pbi_vca_todo = pbi_vca_todo.assign(E="")


    filename = FOLDER_FROST + 'GCT_upload_' + area_upper + '_' + stamp + '.csv'

    out.info_file('Zoning FID', zoning_fid)
    out.info_file('Zoning ID', zoning_id)
    out.info_file('Area', area)


#    csv = pbi_rft_to_do.to_csv(filename,sep=';',index=False,columns=['Zoning_FID','Area', 'Zoning_ID','Lamkey','Lu_Key','E','Area','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','B1','B2_new'])

#Lamkey;Lu_Key;Block_Name;Street;House_Nr;House_Nr_Suffix;App_Nr;Postal_Code;Building_UnitsCITY_NAME;LU_nature;MUD/SDU;Quadrant;VCA;M5A;M6A;B1;B2;Handover_Date;Stop_Selling_Dt;Stop_Service_Dt;Best_Unit_Status;RFS;RFT;Building_Group_FID;Building_Group_name;OpdrachtID;Projectnummer;Opdrachtnummer;BG_Name;Blok;Straat;Huisnummer;Huisnummer_Toevoeging;Buildingtype;Quadrant_PR;NR_BU;NR_LU;NR_SU;UNITS_TOTAL;Surveyor;TSA_SENT;TSA_SIGNED;VCA_Status;Opdrachttemplate;TSA_SIGNED_TEST;VCA_PR;PENDING;VCA_DELTA

    filename_vca = FOLDER_FROST + 'vca_' + projectnummer + '.csv' 
    csv_vca_manual = df_vca_todo_manualy.to_csv(filename_vca,sep=';',index=False,columns=['Lamkey','Straat','Huisnummer','Huisnummer_Toevoeging','Quadrant','Quadrant_PR','BG_Name','VCA_Status','VCA'])
    out.info_file('csv VCA Frost to do Manualy written',filename_vca)
   

    filename_gct = FOLDER_FROST + 'gct_' + projectnummer + '.csv' 
    csv = pbi_vca_todo.to_csv(filename,sep=';',index=False,columns=['Zoning_FID','Area', 'Zoning_ID','Lamkey_FINAL','Lu_Key','E','Area','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','VCA_Status','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','B1_FINAL','B2_FINAL'])

    out.info_file('gct csv written',filename)


#make_gct()
