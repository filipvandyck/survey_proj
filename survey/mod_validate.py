#!/usr/bin/env python3
#
# mod_validate.py

#requires geopandas 
#requires rtree 

import sys
import os
import glob
import pandas as pd
import numpy as np

import geopandas
import folium
import webbrowser

import myoutput as out


LIST_HEADER = ['File SSV Action', 'File SSV Status', 'File SSV Error', 'Area Type', 'Area FID', 'Area Version', 'Area Name', 'Zoning FID', 'Zoning Version', 'Zoning Name', 'Zoning Id', 'Zoning Tech', 'BG Id', 'BG Version', 'BG Name', 'BG SSV Action', 'BG SSV Status', 'BG SSV Error', 'BG Building SSV Action', 'BG Building SSV Status', 'BG Building SSV Error', 'Building FID', 'Building Version', 'LAM MK', 'LAM City Code', 'LAM Street Code', 'Street', 'Nr', 'Suffix', 'Zip', 'Municipality', 'Suburb', 'xPos', 'yPos', 'Name', 'Wall Mount', 'SS Reason', 'Number Floors', 'Height Cable', 'Orig VC Type', 'New VC Type', 'VC Method', 'Intro Tube', 'Prov Status', 'Prov Reason', 'Prov Planned', 'Prov Mod By', 'Prov Mod Date', 'Comments', 'SSV Flag', 'SSV Action', 'SSV Status', 'SSV Error', 'SSV Date', 'Seq', 'LU Key', 'LAM SK', 'Nature', 'Nr TPs', 'PBox', 'App', 'Block', 'Floor', 'OtherRef', 'CAD', 'CAD Details', 'CAD Type', 'CAD Type Descr', 'CAD SubType', 'Prov Status LU', 'Prov Reason LU', 'Prov Planned LU', 'Prov Mod By LU', 'Prov Mod Date LU', 'Comments LU', 'SSV Flag LU', 'SSV Action LU', 'SSV Status LU', 'SSV Error LU', 'SSV Date LU', 'planrrr_bid', 'planrrr_uid']


VALIDATEFOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)),'validate/')



TESTFILE = os.path.dirname(os.path.realpath(__file__)) + '/Survey-Test2.csv'
TESTGML = os.path.dirname(os.path.realpath(__file__)) + '/validate/evere.gml'
TESTGEOJSON = os.path.dirname(os.path.realpath(__file__)) + '/validate/evere.geojson'




def columnToInt(df, column):
    df[column].fillna(value=0,inplace=True)    
    df[column] = df[column].astype(int)
    return(df)

def columnToStr(df, column):
    df[column].fillna(value='NA',inplace=True)    
    df[column] = df[column].astype(str)
    return(df)

#### COLUMN CHECK :: EMPTY 
def check_column_must_be_empty(df, column):
    check = 'check for: column must be empty column [' + column + ']'
    df = df[df[column] !='']
    errors = print_errors_check_df(df,column,check)

def check_columns_must_be_empty(df,columns):
    for column in columns:
        check_column_must_be_empty(df,column)

#### COLUMN CHECK :: NOT EMPTY

def check_column_cant_be_empty(df, column):
    check = 'check for: column cant be empty [' + column + ']' 
    df = df.astype(str)
    df = df[df[column] =='']
    errors = print_errors_check_df(df,column,check)

def check_columns_cant_be_empty(df,columns):
    for column in columns:
        check_column_cant_be_empty(df,column)

### COLUMN CHECK :: SAME VALUE

def check_column_must_be_the_same(df, column):
    df = df.astype(str)
    df = df[column].value_counts()
    if df.size > 1:
        print('check for: column must be the same [' + column + ']' )
        print('!!!ERROR MULTIPLE VALUES FOR COLUMN :: ' + column)
        print(df)
        print('!!!')
 #   else:
 #       print('OK')
 
def check_columns_must_be_the_same(df,columns):
    for column in columns:
        check_column_must_be_the_same(df,column)


### COLUMN CHECK :: SAME VALUE FOR LAM KEY

def check_adrescount_for_lam(df):
    df = df.groupby('adres').LAM_MK.value_counts().reset_index(name='count')
    df = df.groupby('adres').count()
    df = df[df['count'] > 1]
    if df.size > 1:
        print('check for: lam key must be the unique for adres')
        print('!!!ERROR MULTIPLE LAM FOUND FOR ADRES ')
        print(df)
        print('!!!')
#    else:
#        print('OK')
 

### COLUMN CHECK :: SAME VALUE FOR LAM KEY (adres nb)

def check_column_must_be_the_same_for_lam(df, column):
    df = df.astype(str)
#    print(column)
    df = df[df[column] != '']
    if df.size > 0:
        df = df.groupby(column).adres.value_counts().reset_index(name='count')
        df = df.groupby('adres').count()
        df = df[df['count'] > 1]
        if df.size > 1:
            print('check for: column must be the same for lam key [' + column + ']' )
            print('!!!ERROR MULTIPLE VALUES FOR COLUMN :: ' + column)
            print(df)
            print('!!!')
#    else:
#        print('OK')
   
def check_columns_must_be_the_same_for_lam(df,columns):
    for column in columns:
        check_column_must_be_the_same_for_lam(df,column)

### COLUMN CHECK :: SAME VALUE FOR STREET 

def check_column_must_be_the_same_for_street(df, column):
    df = df[df[column] != ''].groupby(column).Street.value_counts().reset_index(name='count')
    df = df.groupby('Street').count()
    df = df[df['count'] > 1]
    if df.size > 1:
        print('check for: column must be the same for street [' + column + ']' )
        print('!!!ERROR MULTIPLE VALUES FOR COLUMN :: ' + column)
        print(df)
        print('!!!')
#    else:
#        print('OK')
   
def check_columns_must_be_the_same_for_street(df,columns):
    for column in columns:
        check_column_must_be_the_same_for_street(df,column)




def print_errors_check_df(df,column,check):
    if df.empty:
        pass
    else:    
        print(check)
        print('!!!ERROR ON:')
        print(df[['LAM_MK','Street','Nr','Suffix',column]])
        print('!!!')







def clean_str(x):
    x = str(x)
    x = x.replace("'", "")
    return(x)

def convert_float(x):
    x = x.replace("'", "")
    x = x.replace(".", "/")
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











def processfile(f, polyglon='', process_for='S'):

    out.info_file('Validate file', f)
  


    survey = pd.read_csv(f, delimiter=';',encoding = "ISO-8859-1", keep_default_na=False)

    
    out.info_file('Check heading file', f)
    lstColumns = list(survey.columns)
    if lstColumns != LIST_HEADER :
        print('BAD Header file!!!\n\n')

    survey.columns = survey.columns.str.replace(' ','_')

    survey['adres_full'] = survey['Street'].apply(clean_str) + ' ' + survey['Nr'].apply(clean_str) + survey['Suffix'].apply(clean_str)    

    survey['x'] = survey['xPos'].apply(convert_float)
    survey['y'] = survey['yPos'].apply(convert_float)
 
    if polyglon != '':
        check_poly(survey, polyglon)
    if process_for == 'S':
        process_for_street_survey(survey)
    if process_for == 'SS': 
        process_for_street_survey(survey)
        process_for_site_survey(survey)




def check_poly(survey, gmlfile):
      
    out.info_file('Check polyglon load GML', gmlfile)



    gdf_poly = geopandas.read_file(gmlfile)
    gdf_survey = geopandas.GeoDataFrame(survey, geometry=geopandas.points_from_xy(survey.x, survey.y))
        
    gdf_survey.crs = {'init' :'epsg:31370'}
        
    gdf_survey_in = geopandas.sjoin(gdf_survey, gdf_poly, op = 'within')

        
    s_survey = set(gdf_survey['adres_full'].unique())
    s_survey_in = set(gdf_survey_in['adres_full'].unique())

    s_outside = s_survey.difference(s_survey_in)



    out.print_s(s_outside,'Outside the Area')
        





def process_for_street_survey(survey):

    out.menu_header('STREET SURVEY')



    check_columns_must_be_empty(survey,['File_SSV_Action','File_SSV_Status','File_SSV_Error','BG_SSV_Status','BG_SSV_Error','BG_Building_SSV_Status','BG_Building_SSV_Error','Name'])
    check_columns_cant_be_empty(survey,['Area_Type','Area_FID','Area_Version','Area_Name', 'Zoning_FID', 'Zoning_Version', 'Zoning_Name', 'Zoning_Id', 'Zoning_Tech','LAM_City_Code','LAM_Street_Code','Street','Nr','Zip','Municipality','xPos','yPos','Wall_Mount','SS_Reason','SSV_Action','Nature','SSV_Action_LU'])
    
    check_columns_cant_be_empty(survey[survey['SSV_Action']!='NEW'],['LAM_MK','Building_FID'])
    check_columns_cant_be_empty(survey[survey['SSV_Action_LU']!='NEW'],['LU_Key','Seq'])
    
    check_columns_must_be_the_same(survey,['Area_Type','Area_FID','Area_Version','Area_Name', 'Zoning_FID', 'Zoning_Version', 'Zoning_Name', 'Zoning_Id', 'Zoning_Tech','LAM_City_Code','Zip','Municipality'])


    survey['adres'] = survey['Street'] + survey['Nr'] + survey['Suffix']

    check_adrescount_for_lam(survey)



    #check_columns_must_be_the_same_for_lam(survey,['BG_Id','Prov Status','Prov Reason','Prov Status LU','Prov Reason LU','BG_Version','BG_Name','BG_SSV_Action','Building_FID','Building_Version','Street','Nr','Suffix','xPos','yPos','Wall_Mount','SS_Reason','Number_Floors','Height_Cable','VC_Method','SSV_Action'])
    check_columns_must_be_the_same_for_lam(survey,['BG_Id','Prov_Status','Prov_Reason','Prov_Status_LU','Prov_Reason_LU','BG_Version','BG_Name','BG_SSV_Action','Building_FID','Building_Version','Street','Nr','Suffix','xPos','yPos','Wall_Mount','SS_Reason','Number_Floors','Height_Cable','VC_Method','SSV_Action'])

    #######  PROV STATUS
    checkValidValues(survey,'Prov_Status_LU',['B',''])
    checkValidValues(survey,'Prov_Status',['B',''])

    checkValidValues(survey,'Prov_Reason',['BOWN','BNEO',''])
    checkValidValues(survey,'Prov_Reason_LU',['BOWN','BNEO',''])


    #######  BUILDING GROUPS
    checkValidValues(survey,'BG_SSV_Action',['MODIFY','DELETE','KEEP','NEW',''])
    checkValidValues(survey,'BG_Building_SSV_Action',['MODIFY','DELETE','KEEP','NEW',''])
   
    check_columns_cant_be_empty(survey[survey['BG_Id']!=''],['BG_Name', 'BG_Version','BG_SSV_Action', 'BG_Building_SSV_Action'])
    checkValidValues(survey[survey['BG_Id']!=''],'BG_SSV_Action',['MODIFY','DELETE','KEEP'])
    checkValidValues(survey[survey['BG_Id']!=''],'BG_Building_SSV_Action',['MODIFY','DELETE','KEEP'])

    checkValidValues(survey[survey['BG_Building_SSV_Action']=='NEW'],'BG_Id','')
    checkValidValues(survey[survey['BG_Building_SSV_Action']=='NEW'],'BG_SSV_Action',['NEW'])
    
    checkValidValues(survey[survey['BG_SSV_Action']=='NEW'],'BG_Id','')
    checkValidValues(survey[survey['BG_SSV_Action']=='NEW'],'BG_Building_SSV_Action',['NEW'])

    #######  BUILDING GROUPS

    check_columns_must_be_the_same_for_street(survey,['LAM_Street_Code'])
    
    
    
    ####### XPOS YPOS 
    
    
    survey['xPos'] = survey['xPos'].apply(convert_float)
    survey['yPos'] = survey['yPos'].apply(convert_float)
    
    check_columns_cant_be_empty(survey,['xPos','yPos'])



    #######  WALL MOUNT

    survey_building_no_deletes = survey[survey['SSV_Action'] != 'DELETE'] 
    
    checkValidValues(survey[survey['SS_Reason'] != 'DELETE'],'Wall_Mount',['Y','N'])
    checkValidValues(survey,'Wall_Mount',['Y','N','NA'])
    checkValidValues(survey,'SS_Reason',['HEIGHT','NA','ORN','IRREG','MON','GLASS'])

    checkValidValues(survey_building_no_deletes[survey_building_no_deletes['Wall_Mount'] == 'N'],'SS_Reason',['HEIGHT','ORN','IRREG','MON','GLASS'])
    checkValidValues(survey[survey['Wall_Mount'] == 'Y'],'SS_Reason',['MON','NA'])
   

    ####### NUMBER FLOORS 
    
    
    survey['Number_Floors'] = survey['Number_Floors'].apply(convert_int)
    check_columns_cant_be_empty(survey[survey['SSV_Action'] != 'DELETE'],['Number_Floors'])


    ####### HEIGHT CABLE 
    
    
    survey['Height_Cable'] = survey['Height_Cable'].apply(convert_int)
    check_columns_cant_be_empty(survey[survey['Wall_Mount'] == 'Y'],['Height_Cable'])

    ####### VC METHOD 
   
    checkValidValues(survey,'VC_Method',['','D - Facade Box','A - Floorbox','C - Precabled ONTP','X - Awaiting decision on B','B - G.Fast','F - Fiber','E - CAT5e-6'])
    
    ####### NR TPs 
   
    checkValidValues(survey,'Nr_TPs','1')
    
    
    ####### SSV ACTION


    checkValidValues(survey,'SSV_Action',['MODIFY','DELETE','KEEP','NEW'])
    checkValidValues(survey[survey['SSV_Action'] == 'NEW'],'LAM_MK',[''])
    checkValidValues(survey[survey['SSV_Action'] == 'NEW'],'Building_FID',[''])
    checkValidValues(survey[survey['SSV_Action'] == 'NEW'],'LU_Key',[''])
    checkValidValues(survey[survey['SSV_Action'] == 'NEW'],'SSV_Action_LU',['NEW'])
   
    checkValidValues(survey[survey['SSV_Action'] == 'DELETE'],'SSV_Action_LU',['DELETE'])
    
    
    print('check for: if all SSV Action LU is DELETE then SSV Action must be DELETE' )
    df1 = survey[survey['SSV_Action'] != 'DELETE'].groupby('adres').Street.value_counts().reset_index(name='count')
    df2 = survey[survey['SSV_Action_LU'] != 'DELETE'].groupby('adres').Street.value_counts().reset_index(name='count')
    df3 = pd.concat([df1['adres'],df2['adres']]).drop_duplicates(keep=False)
    if df3.empty:
        print('OK')
    else:       
        print('!!!ERROR ON:')
        print(df3)
        print('!!!')


    ####### SEQ LU KEY 

    df1 = survey[survey['SSV_Action_LU']!='NEW']
    survey['Seq'] = survey['Seq'].apply(convert_int)
    check_columns_cant_be_empty(df1,['Seq'])
    
    print('check for: SEQ must be unique for LAM' )
    df1 = survey[survey['SSV_Action_LU'] != 'NEW'].groupby('LAM_MK').Seq.value_counts().reset_index(name='count')
    
    df1 = df1[df1['count']>1]
    if df1.empty:
        print('OK')
    else:       
        print('!!!ERROR ON:')
        print(df1)
        print('!!!')

    check_columns_must_be_empty(survey[survey['SSV_Action_LU']=='NEW'],['Seq','LU_Key'])

    #######  NATURE


    checkValidValues(survey,'Nature',['BU','LU','SU'])





def process_for_site_survey(survey): 

    out.menu_header('STREET SURVEY')



    ####### PBOX

    survey2 = survey[survey['SSV_Action_LU']!='DELETE']
    survey2 = survey2[survey2['SSV_Action']!='DELETE']

    df_lu = survey2[survey2['Nature'] == 'LU'].groupby(['adres']).size().reset_index(name='LU')
    df_bu = survey2[survey2['Nature'] == 'BU'].groupby(['adres']).size().reset_index(name='BU')
    df_su = survey2[survey2['Nature'] == 'SU'].groupby(['adres']).size().reset_index(name='SU')
 
    survey2 = df_lu.merge(survey2, how='right')
    columnToInt(survey2,'LU')

    survey2 = df_bu.merge(survey2, how='right')
    columnToInt(survey2,'BU')

    survey2 = df_su.merge(survey2, how='right')
    columnToInt(survey2,'SU')

    survey2['BT'] = np.where( survey2.BU + survey2.LU > 1, 'MDU','SDU')


    print('check for: PBOX must be unique for LAM' )
    df1 = survey2[survey2['BT'] == 'MDU'].groupby('adres').PBox.value_counts().reset_index(name='count')
    
    df1 = df1[df1['count']>1]
    if df1.empty:
        print('OK')
    else:       
        print('!!!ERROR ON:')
        print(df1)
        print('!!!')


    survey2['PBox'] = survey2['PBox'].apply(check_sub)
    check_columns_cant_be_empty(survey2[survey2['BT'] == 'MDU'],['PBox'])

    ####### APP 

    print('check for: APP must be unique for LAM' )
    df1 = survey2[survey2['BT'] == 'MDU'].groupby('adres').App.value_counts().reset_index(name='count')
    
    df1 = df1[df1['count']>1]
    if df1.empty:
        print('OK')
    else:       
        print('!!!ERROR ON:')
        print(df1)
        print('!!!')

    survey2['App'] = survey2['App'].apply(check_sub)
    check_columns_cant_be_empty(survey2[survey2['BT'] == 'MDU'],['App'])


    ####### FLOOR 
    
    
    survey2 = survey2[survey2['BT'] == 'MDU']
    survey2['Floor'] = survey2['Floor'].apply(convert_int2)
    check_columns_cant_be_empty(survey2,['Floor'])
    survey2['Number_Floors'] = survey2['Number_Floors'].apply(convert_int2)
  #  print(survey2['Floor'])

    print('check for: Floor < Number Floors' )
 #   df2 = survey2.query('Floor > Number_Floors')
 #   check_column_must_be_empty(df2,'adres')

    try:
      #  df2 = survey2.query('Floor < Number_Floors')
        df2 = survey2.query('Floor > Number_Floors')
        check_column_must_be_empty(df2,'adres')
    except :
        print('FAIL')
    
    print('#####################SITE SURVEY######################')
    print('######################################################')



def checkValidValues(df,column,vCheck):
    if vCheck != '':
        ch = ''
        for check in vCheck:
            ch = ch + column + ' != "' + str(check) + '" and '
        ch = ch.rstrip(' and ')
        df = df.query(ch)
    else:
        df = df.query(column + '!=""')
    if df.empty:
        pass
    #    print('OK')
    else:       
        print('Check for valid values in column [' + column + ']')
        print('!!!ERROR ON:')
        print(df[['LAM_MK','Street','Nr','Suffix',column]])
        print('valid:') 
        for check in vCheck:
            print('-->' + str(check))
        print('!!!')

#processfile(TESTFILE)





def getimportfiles(directory):
    files = [f for f in glob.glob(directory + "*.csv")]
    return(files)
'''

directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),'validate/')
validateFiles = getimportfiles(directory)
for f in validateFiles:
    processfile(f)
'''

