#!/usr/bin/env python3
#
# mod_import_coordinates.py


import glob
import os, shutil
import pandas as pd
import datetime
import time
import requests

import mod_map as map

PRFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/coordinates/pr/' 
COORDINATESFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/coordinates/' 

class Geopunt:

    #REQUEST_URL = 'https://loc.geopunt.be/v4/location?&q=kleerroos&c=1'
    REQUEST_URL = 'https://loc.geopunt.be/v4/location'
    xPos = ''
    ypos = ''

    def search(self,adres):
        parameter = {"q":adres,"c":"1"}
        request = requests.get(self.REQUEST_URL,parameter)

        '''
{'LocationResult': [{'Municipality': 'Herentals', 'Zipcode': '2200', 'Thoroughfarename': 'Kleerroos', 'Housenumber': '89', 'ID': 1105227, 'FormattedAddress': 'Kleerroos 89, 2200 Herentals', 'Location': {'Lat_WGS84': 51.17220987413536, 'Lon_WGS84': 4.844441071620486, 'X_Lambert72': 183268.23, 'Y_Lambert72': 207018.23}, 'LocationType': 'crab_huisnummer_afgeleidVanGebouw', 'BoundingBox': {'LowerLeft': {'Lat_WGS84': 51.17220987413536, 'Lon_WGS84': 4.844441071620486, 'X_Lambert72': 183268.23, 'Y_Lambert72': 207018.23}, 'UpperRight': {'Lat_WGS84': 51.17220987413536, 'Lon_WGS84': 4.844441071620486, 'X_Lambert72': 183268.23, 'Y_Lambert72': 207018.23}}}]}
        '''
        
        if request.status_code == 200:
         
            data = request.json()
            if(len(data['LocationResult'])>0): 
                xPos = str(data['LocationResult'][0]['Location']['X_Lambert72'])
                yPos = str(data['LocationResult'][0]['Location']['Y_Lambert72'])
                self.xPos = xPos.replace('.',',')
                self.yPos = yPos.replace('.',',')
            else:
                self.xPos = ''
                self.yPos = ''


def writecsv(df,importnaam,folder):
    f_begin = df['Projectnummer'][0] + '-'

    d = datetime.date.today()
    f_end = '-' + str(d.year) + '%02d' % d.month + '%02d' % d.day + '.csv'

    filename = folder + f_begin + importnaam + f_end

    csv = df.to_csv(filename,sep=';',index=False)
    print('import csv written :: '+ filename)



def getcsvfile(directory):
     files = [f for f in glob.glob(directory + "*.csv")]
     if len(files) > 0 :
         return(files[0])
     else:
         print('no csv file found in: ' + directory)
         return(0)


def menu():

    print('Geocode CSV file')

    answer = 'n'
    while answer == 'N' or answer == 'n' :  
        prfile = getcsvfile(PRFOLDER)
        print('reading PR file in folder :: ' + COORDINATESFOLDER)
        if not prfile: 
            retry = input('place csv in folder :: press any key')
            answer = n
        else:
            answer = input('loading... ' + prfile + '\n[Y] :: continue \n[N] :: reload\n')

    geocode(prfile,COORDINATESFOLDER)




def geocode(f,outputfolder):

    df_pr = pd.read_csv(f, delimiter=',', encoding = "ISO-8859-1", keep_default_na=False)
    df_pr = df_pr.applymap(str)
    print(df_pr)

    geo = Geopunt()





    # Straat  Huisnummer Huisnummer Toevoeging  Postcode        Plaats 
    df_pr['Adres'] = df_pr['Straat'] + ' ' + df_pr['Huisnummer'] + ' '+ df_pr['Huisnummer Toevoeging'] + ' ' + df_pr['Postcode'] + ' ' + df_pr['Plaats']
    df_pr['Adres'] = df_pr['Adres'].str.replace('  ',' ')
    for index, row in df_pr.iterrows():
        adres = row['Adres']
        print('geocode adres: ' + adres)
        geo.search(adres)
        while (adres != 'q' and geo.xPos == ''):
            adres = input('adres not found please retry (q to quit)::> ')
            geo.search(adres)
            print(adres != 'q' and geo.xPos == '') 
        
    
        print('xy found :: ' + geo.xPos + ',' + geo.yPos)

        df_pr.at[index,'xPos'] = geo.xPos
        df_pr.at[index,'yPos'] = geo.yPos

        time.sleep(0.5)


    print(df_pr)

    writecsv(df_pr,'coordinaten_pr', outputfolder)

   
#menu()
