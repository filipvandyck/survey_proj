#!/usr/bin/env python3
####  units.py
####    


import sys
import os
import glob
import pandas as pd
import numpy as np
import math 

INPUTFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/input/' 
OUTPUTFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/output/' 

TESTFILE = os.path.dirname(os.path.realpath(__file__)) + '/units/Survey-Antwerpen-FH01.csv'
UNITSFILE = os.path.dirname(os.path.realpath(__file__)) + '/units/appeee/units.csv'
TESTOUTPUT = os.path.dirname(os.path.realpath(__file__)) + '/units/test.csv'

def columnToInt(df, column):
    df[column].fillna(value=0,inplace=True)    
    df[column] = df[column].astype(int)
    return(df)

def columnToStr(df, column):
    df[column].fillna(value='NA',inplace=True)    
    df[column] = df[column].astype(str)
    return(df)

def clean_str(x):
    x = str(x)
    x = x.replace("'", "")
    return(x)

def convert_float(x):
    x = x.replace("'", "")
    x = x.replace(",", ".")
    x = x.replace(" ", "/")
    try:
        return float(x)
    except ValueError:
        return('')  

def convert_int(x):
    x  = clean_str(x)
    x = x.replace(" ", "/")
   
    try:
        x = int(x)
    except ValueError:
        x = 0  
    
    if x > 0:
        return(x)
    else:
        return('')  

def check_sub(x):
    x  = str(x)
    ch = True
    x = x.replace("'", "")
    if "/" in x:
        ch = False
    if "." in x:
        ch = False
    if len(x) > 5:
        ch = False
    
    if ch == True:
        return(x)
    else:
        return('')


def convert_int2(x):
    x  = clean_str(x)
    x = x.replace(" ", "/")
    try:
        x = int(x)
    except ValueError:
        x = ''  
    
    return(x)  


def LUindexDF(df,columnLAM,columnNature):
    LAMPREV = ''
    LAM = ''
    teller = 1
    LUteller = 0
    BUteller = 0
    SUteller = 0
    rowteller = 0
    unitteller = 0 

    for index, row in df.iterrows():
        LAM = row[columnLAM]


        if LAM != LAMPREV:
            teller = 1
            LUteller = 0
            BUteller = 0
            SUteller = 0
            unitteller = 0  


        if row[columnNature] == 'LU':
            LUteller += 1
            NatureIndex = 'LU' + str(LUteller)
            unitteller += 1 

        if row[columnNature] == 'BU':
            BUteller += 1
            NatureIndex = 'BU' + str(BUteller)
            unitteller += 1

        if row[columnNature] == 'SU':
            SUteller += 1
            NatureIndex = 'SU' + str(SUteller)
        

        LAM_Nature_index = str(LAM) + '-' + str(NatureIndex)
        df.loc[index,'LAM Nature index'] = LAM_Nature_index
        df.loc[index,'Unit Counter'] = unitteller



        rowteller = rowteller + 1        
        teller = teller + 1
        LAMPREV = LAM
    return(df) 

def processfile(f):

    print('processing:' + f)
    survey = pd.read_csv(f, delimiter=';',encoding = "ISO-8859-1", keep_default_na=False)
    survey.columns = survey.columns.str.replace(' ','_')

    survey['adres_full'] = survey['Street'].apply(clean_str) + ' ' + survey['Nr'].apply(clean_str) + survey['Suffix'].apply(clean_str)    


    # enkel mdu's en niet deletes uitfilteren

    survey = survey[survey['SSV_Action_LU']!='DELETE']
    survey = survey[survey['SSV_Action']!='DELETE']

    df_lu = survey[survey['Nature'] == 'LU'].groupby(['adres_full']).size().reset_index(name='LU')
    df_bu = survey[survey['Nature'] == 'BU'].groupby(['adres_full']).size().reset_index(name='BU')
    df_su = survey[survey['Nature'] == 'SU'].groupby(['adres_full']).size().reset_index(name='SU')
 
    survey = df_lu.merge(survey, how='right')
    columnToInt(survey,'LU')

    survey = df_bu.merge(survey, how='right')
    columnToInt(survey,'BU')

    survey = df_su.merge(survey, how='right')
    columnToInt(survey,'SU')

    survey['BT'] = np.where( survey.BU + survey.LU > 1, 'MDU','SDU')

    survey = survey[survey['BT']=='MDU']


    # aantal units / verdieping

    survey['GUESSED_UNITS_FLOOR'] = (survey['LU'] + survey['BU'])/survey['Number_Floors'] 



    survey = survey.sort_values(by=['LAM_MK', 'Nature'])
    

    # units indexeren (nieuwe hebben geen key)

    survey = LUindexDF(survey,'planrrr_bid','Nature')
    print(survey)

    # verdieping waar het unit wss zal zitten op basis van units / verdieping

    survey['GUESSED_FLOOR'] = survey['Unit Counter']/survey['GUESSED_UNITS_FLOOR'] - ( 1 / survey['GUESSED_UNITS_FLOOR'] )
    survey['GUESSED_FLOOR_TRUNC'] = survey['GUESSED_FLOOR'].apply(math.trunc)

    
    print('processing units: ' + UNITSFILE)
    
    
    units = pd.read_csv(UNITSFILE, delimiter=';', encoding = "ISO-8859-1", keep_default_na=False)
    units = units.sort_values(by=['LAMKEY', 'NATURE'])

    columnToStr(units,'LAMKEY')
    columnToStr(survey,'LAM_MK')
    
    # units met gekende lamkey uitfilteren

    units = units[units.LAMKEY.isin(survey['LAM_MK'])]


   
    print(survey['LAM_MK'])

    # indexeren van units 

    units = LUindexDF(units,'LAMKEY','NATURE')  

  
   
    # op basis van index samenvoegen

    merge = survey.merge(units, on='LAM Nature index', how='left')


    print(merge)

    ### FLOOR invullen indien aanwezig en valid. ingevulde nemen anders de guessed (berekende)

    for index, row in merge.iterrows():
        guessed_floor = row['GUESSED_FLOOR_TRUNC']
        number_floors = row['Number_Floors']
        print(row['FLOOR'])
        floor = row['FLOOR']
        nature = row['Nature']

        merged_floor = 99
        try:
            floor = int(floor)
            if floor <= number_floors:
                merged_floor = floor
            else:
                merged_floor = guessed_floor
        except ValueError:
            merged_floor = guessed_floor


        if nature == 'SU':
            merged_floor = 0


        merge.loc[index,'MERGED_FLOOR'] = merged_floor

    merge['MERGED_FLOOR'] = merge['MERGED_FLOOR'].apply(math.trunc)


    merge = merge.sort_values(by=['LAM_MK', 'Nature','MERGED_FLOOR'])




    ### APP BEREKENEN UIT MERGED FLOOR + NATURE
    #### NIET MOOI FILIP!!!



    unitcounter = 0
    floor_prev = 99
    sucounter = 0
    for index, row in merge.iterrows():
        floor = row['MERGED_FLOOR']
        nature = row['Nature']
        app = ''

        if floor_prev != floor :
            unitcounter = 1
            if nature == 'SU':
                unitcounter = 0
            sucounter = 1
        else:
            if nature == 'SU':
                sucounter += 1
            else:
                unitcounter += 1 
        
        if nature == 'SU':
            app = 'SU' + str(sucounter)
        else:
            if unitcounter < 10:
                app = str(floor) + '0' + str(unitcounter)
            else:
                app = str(floor) + str(unitcounter)
                
        merge.loc[index,'MERGED_APP'] = app
        
 
 
        merge['MERGED_APP'] = merge['MERGED_APP'].apply(str)
 
 
        floor_prev = floor



    
    ### PBOX app of merged app gebruiken als pbox leeg is


    for index, row in merge.iterrows():
        pbox = row['PBOX']
        app = row['APP']
        merged_app = row['MERGED_APP']
        merged_pbox = ''


        if pbox != '' and not pd.isna(pbox) :
            merged_pbox = pbox
        else:
            if app != '' and not pd.isna(app) :
                merged_pbox = app
            else:
                merged_pbox = merged_app

        merge.loc[index,'MERGED_PBOX'] = merged_pbox
        



        




    print(merge)

    merge.to_csv(TESTOUTPUT,index=False, sep=";")
'''

    answer = input("Street survey [S] | Site Survey [SS] | Map [M] | All [A] ::> ") 
    if answer == 'S' or answer == 's':
        process_for_street_survey(survey)
    if answer == 'M' or answer == 'm': 
        draw_map(survey)
    if answer == 'SS' or answer == 'ss': 
        process_for_street_survey(survey)
        process_for_site_survey(survey)
    if answer == 'a' or answer == 'A': 
        process_for_street_survey(survey)
        process_for_site_survey(survey)
        draw_map(survey)

'''


#processfile(TESTFILE)





def getimportfiles(directory):
    files = [f for f in glob.glob(directory + "*.csv")]
    return(files)




directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),'units/')
importFiles = getimportfiles(directory)
for f in importFiles:
    processfile(f)


