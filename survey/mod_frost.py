#!/usr/bin/env python3
#
#Make GCT upload from power_bi data (b1 en b2)
#based on rft yes and no
#
# mod_frost.py
import myoutput as out
import os
import pandas as pd

import mod_import_pr as imp

from datetime import datetime
from time import strftime

TEST_POWER_BI = os.path.dirname(os.path.realpath(__file__)) + '/frost/power_bi/data.xlsx'
TEST_PR = os.path.dirname(os.path.realpath(__file__)) + '/frost/power_bi/area.xlsx'


TEST_OUTPUT = os.path.dirname(os.path.realpath(__file__)) + '/frost/gct.csv'

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


    total_rft_todo = len(pbi_rft_to_do.B2_new)
    total_rft_no = len(pbi_rft_no_past.B2)
    total_rft_yes = len(pbi_rft_yes_future.B2)
    total_b2_no = len(pbi_b2_no['B2_new'])

    out.menu_header("GCT Power BI update")
    out.info_file('Total RFT No B2 past',total_rft_no)
    out.info_file('Total RFT Yes B2 future',total_rft_yes)
    out.info_file('Total B2 empty',total_b2_no)
    out.info_file('Total changes B1 B2',total_rft_todo)

    pbi_rft_to_do['B2_new'] = pbi_rft_to_do['B2_new'].dt.date
    pbi_rft_to_do['B2'] = pbi_rft_to_do['B2'].dt.date
    pbi_rft_to_do['B1'] = pbi_rft_to_do['B1'].dt.date

    #GCT_upload_W03-C-ANTWERPEN-WEST-FH01_20200705_101804
    area = pbi['Block_Name'][1]
    area = area.split('_')[0]
    area_upper = area.upper()
#    print(area)

#    print(areas)

    areas = areas[areas['Zoning_Name']==area]

    zoning_fid = areas['Zoning_FID'][0]
    zoning_id = areas['Zoning_ID'][0]

#    print(zoning_fid)
#    print(zoning_id)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")


    pbi_rft_to_do = pbi_rft_to_do.assign(Zoning_FID=zoning_fid)
    pbi_rft_to_do = pbi_rft_to_do.assign(Zoning_ID=zoning_id)
    pbi_rft_to_do = pbi_rft_to_do.assign(Area=area)
    pbi_rft_to_do = pbi_rft_to_do.assign(E="")


    filename = os.path.dirname(os.path.realpath(__file__)) + '/frost/'
    filename = filename + 'GCT_upload_' + area_upper + '_' + stamp + '.csv'

    out.info_file('Zoning FID', zoning_fid)
    out.info_file('Zoning ID', zoning_id)
    out.info_file('Area', area)

    csv = pbi_rft_to_do.to_csv(filename,sep=';',index=False,columns=['Zoning_FID','Area', 'Zoning_ID','Lamkey','Lu_Key','E','Area','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','E','B1','B2_new'])
    out.info_file('gct csv written',filename)


#make_gct()
