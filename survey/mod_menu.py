#!/usr/bin/env python3
#
#mod_ menu.py




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


