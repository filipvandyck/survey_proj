#!/usr/bin/env python3
#
# mod_correction_import.py


import glob
import os, shutil
import mod_import_pr_fr as import_pr_fr
import pandas as pd
import datetime

import myoutput as out

CORRECTIONSFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/corrections/' 
EXPORTFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/corrections/export/' 
IFHFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/corrections/export/ifh/' 
IFHBACKUPFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/corrections/export/ifh/backup/' 
PRFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/corrections/pr/' 

ENCODING = 'ansi'



#INPUT_STREET_FILE = os.path.dirname(os.path.realpath(__file__)) + '/exports/streets/streets.csv' 
#INPUT_CITY_FILE = os.path.dirname(os.path.realpath(__file__)) + '/exports/streets/cities.csv' 



def writecsvcorrection(df,df_ifh,importnaam):
    f_begin = df_ifh['Area Name'][0] + '-'

    d = datetime.date.today()
    f_end = '-' + str(d.year) + '%02d' % d.month + '%02d' % d.day + '.csv'

    filename = CORRECTIONSFOLDER + f_begin + importnaam + f_end

    csv = df.to_csv(filename,sep=';',index=False, encoding = ENCODING)
    out.info_file('import csv written',filename)



def getcsvfile(directory):
     files = [f for f in glob.glob(directory + "*.csv")]
     if len(files) > 0 :
         return(files[0])
     else:
         print('no csv file found in: ' + directory)
         return(0)

def writecorrections(exportfile, prfile):
    global ENCODING
    
    out.info_file('Processing for corrections',exportfile)
    #import_pr.make_import_streets_cities(INPUTFOLDER, INPUT_STREET_FILE, INPUT_CITY_FILE)
    import_pr_fr.make_import_pr_file(exportfile,IFHFOLDER, import_pr_fr.INPUT_STREET_FILE_FR, import_pr_fr.INPUT_CITY_FILE_FR, False, False)

    ifhfile = getcsvfile(IFHFOLDER)
    out.info_file('Reading ifh file',ifhfile)

#    prfile = getcsvfile(PRFOLDER)
#    out.info_file('Reading PR file',prfile)


    df_ifh = pd.read_csv(ifhfile, delimiter=';', encoding = ENCODING, keep_default_na=False)
    df_pr = pd.read_csv(prfile, delimiter=',', encoding = ENCODING, keep_default_na=False)

    df_ifh = df_ifh.applymap(str)
    df_pr = df_pr.applymap(str)

    df_ifh['adres'] = df_ifh['Street'] + df_ifh['Nr'] + df_ifh['Suffix']
    df_pr['adres'] = df_pr['Straat'] + df_pr['Huisnummer'] + df_pr['Huisnummer Toevoeging']

    #columnToStr(df_ifh,'LU Key')
    #OpdrachtID,Projectnummer,Opdrachttemplate,Opdrachtnummer,"Opdrachtnummer extern",Straat,Huisnummer,"Huisnummer Toevoeging","SSV Action","SSV Action LU",Nature,"Building exists"

    df_pr_buildings = df_pr[df_pr['Opdrachttemplate']=='BUILDING template']
    df_pr_units = df_pr[df_pr['Opdrachttemplate']=='(L/B/S)U template']
    df_pr_nb = df_pr_buildings[df_pr_buildings['Opdrachtnummer'].str.contains('NB')]

    out.menu_header('CORRECTIONS LU')

    s_pr = set(df_pr_units['Opdrachtnummer'].unique())
    s_ifh = set(df_ifh['LU Key'].unique())
 
    s_missing_lu = s_ifh.difference(s_pr)
    df_pr_missing_lu = df_ifh[df_ifh['LU Key'].isin(s_missing_lu)]

    out.print_df(df_pr_missing_lu,i='LU in IFH not in PR : import street survey unit')


    s_delete_lu = s_pr.difference(s_ifh)
    df_delete_lu = pd.DataFrame(list(s_delete_lu),columns=['LU_Key'])
    df_pr_delete_lu = df_delete_lu.assign(SSV_Action_LU='DELETE')


    out.print_df(df_pr_delete_lu ,i='LU in PR not in IFH : import delete LU set SSV Acton LU as Delete')



    df_corrections_lu = pd.concat([df_pr_missing_lu, df_pr_delete_lu], join='outer', axis=1)
    df_corrections_lu = df_corrections_lu.fillna('')
    #print(df_corrections_lu)





    out.menu_header('CORRECTIONS BUILDINGS')

    s_pr = set(df_pr_buildings['Opdrachtnummer'].unique())
    s_ifh = set(df_ifh['LAM MK'].unique())
    s_missing_lam = s_ifh.difference(s_pr)

    df_pr_missing = df_ifh[df_ifh['LAM MK'].isin(s_missing_lam)]
    df_pr_missing_lam = df_pr_missing.drop_duplicates(subset='LAM MK', keep='first')



    #als key in missing lam pr en tussen nb lijst pr -> key lam ifh wegschrijven in pr 

    df_pr_nb = df_pr_nb[['Opdrachtnummer','adres']]
    df_pr_nb_change = pd.concat([df_pr_missing_lam.set_index('adres'), df_pr_nb.set_index('adres')], join='inner', axis=1)


    df_pr_nb_change = df_pr_nb_change[['Opdrachtnummer','LAM MK']] 
    out.print_df(df_pr_nb_change ,i='New buildings in IFH as NB in PR: import NB to change keys')



    df_pr_nb_new = df_pr_missing_lam[~df_pr_missing_lam['adres'].isin(df_pr_nb_change.index)]
    out.print_df(df_pr_nb_new,i='ew buildings in ifh not in pr: import buildings street survey') 

    #buildings in PR not in IFH

    s_delete_opdrachtnummer = s_pr.difference(s_ifh)
    df_delete_opdrachtnummer = pd.DataFrame(list(s_delete_opdrachtnummer),columns=['LAM_MK'])

    #remove nb's accepted in ifh
    df_delete_opdrachtnummer = df_delete_opdrachtnummer[~df_delete_opdrachtnummer['LAM_MK'].isin(df_pr_nb_change['Opdrachtnummer'])]

    df_pr_delete_opdrachtnummer = df_delete_opdrachtnummer.assign(SSV_Action='DELETE')


    out.print_df(df_pr_delete_opdrachtnummer,i='Buildings in PR not in IFH: import delete buildings set SSV Action on DELETE')


    '''
    writecsvcorrection(df_pr_delete_lu,df_ifh,'delete_lu')
    writecsvcorrection(df_pr_nb_change,df_ifh,'change_nb_lam')
    writecsvcorrection(df_pr_delete_opdrachtnummer,df_ifh,'delete_lam')
    '''

    # make one correction file for corrections to do PR

    df_corrections = pd.concat([df_pr_delete_opdrachtnummer, df_pr_delete_lu], join='outer', axis=1)

    df_pr_nb_change = df_pr_nb_change.reset_index()
    df_corrections['Opdrachtnummer'] = df_pr_nb_change['Opdrachtnummer']
    df_corrections['LAM MK'] = df_pr_nb_change['LAM MK']


    pf_corrections = df_corrections.fillna('')
    out.print_df(df_corrections,i='Corrections todo in Planrrr')



    writecsvcorrection(df_pr_missing_lu,df_ifh,'missing_lu')
    writecsvcorrection(df_pr_nb_new,df_ifh,'missing_lam')
    writecsvcorrection(df_corrections,df_ifh,'corrections_todo_pr')



    files = [f for f in glob.glob(IFHFOLDER + "*.csv")]
    for f in files:
        out.info_file('Move IFH file to backup',f)
        shutil.move(f,os.path.join(IFHBACKUPFOLDER, os.path.basename(f)))






