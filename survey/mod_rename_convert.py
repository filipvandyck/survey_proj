#rename_convert.py
# file renamer and doc converter for site survey and tsa
# requires:
#	- pdfminer.six
#	- pandas
#	- chardet
#	- comtypes 1.1.7 (windows)
#       - libreoffice(linux) or word(windows)


#--------------------------------------------------------------
#imports





import sys
import os
import pandas as pd
import glob
import time
import io
import re
import subprocess
from datetime import datetime
import shutil

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter#process_pdf
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTFigure
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser

from docx2pdf import convert


windowsClient = True
try:
    import comtypes.client
except ImportError:
    windowsClient = False	



INPUTFOLDER  = os.path.dirname(os.path.realpath(__file__)) + '/documents/FFL/' 
OUTPUTFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/documents/FFL/RENAMED/'
TESTFILE     = INPUTFOLDER + 'test.pdf' 
LOGFILE      = os.path.dirname(os.path.realpath(__file__)) + '/output/' + 'LOG.csv' 

#--------------------------------------------------------------

def pdf_page_to_text(pdfname, pagenr):

    # PDFMiner boilerplate
    rsrcmgr = PDFResourceManager()
    sio = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Extract text
    fp = open(pdfname, 'rb')
    
    pages = PDFPage.get_pages(fp)
#debiel    
    p = 0
    for page in PDFPage.get_pages(fp):
        p = p + 1
        if pagenr == p :
            interpreter.process_page(page)
    
    fp.close()

    text = sio.getvalue()
    device.close()
    sio.close()

    return text

def pdf_to_text(pdfname):

    # PDFMiner boilerplate
    rsrcmgr = PDFResourceManager()
    sio = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Extract text
    fp = open(pdfname, 'rb')
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
    
    fp.close()

    # Get text from StringIO
    text = sio.getvalue()

    # Cleanup
    device.close()
    sio.close()

    return text

def parse_layout_count_figures(layout):
    tel = 0
    for lt_obj in layout:
        if isinstance(lt_obj, LTFigure):
#            parse_layout(lt_obj)  # Recursive
#            print(lt_obj.__class__.__name__)
            tel = tel + parse_figure(lt_obj)  
    return(tel)


def parse_figure(fig):
    i = 0
    for obj in fig:
        if isinstance(obj, LTFigure):
#            print(obj.__class__.__name__)
            i = i + 1
    return(i)


def pdf_find_handtekening(pdfname):
    
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    fp = open(pdfname, 'rb')

    parser = PDFParser(fp)
    doc = PDFDocument(parser)

    p = 0
    count_figs = 0
    for page in PDFP/home/filip/Python/survey_proj/survey/documents/FFLage.create_pages(doc):
        p = p + 1
        pagetext = pdf_page_to_text(pdfname,p).lower()
        if 'handtekening' in pagetext:
            interpreter.process_page(page)
            layout = device.get_result()
            count_figs = parse_layout_count_figures(layout)
    #        print('aantal fig:' + str(count_figs))     
    fp.close()
    device.close()

    if count_figs > 1 :
        return(True)
    else:
        return(False)






def windows_doc_to_pdf(doc,outputdir):
    """
    convert a doc/docx document to pdf format (windows only, requires word)
    :param doc: path to document
    """
    base=os.path.basename(doc)
    filename = os.path.splitext(base)[0]
    time.sleep(1)
    convert(doc, outputdir + filename + ".pdf")
    
    """
    wdFormatPDF = 17
    word = comtypes.client.CreateObject('Word.Application')
    word.Visible = False
    doc = word.Documents.Open(doc)
    doc.SaveAs(doc + '.pdf', FileFormat=wdFormatPDF)
    doc.Close()
    word.Quit()
    """
def linux_doc_to_pdf(doc,outputdir=INPUTFOLDER):
    """
    convert a doc/docx document to pdf format (linux only, requires libreoffice)
    :param doc: path to document
    """

    cmd = 'libreoffice --convert-to pdf'.split() + ['--outdir'] + [outputdir] + [doc]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    p.wait(timeout=10)
    stdout, stderr = p.communicate()
    if stderr:
        raise subprocess.SubprocessError(stderr)

def get_files_from_directory(directory,ext):
    files = [f for f in glob.glob(directory + "*." + ext)]
    return(files)


#--------------------------------------------------------------




def getoutputfile(importfile):
    the_file= os.path.basename(importfile)
    return(OUTPUTFOLDER + "output" + the_file)


def processFile(file1,outputfolder,logfile=LOGFILE):



#    print(text)
    print('-------------------------------------------------')
    print('processing: ' + file1)

    text = pdf_to_text(file1)
#french TSA updated test not nl
    text = " ".join(text.split())	    
    
    Q = ''
    result = re.search('Dossier\s:\s(.*)/', text)
    check  = False
    if (result != None and "MDU Technische Oplossing" in text) :
        print('TSA FOUND!!!')
        
        test = result.group(1)
        LAM = test.split('/')
        
        LAMKEY = LAM[0]
        ADR = LAM[1].split(',')
        ADRES = ADR[0] + ADR[1]
        
        zoek = test.find('Quadrant')
        if zoek > -1:
            Q = test[zoek+8:zoek+9]
        
        zoek = test.find('☒')
        if zoek > -1:
            Q = test[zoek+1:zoek+2]
        
        file_renamed = 'Doctyp_FTS-Lamkey_' + LAMKEY + '-name_' + Q

        check = True

    if (result != None and "MDU Solution Technique" in text) :
        print('FRENCH TSA FOUND!!!')

        test = result.group(1)
        LAM = test.split('/')
       
#        print(test)
#        print(LAM)
        LAMKEY = LAM[0]
        ADR = LAM[1].split(',')
        ADRES = ADR[0] + ADR[1]
#!!!!!!!NIET GETEST
        zoek = test.find('Quadrant')
        if zoek > -1:
            Q = test[zoek+8:zoek+9]
        
        zoek = test.find('☒')
        if zoek > -1:
            Q = test[zoek+1:zoek+2]
        file_renamed = 'Doctyp_FTS-Lamkey_' + LAMKEY + '-name_' + Q + 'fr'

        check = True

#   last updated test with linux
    
    result = re.search(' MDU(.*)Secundaire adressen', text)

    if (result != None and "MDU Site Survey Report" in text) :
        print('SITE SURVEY FOUND!!!')

        test = result.group(1)
        test = test.replace("MDU","")
        test = test.strip()
        ADR = test.split(' ')
        ADRES = ADR[0] + ADR[1]
        result = re.search('IFH(.*)5\.', text)
        LAM = result.group(1)
        LAM = LAM.strip()
        LAM = LAM.replace("IFH","")
        LAM = LAM.replace("Geplande","")

        LAM = LAM.split(' ')
        LAMKEY = LAM[len(LAM)-2]    

        #fucked up documents
        if LAMKEY == '':
            result = re.search('Reference(.*?)Details', text)
            LAM2 = result.group(1).strip()
            LAM2 = LAM2.split(' ')
            LAMKEY = LAM2[len(LAM2)-2]    

        zoek = text.find('Quadrant')
        if zoek > -1:
            Q = text[zoek+8:zoek+9]
        
        
        file_renamed = 'Doctyp_FIS-Lamkey_' + LAMKEY + '-name_' + Q  
        
        
        check = True 

    result = re.search('MDU(.*)Adresse\(s\) secondaire', text)
    if (result != None and "MDU Site Survey Report" in text) :
        print('FRENCH SITE SURVEY FOUND!!!')

        test = result.group(1)
        test = test.replace("MDU","")
        test = test.replace('Site Survey Report – Procès-verbal étude de siteAdresse(s)','')
        test = test.strip()
        ADR = test.split(' ')
        ADRES = ADR[0] + ADR[1]
        result = re.search('IFH(.*)5\.', text)
        LAM = result.group(1)

        LAM = LAM.strip()
        LAM = LAM.replace("IFH","")
        LAM = LAM.replace("Distribution","")

        LAM = LAM.split(' ')
        LAMKEY = LAM[len(LAM)-2]    

        #fucked up documents
        if LAMKEY == '':
            result = re.search('Reference(.*?)Details', text)
            LAM2 = result.group(1).strip()
            LAM2 = LAM2.split(' ')
            LAMKEY = LAM2[len(LAM2)-2]    

        zoek = text.find('Quadrant')
        if zoek > -1:
            Q = text[zoek+8:zoek+9]
        
        
        file_renamed = 'Doctyp_FIS-Lamkey_' + LAMKEY + '-name_' + Q + 'fr' 
        
        
        check = True 



    if check == False and "MDU Site Survey Report" in text :
        print('OLD SITE SURVEY FOUND!!!')
        text = text.replace('\n',' ')
        
        print(text)
        resultAdres = re.search('Adres(.*)1. Algemene', text)
        resultAdres = resultAdres.group(1)
        resultAdres = re.search('MDU(.*)SSRT', resultAdres)
        resultAdres = resultAdres.group(1)
        resultAdres = re.search('-(.*)\d\d\d\d', resultAdres)
        resultAdres = resultAdres.group(1)
      #  print("resultAdres:" + resultAdres)        
        Adressen = resultAdres.split(' ')
       # print(Adressen)        
        nr = Adressen[1].replace("'",'')
        ADRES = Adressen[2]+Adressen[3]+nr
        ADRES = ADRES.replace(" ",'')
                
      
        
        result = re.search('Reference(.*)Karaktergevel', text)
        result1 = result.group(1)
     #   print(result1)
        FIBERHOODS = re.search('\s(.*)\s\d+', result1)
        FIBERHOOD = FIBERHOODS.group(1)
        FIBERHOOD = FIBERHOOD.replace("-",'')
        FIBERHOOD = FIBERHOOD.replace(" ",'')
        
        result2 = re.search('\s\d\d\d+', result1)
        LAMKEY = result2.group(0)
        

        print('FIBERHOOD: ' + FIBERHOOD )

     
        file_renamed = 'Doctyp_FIS-Lamkey_' + LAMKEY + '-name_'  
        check = True

    
    if check == True:
        print('LAMKEY: ' + LAMKEY)
        print('ADRES: ' + ADRES)
        
        ADRES = ADRES.encode("ascii", "ignore")
        ADRES = ADRES.decode("utf-8").lower()
        ADRES = ADRES.replace("-","")
        ADRES = ADRES.replace("_","")
        ADRES = ADRES.replace(" ","")
        type_doc_ssv      = False
        type_doc_tsa      = False
        handtekening      = ''
        test_handtekening = False
        if "Doctyp_FIS" in file_renamed:
            type_doc_ssv = True 
        if "Doctyp_FTS" in file_renamed:
            type_doc_tsa = True
            test_handtekening = pdf_find_handtekening(file1)    
            if test_handtekening == True:
                handtekening = 'OK'    
 

        logs_append(logfile,LAMKEY,ADRES,type_doc_tsa,type_doc_ssv,test_handtekening)

        ADRES_N = ADRES[0:25]
        file_renamed = file_renamed + ADRES_N
        print('FILENAME (new): ' + file_renamed)
 
        if os.path.exists(outputfolder + file_renamed + '.pdf'):
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            file_renamed = file_renamed + '_' + str(timestamp)
        
        os.rename(file1, outputfolder + file_renamed + handtekening + '.pdf')

        print('file created:' + file_renamed)

    if check == False:
   
        print('NO DOCUMENT FOUND' + file1)



def logs_clear(logfile):
    log = pd.DataFrame(columns=['LAMKEY','ADRES','TSA','SSV','HANDTEKENING'])
    log.to_csv(logfile,sep=';',index=False)
    

def logs_append(logfile,LAMKEY,ADRES,type_doc_tsa,type_doc_ssv,handtekening):   
    log = pd.read_csv(logfile, delimiter=';', encoding = "ISO-8859-1")
    log = log.append({'LAMKEY' : LAMKEY , 'ADRES' : ADRES, 'TSA' : type_doc_tsa, 'SSV' : type_doc_ssv, 'HANDTEKENING' : handtekening } , ignore_index=True)
    log.to_csv(logfile,sep=';',index=False)
       
 


def convert_doc_to_pdf_from_directory(directory,outputdir): 
    docfiles = get_files_from_directory(directory,"docx")

    # convert doc to pdf files
    for f in docfiles:
        print(f + " to pdf " + " is windows client: " + str(windowsClient))	
        if windowsClient == True:
            
             windows_doc_to_pdf(f,outputdir)
          
             
        else:
             linux_doc_to_pdf(f,outputdir)		
    return(docfiles)
"""
convert_doc_to_pdf_from_directory(INPUTFOLDER)
"""

def rename_pdf_TSA_or_SSV_from_directory(directory,outputfolder,logfile=LOGFILE):
    pdffiles = get_files_from_directory(directory,"pdf")

    # rename the pdf files
    for f in pdffiles:
        
        try:
            processFile(f,outputfolder,logfile)
        except:
           print('TSA or SSV rename exception')
    return(pdffiles)


#test

def rename_pdf_facade():
    pdffiles = get_files_from_directory(INPUTFOLDER,"pdf")

    document_counter = 1
    for f in pdffiles:
        text = pdf_to_text(f)


        position_start = text.find(":")
    

        position_start = text.find(":",position_start+2,len(text)-position_start)+2


        text = text[position_start:len(text)]
        text = text.lstrip()
        #print(text)

        position_end = text.find("\n") 

        LAMKEY = text[0:position_end]


        #print(position_start)
        #print(position_end)
        print("Lamkey:" + LAMKEY)

        Prefix = "Doctyp_FFL-Lamkey_"


        new_filename = Prefix + LAMKEY + "_" + str(document_counter) + '.pdf'

        print("Rename file: \t" + f + "\nto: \t\t" + new_filename)

        os.rename(f, OUTPUTFOLDER + new_filename)


        document_counter += 1

#rename_pdf_TSA_or_SSV_from_directory('/home/filip/Python/survey/download/Evere_Documents/UNPROCESSED/','/home/filip/Python/survey/download/Evere_Documents

