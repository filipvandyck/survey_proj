#!/usr/bin/env python3
#
# menu.py



import mod_map as mymap
import mod_import_coordinates as coor
import mod_validate as val
import mod_import_pr as imp
import mod_correction_import as cor

import os
import glob


MENU_WIDTH      = 80


LABEL_MAIN_MENU = '[M]ain menu'
LABEL_QUIT      = '[Q]uit'


def menu_header(header=''):
    print('\n\n')
    print('+'*MENU_WIDTH)
    print(header.center(MENU_WIDTH, ' ')) 
    print('-'*MENU_WIDTH)


def menu_footer(footer=''):
#    print('-'*MENU_WIDTH)
    print(footer.rjust(MENU_WIDTH,' '))
    print('-'*MENU_WIDTH)


def files_to_dict_all(folder, ext):
    files = [f for f in glob.glob(folder + "*." + ext)]
    i = 0

    mydict = {}

    for f in files:
        i+=1

        key = str(i)

        mydict[key] = {}

        mydict[key]['name'] = os.path.splitext(os.path.basename(f))[0]
        mydict[key]['action'] = [f]
    
    mydict['A'] = {}
    mydict['A']['name'] = 'All'
    mydict['A']['action'] = files

    return(mydict) 



def files_to_dict(folder, ext):
    files = [f for f in glob.glob(folder + "*." + ext)]
    i = 0

    mydict = {}

    for f in files:
        i+=1

        key = str(i)

        mydict[key] = {}

        mydict[key]['name'] = os.path.splitext(os.path.basename(f))[0]
        mydict[key]['action'] = f

    return(mydict) 


def select_files_from_folder_menu(folder,ext,title='',footer=""):
    menu_dict = files_to_dict_all(folder,ext)
    return(menu_from_dict(menu_dict,title,footer))

def select_file_from_folder_menu(folder,ext,title='',footer=""):
    menu_dict = files_to_dict(folder,ext)
    return(menu_from_dict(menu_dict,title,footer))

def select_geojson_file():
    mymap.convert_gml()
    geojsonfiles = select_files_from_folder_menu(mymap.GEOJSONFOLDER,'geojson','LOAD POLYGLON', mymap.GEOJSONFOLDER)
    return(geojsonfiles)

def menu_from_dict(mydict, header='',footer=''):

    if header:
        menu_header(header)


    answer_found = False
    while answer_found == False:

        for key in mydict:
            print('[' + str(key) + ']' + '\t' + str(mydict[key]['name']))    
        
        
        
        print('-'*MENU_WIDTH)
        
        if footer:
            menu_footer(footer)

        print(LABEL_MAIN_MENU + LABEL_QUIT.rjust(MENU_WIDTH - len(LABEL_MAIN_MENU),' '))
        

        print('+'*MENU_WIDTH)


        answer = input("\n :: ") 
       
        answer = answer.upper()
        
        if answer in mydict:
            action = mydict[answer]['action']
            answer_found = True
        
        if answer == 'Q':
            action = quit 
            answer_found = True

        if answer == 'M':
            action = main_menu
            answer_found = True
    
    
    ret = ''

    print('select: ' + str(action) + '\n')
    if os.path.splitext(str(action))[1] or type(action).__name__ == 'list':
        ret = action
    else:
        do = action()

    return(ret)

def main_menu():
    menu = {
            'P': {'name' : 'Plannrrr Corrections', 'action' : corrections_menu},
            'C': {'name' : 'Coordinates', 'action' : coords_menu},
            'V': {'name' : 'Validate Survey', 'action' : validate_menu},
            'I': {'name' : 'Make Import Versions / Survey', 'action' : import_menu}
    }
    action = menu_from_dict(menu,'MAIN MENU')
    if action:
        test = action()

def validate_menu():
    menu = {
            'S' : {'name' : 'Validate for Street Survey', 'action' : validate_file_street},
            'SS': {'name' : 'Validate for Site Site', 'action' : validate_file_site},
            'D' : {'name' : 'Draw coordinates', 'action' : validate_draw_coords_menu}
    }
    menu_from_dict(menu,'VALIDATE')

def validate_file_street():

    geojsonfile = select_file_from_folder_menu(mymap.GMLFOLDER,'gml','LOAD POLYGLON', mymap.GMLFOLDER)
    validatefile = select_file_from_folder_menu(val.VALIDATEFOLDER,'csv', 'VALIDATE FILE', val.VALIDATEFOLDER)
    
    if validatefile:
        val.processfile(validatefile, geojsonfile, process_for='S')

    validate_menu()

def validate_file_site():

    geojsonfile = select_file_from_folder_menu(mymap.GMLFOLDER,'gml','LOAD POLYGLON', mymap.GMLFOLDER)
    validatefile = select_file_from_folder_menu(val.VALIDATEFOLDER,'csv', 'VALIDATE FILE', val.VALIDATEFOLDER)
    
    if validatefile:
        val.processfile(validatefile, geojsonfile, process_for='SS')

    validate_menu()


def validate_draw_coords_menu():


    geojsonfiles = select_geojson_file()

  
    mapfile = select_file_from_folder_menu(val.VALIDATEFOLDER,'csv', 'DRAW MAP', val.VALIDATEFOLDER)
    if mapfile:
        mymap.draw_coordinates(mapfile,geojsonfiles,allow_change=False,option='all')
        mymap.draw_coordinates(mapfile,geojsonfiles,allow_change=False,option='sts')
        mymap.draw_coordinates(mapfile,geojsonfiles,allow_change=False,option='ssv')


    validate_menu()


def import_menu():
    impfile = select_file_from_folder_menu(imp.INPUTFOLDER,'csv','IMPORT SURVEY', imp.INPUTFOLDER)
    if impfile:
      
        imp.make_import_streets_cities_file(impfile, imp.INPUT_STREET_FILE, imp.INPUT_CITY_FILE)
 
        imp.make_import_pr_file(impfile,imp.OUTPUTFOLDER, imp.INPUT_STREET_FILE, imp.INPUT_CITY_FILE, True, True)
        
        #coor.geocode(coorfile,coor.COORDINATESFOLDER)
        
    main_menu()


def corrections_menu():
    
    ifhfile = select_file_from_folder_menu(cor.EXPORTFOLDER,'csv','IFH EXPORT SURVEY', cor.EXPORTFOLDER)
    prfile = select_file_from_folder_menu(cor.PRFOLDER,'csv','PR EXPORT CORRECTIONS', cor.PRFOLDER)
    if prfile:

        cor.writecorrections(ifhfile,prfile) 

            
    main_menu()



def coords_menu():
    menu = {
            'G': {'name' : 'Geocode', 'action' : geocode_menu},
            'C': {'name' : 'Check coordinates', 'action' : draw_coords_menu}
    }
    menu_from_dict(menu,'COORDS')


def geocode_menu():

    footer = coor.PRFOLDER
    coorfile = select_file_from_folder_menu(coor.PRFOLDER,'csv','GEOCODE', footer)
    if coorfile:
        coor.geocode(coorfile,coor.COORDINATESFOLDER)

    coords_menu()


def draw_coords_menu():

    geojsonfiles = select_geojson_file()


    footer = coor.COORDINATESFOLDER
    mapfile = select_file_from_folder_menu(coor.COORDINATESFOLDER,'csv', 'DRAW COORDINATES', footer)
    
    if mapfile:
        mymap.draw_coordinates(mapfile,geojsonfiles)

    coords_menu()

def quit():
    print('Exit menu!') 

main_menu()        
#coords_menu()








