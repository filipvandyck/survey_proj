#!/usr/bin/env python3
#
# mod_import_pr.py




import sys
import os
import glob
import pandas as pd
import numpy as np

import myoutput as out




INPUTFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/exports/' 
OUTPUTFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/imports/' 


INPUT_STREET_FILE = os.path.dirname(os.path.realpath(__file__)) + '/exports/streets/streets.csv' 
INPUT_CITY_FILE = os.path.dirname(os.path.realpath(__file__)) + '/exports/streets/cities.csv' 







def getimportfiles(directory):
    files = [f for f in glob.glob(directory + "*.csv")]
    return(files)

def getoutputfile(importfile):
    the_file= os.path.basename(importfile)
    return("import_pr_street_survey_" + the_file)

def getoutputversionfile(importfile):
    the_file= os.path.basename(importfile)
    return("import_pr_versions_" + the_file)


def getoutputBlockfile(importfile):
    the_file= os.path.basename(importfile)
    return("import_block_pr_" + the_file)




def make_versions_import(file1, outputfolder):
    out.info_file('processing file for version import',file1)


    survey = pd.read_csv(file1, delimiter=';', encoding = "ISO-8859-1")
    survey_obj = survey.select_dtypes(['object'])

    survey[survey_obj.columns] = survey_obj.apply(lambda x: x.str.lstrip("'"))
   

    columnToInt0isEmpty(survey,'BG Id')
  #  columnToInt0isEmpty(survey,'BG Version')

    versions = survey.drop_duplicates(subset='LAM MK', keep='first')
    

    area = survey['Area Name'].iloc[0]

    outputdir = outputfolder + area
   
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    exportfile = outputdir + "/" + getoutputversionfile(file1)


    csv = versions.to_csv(exportfile,sep=';',columns=['LAM MK','Area Type','Area FID','Area Version','Area Name', 'Zoning FID','Zoning Version','Zoning Name','Zoning Id','Zoning Tech','BG Version','Building FID','Building Version','BG Id','LAM City Code','LAM Street Code'],index=False)



    out.info_file('writing version import file',file1)




def make_survey_import(file1, outputfolder, streetfile, cityfile, output_to_area=False):
    out.info_file('processing file for survey import',file1)

    survey = pd.read_csv(file1, delimiter=';', encoding = "ISO-8859-1")
    survey_obj = survey.select_dtypes(['object'])
    


    survey[survey_obj.columns] = survey_obj.apply(lambda x: x.str.lstrip("'"))
   

    # replace street with unique street name from csv
    
    input_streets = pd.read_csv(streetfile, delimiter=';', encoding = "ISO-8859-1")

    columnToStr(survey,'LAM Street Code')
    columnToStr(survey,'Zip')

    survey['id'] = survey[['Zip', 'LAM Street Code']].apply(lambda x: '-'.join(x), axis=1)
    survey = pd.merge(input_streets,survey,how='right', on=['id','id'])

    survey['Street'] = survey.Street_x.combine_first(survey.Street_y)
    survey['Zip'] = survey.Zip_x.combine_first(survey.Zip_y)
    
    survey = survey.drop(columns=['LAM_Street_Code','Zip_x','Zip_y','id','Street_y','Street_x','Area_Name'])
    
    # replace city with unique street name from csv

    input_cities = pd.read_csv(cityfile, delimiter=';', encoding = "ISO-8859-1")

    columnToStr(survey,'Zip')
    columnToStr(input_cities,'Zip')

    survey = pd.merge(input_cities,survey,how='right', on=['Zip','Zip'])

    survey['Municipality'] = survey.Municipality_x.combine_first(survey.Municipality_y)
    
    survey = survey.drop(columns=['Municipality_x','Municipality_y'])
  

    survey['SSV Date']=''
    survey['SSV Flag']=''
    survey['SSV Flag LU']=''
    survey['SSV Date LU']=''
    survey['Prov Mod By'] = ''
    survey['Prov Mod Date'] = ''

    survey['Prov Mod By LU'] = ''
    survey['Prov Mod Date LU'] = ''
    survey['Name'] = ''



    survey['LANGUAGE']='NL'
    
    df_lu = survey[survey['Nature'] == 'LU'].groupby(['LAM MK']).size().reset_index(name='LU')
    df_bu = survey[survey['Nature'] == 'BU'].groupby(['LAM MK']).size().reset_index(name='BU')
    df_su = survey[survey['Nature'] == 'SU'].groupby(['LAM MK']).size().reset_index(name='SU')
    df_totaal = survey[survey['Nature'] != ''].groupby(['LAM MK']).size().reset_index(name='TOTAAL')
 
    survey = df_lu.merge(survey, how='right')
    columnToInt(survey,'LU')

    survey = df_bu.merge(survey, how='right')
    columnToInt(survey,'BU')

    survey = df_su.merge(survey, how='right')
    columnToInt(survey,'SU')

    survey = df_totaal.merge(survey, how='right')
    columnToInt(survey,'TOTAAL')
 
    survey['BT'] = np.where( survey.BU + survey.LU > 1, 'MDU','SDU')

    columnToInt(survey,'Number Floors')
    columnToInt(survey,'Height Cable')
    columnToStr(survey,'SS Reason')
    columnToStr(survey,'Wall Mount')

    columnToInt0isEmpty(survey,'LAM SK')
    columnToInt0isEmpty(survey,'BG Id')
    columnToInt0isEmpty(survey,'LAM MK')
    columnToInt0isEmpty(survey,'Building FID')
    columnToInt0isEmpty(survey,'Seq')
    columnToInt0isEmpty(survey,'LU Key')
   # columnToInt0isEmpty(survey,'BG Version')

    columnReplaceChar(survey, 'xPos', ".", ",")
    columnReplaceChar(survey, 'yPos', ".", ",")

    area = ''    
    if output_to_area == True:
        area = survey['Area Name'].iloc[0] + '/'


    outputdir = outputfolder + area 
   
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    exportfile = outputdir + getoutputfile(file1)

    survey = survey[['File SSV Action', 'File SSV Status', 'File SSV Error', 'Area Type', 'Area FID', 'Area Version', 'Area Name', 'Zoning FID', 'Zoning Version', 'Zoning Name', 'Zoning Id', 'Zoning Tech', 'BG Id', 'BG Version', 'BG Name', 'BG SSV Action', 'BG SSV Status', 'BG SSV Error', 'BG Building SSV Action', 'BG Building SSV Status', 'BG Building SSV Error', 'Building FID', 'Building Version', 'LAM MK', 'LAM City Code', 'LAM Street Code', 'Street', 'Nr', 'Suffix', 'Zip', 'Municipality', 'Suburb', 'xPos', 'yPos', 'Name', 'Wall Mount', 'SS Reason', 'Number Floors', 'Height Cable', 'Orig VC Type', 'New VC Type', 'VC Method', 'Intro Tube', 'Prov Status', 'Prov Reason', 'Prov Planned', 'Prov Mod By', 'Prov Mod Date', 'Comments', 'SSV Flag', 'SSV Action', 'SSV Status', 'SSV Error', 'SSV Date', 'Seq', 'LU Key', 'LAM SK', 'Nature', 'Nr TPs', 'PBox', 'App', 'Block', 'Floor', 'OtherRef', 'CAD', 'CAD Details', 'CAD Type', 'CAD Type Descr', 'CAD SubType', 'Prov Status LU', 'Prov Reason LU', 'Prov Planned LU', 'Prov Mod By LU', 'Prov Mod Date LU', 'Comments LU', 'SSV Flag LU', 'SSV Action LU', 'SSV Status LU', 'SSV Error LU', 'SSV Date LU','LU','BU','SU','TOTAAL','LANGUAGE','BT']]

    csv = survey.to_csv(exportfile,sep=';',index=False)
    
    
    out.info_file('writing street survey import file', exportfile)



def make_street_names(file1,streetfile):

    out.info_file('processing street file for new streets',streetfile)


    survey = pd.read_csv(file1, delimiter=';', encoding = "ISO-8859-1")
    input_streets = pd.read_csv(streetfile, delimiter=';', encoding = "ISO-8859-1")
    survey.columns = survey.columns.str.replace(' ','_')
    input_streets.columns = input_streets.columns.str.replace(' ','_')


    columnToStr(survey,'LAM_Street_Code')
    columnToStr(survey,'Zip')
    
    columnReplaceChar(survey, 'LAM_Street_Code', "'", "")
    columnReplaceAllChars(survey, 'Street')
    
  


    streets = survey.groupby(['LAM_Street_Code','Street','Zip','Area_Name']).count().reset_index()
   

    streets['id'] = streets[['Zip', 'LAM_Street_Code']].apply(lambda x: '-'.join(x), axis=1)

    out_streets = pd.merge(input_streets,streets,how='outer', on=['id','id'])

    out_streets['Street'] = out_streets.Street_x.combine_first(out_streets.Street_y)
    out_streets['Zip'] = out_streets.Zip_x.combine_first(out_streets.Zip_y)
    out_streets['LAM_Street_Code'] = out_streets.LAM_Street_Code_x.combine_first(out_streets.LAM_Street_Code_y)
    out_streets['Area_Name'] = out_streets.Area_Name_x.combine_first(out_streets.Area_Name_y)

    out_streets = out_streets.drop_duplicates(subset='id', keep='first')
    
    columnToInt(out_streets,'Zip')
    columnToInt(out_streets,'LAM_Street_Code')

    csv = out_streets.to_csv(streetfile,sep=';',columns=['id','Zip','LAM_Street_Code','Street','Area_Name'],index=False)




    out.print_df(streets,['LAM_Street_Code','Street','Area_Name'],'input streets')
    out.print_df(out_streets,['LAM_Street_Code','Street','Area_Name'],'output streets')
    out.info_file('New streets found', str(out_streets.shape[0] - input_streets.shape[0]) )
    out.info_file('writing output streets file', streetfile)




def make_city_names(file1,cityfile):
    out.info_file('processing city file for new cities',cityfile)
    

    survey = pd.read_csv(file1, delimiter=';', encoding = "ISO-8859-1")
    input_cities = pd.read_csv(cityfile, delimiter=';', encoding = "ISO-8859-1")

    columnReplaceAllChars(survey, 'Municipality')
    columnToInt(survey,'Zip')
    columnToInt(input_cities,'Zip')
    
    cities = survey.drop_duplicates(subset='Zip', keep='first')
    
    out_cities = pd.merge(input_cities,cities,how='outer', on=['Zip','Zip'])
    out_cities['Municipality'] = out_cities.Municipality_x.combine_first(out_cities.Municipality_y)

    csv = out_cities.to_csv(cityfile,sep=';',columns=['Zip','Municipality'],index=False)

    out.print_df(input_cities,['Zip','Municipality'],'input cities')
    out.print_df(out_cities,['Zip','Municipality'],'output cities')
    out.info_file('New cities', str(out_cities.shape[0] - input_cities.shape[0]) )
    out.info_file('writing output cities file', cityfile)



def create_block_import(file1, outputfolder):
    print('processing:(search blok) + remove columns' + file1)

    survey = pd.read_csv(file1, delimiter=';', encoding = "ISO-8859-1")
    survey_obj = survey.select_dtypes(['object'])

    survey['Block'] = survey_obj['Area Name'].apply(lambda x: x[-6:])
    
    if ((survey['Block'][0][:2]) == 'BL'):
        header = ["Area Name","Block", "LAM MK", "LU Key"]

        exportfile = outputfolder + getoutputBlockfile(file1)
        survey.to_csv(exportfile, columns = header, sep=';', index=False)

def columnToStr(df, column):
    df[column].fillna(value='NA',inplace=True)    
    df[column] = df[column].astype(str)
    return(df)

def columnToInt(df, column):
    df[column].fillna(value=0,inplace=True)    
    df[column] = df[column].astype(int)
    return(df)


def columnToInt0isEmpty(df, column):
    df[column].fillna(value=0,inplace=True)    
    df[column] = df[column].astype(int)
    df[column] = df[column].replace(0,'')
    return(df)


def columnReplaceChar(df, column, char, newchar):
    df[column] = df[column].apply(lambda s:s.replace(char, newchar))    
    return(df)

def columnReplaceAllChars(df, column):
    columnReplaceChar(df, column, "ë", "e")
    columnReplaceChar(df, column, "é", "e")
    columnReplaceChar(df, column, "'", " ")
    columnReplaceChar(df, column, "è", "e")
    columnReplaceChar(df, column, "Ã©", "e")


    return(df)


def make_import_streets_cities(importfolder,streetfile,cityfile):
    files = getimportfiles(importfolder)
    for f in files:
        make_import_streets_cities_file(f,streetfile,cityfile)

def make_import_streets_cities_file(f,streetfile,cityfile):
        make_street_names(f,streetfile)
        make_city_names(f,cityfile)



def make_import_pr(importfolder,outputfolder,streetfile,cityfile, output_to_area=False, output_versions=True):
    files = getimportfiles(importfolder)
    for f in files:
        make_import_pr_file(f,outputfolder,streetfile,cityfile, output_to_area, output_versions)

def make_import_pr_file(f,outputfolder,streetfile,cityfile, output_to_area=False, output_versions=True):
    make_survey_import(f,outputfolder,streetfile,cityfile, output_to_area)
    if output_versions == True:
        make_versions_import(f,outputfolder)




def make_import_block_pr(importfolder,outputfolder):
    files = getimportfiles(importfolder)
    for f in files:
        create_block_import(f,outputfolder)

  
#mke_import_block_pr(INPUTFOLDER,OUTPUTFOLDER)
#make_import_pr(INPUTFOLDER,OUTPUTFOLDER)


#make_import_streets_cities(INPUTFOLDER)

#make_import_pr(INPUTFOLDER,OUTPUTFOLDER)



