#!/usr/bin/env python3
#
# mod_check_documents.py
# example file : Doctyp_FIS-Lamkey_2766157-name_BG dUrslaan 24 S d Mercxstr 29.pdf


import mod_rename_convert as ren
import mod_facade_letter as fac

import glob
import os
import re






def replace_bad_chars(s):
    s = re.sub("ë", "e", s)
    s = re.sub("é", "e", s)
    s = re.sub("'", "", s)
    s = re.sub("è", "e", s)
    s = re.sub("Ã©", "e", s)
    s = re.sub(":", "", s)
    s = re.sub("\.", "", s)
    s = re.sub("\ -", "", s)
    s = re.sub("\-", "", s)
    s = re.sub("_", "", s)
    return(s)




def check_document_name(theFile, prefix_to_check,FOLDER_TO_WRITE,FOLDER_TO_CHECK):


    checkfile = os.path.basename(theFile)

    print('File to check:')
    print(checkfile)

    file_is_valid = True


    middle_to_check = "-name_"

    length_prefix = len(prefix_to_check)

    #print(checkfile[:length_prefix]) 

    if (checkfile[:length_prefix] == prefix_to_check) :
        pass
    #    print("Prefix OK")
    else:
        message = "Prefix NOK :: should be :: " + prefix_to_check 
        print(message)
        file_is_valid = False

    find_middle = checkfile.find(middle_to_check)
    length_middle = len(middle_to_check)

    if (find_middle != -1) : 
    #    print("Middle OK")
        pass
    else:
        message = "Middle NOK :: should be :: " + middle_to_check 
        print(message)
        file_is_valid = False

    Lamkey = checkfile[length_prefix:find_middle]
#    print(Lamkey)

    if (Lamkey.isdigit() == True) : 
    #    print("Lamkey OK")
        pass
    else:
        message = "Lamkey NOK :: should be a number :: " + Lamkey 
        print(message)

        file_is_valid = False



    if file_is_valid==True :

        name = checkfile[find_middle+length_middle:-4]

        name = replace_bad_chars(name)

        name_last_part = name[name.rfind(" ")+1:]

        new_name = name
        if len(name) > 25 :
            if(len(name_last_part) < 5):
                new_name = new_name[0:20] + name_last_part
            else:
                new_name = new_name[0:25]



        print("Original file:")
        print(theFile)

        new_name = checkfile[0:find_middle+length_middle] + new_name + ".pdf"
        print("Renamed file: ")
        new_file = os.path.join(FOLDER_TO_WRITE,new_name)
        print(new_file)

        orig_file = os.path.join(FOLDER_TO_CHECK,theFile)

        os.rename(orig_file,new_file)



def check_dir():


    FOLDER_TO_CHECK = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'documents/')


    print('Document FIS / FIS checker + renamer')    
    print('[I] = FIS')    
    print('[T] = FTS')    
    print('[F] = FFL')    
    print('[B] = Make FFL From IFH')    
    print('[M] = FMH')

    answer = input("\n :: ") 
    answer = answer.upper()

    folder = ''

    if(answer== 'I') :
        folder = 'FIS/'
        prefix_to_check = "Doctyp_FIS-Lamkey_" 

    if(answer== 'T') :
        folder = 'FTS/'
        prefix_to_check = "Doctyp_FTS-Lamkey_" 

    if(answer== 'M') : 
        folder = 'FMH/'

        prefix_to_check = "Doctyp_FMH-Lamkey_" 

    if(answer== 'F') :
        ren.rename_pdf_facade()

    if(answer== 'B') :
        folder = 'FFL/'
        
        prefix_to_check = "Doctyp_FFL-Lamkey_" 
        

        print('Select Language of the letter')
        print('[F] = FR')    
        print('[ANY] = NL')    
        answer = input("\n :: ") 
        answer = answer.upper()

        print(fac.INPUTFOLDER + fac.INPUT_SURVEY)

        if answer == 'F':
            fac.process_facade_letter(fac.INPUTFOLDER + fac.INPUT_SURVEY, fac.INPUTFOLDER + fac.INPUT_FACADE_LETTER_FR)
          
        else:    
            fac.process_facade_letter(fac.INPUTFOLDER + fac.INPUT_SURVEY, fac.INPUTFOLDER + fac.INPUT_FACADE_LETTER)

        
        
        PDF_TO_CHECK = os.path.join(FOLDER_TO_CHECK, folder)
        ren.convert_doc_to_pdf_from_directory(fac.OUTPUTFOLDER,PDF_TO_CHECK)

    if folder != '':
        FOLDER_TO_CHECK = os.path.join(FOLDER_TO_CHECK, folder)
        FOLDER_TO_WRITE = os.path.join(FOLDER_TO_CHECK, 'RENAMED/')

        print('selected folder :: ' + FOLDER_TO_CHECK)
        print('prefix to check :: ' + prefix_to_check)


        if not os.path.exists(FOLDER_TO_WRITE):
            os.makedirs(FOLDER_TO_WRITE)



        lstFiles = glob.glob(FOLDER_TO_CHECK + '*.pdf')


        for theFile in lstFiles:
            check_document_name(theFile,prefix_to_check,FOLDER_TO_WRITE,FOLDER_TO_CHECK)

######## BODY
#check_dir()
