#mod_export_pr.py

from selenium import webdriver
import os
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import geckodriver_autoinstaller
import time
import glob
import shutil

geckodriver_autoinstaller.install() 

OUTPUT_FOLDER      = os.path.dirname(os.path.realpath(__file__)) + '/selenium/download/'
OUTPUT_BACK_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/selenium/download/backup/'




def get_export_pr():

    files = glob.glob(OUTPUT_FOLDER + "*.csv")

    for f in files:
        shutil.move(f, OUTPUT_BACK_FOLDER + 'export_back.csv')



    # webdriver firefox options
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.binary = "/usr/bin/firefox-esr"
    
    caps = DesiredCapabilities.FIREFOX.copy()
    caps['marionette'] = True

    print('setting firefox profile download dir:')
    print(OUTPUT_FOLDER)

    # webdriver firefox profile
    fp = webdriver.FirefoxProfile()
    fp.set_preference('browser.download.folderList', 2)
    fp.set_preference('browser.download.manager.showWhenStarting', False)
    fp.set_preference('browser.download.dir', OUTPUT_FOLDER)
    fp.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document, text/plain, application/pdf, application/vnd.ms-excel, text/csv, text/comma-separated-values, application/octet-stream, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
     #----
    print("starting webdriver")

    USERNAME = "filip.vandyck@fifthnet.eu"
    PASSWORD = "Telenet1"

    driver = webdriver.Firefox(options=options,capabilities=caps, firefox_profile=fp)
    #driver = webdriver.Firefox(options=options,firefox_profile=fp)
    #driver = webdriver.Firefox(options=options,executable_path='/home/filip/Tools/survey_proj/survey/selenium/geckodriver')

    print("loading opdrachten - get export")
    driver.get("https://"+USERNAME+":"+PASSWORD + "@fifthnet.connectsoftware.nl/tfc/views/opdrachten/opdrachten.php?dhxr1595860703450=1")

    time.sleep(25)
    URL_PR_EXPORT = "https://"+USERNAME+":"+PASSWORD + "@fifthnet.connectsoftware.nl/tfc/views/opdrachten/connectors/grid2csv.php"

    #driver2.get(URL_PR_EXPORT)


    driver.execute_script('''window.open("''' + URL_PR_EXPORT + '''","width=350,height=250");''')
    #driver.execute_script('''window.open("''' + URL_PR_EXPORT + '''","_blank");''')

    #wait for export to finish
    time.sleep(55)


    files = glob.glob(OUTPUT_FOLDER + "*.csv")
    
    if files:
        return files[0]
    else:
        print("something went wrong...: " )

    driver.quit()
#f = get_export_pr()
#print("export written: " + f)


