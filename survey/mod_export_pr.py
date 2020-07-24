#mod_export_pr.py

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import geckodriver_autoinstaller
geckodriver_autoinstaller.install() 

options = Options()
options.headless = True



print("starting webdriver")

USERNAME = "filip.vandyck@fifthnet.eu"
PASSWORD = "Telenet1"

driver = webdriver.Firefox(options=options)
#driver = webdriver.Firefox(options=options,executable_path='/home/filip/Tools/survey_proj/survey/selenium/geckodriver')

print("loading opdrachten")
#driver.get("https://"+USERNAME+":"+PASSWORD + "@fifthnet.connectsoftware.nl/tfc/views/opdrachten/opdrachten.php")
driver.get("https://"+USERNAME+":"+PASSWORD + "@fifthnet.connectsoftware.nl/tfc/views/opdrachten/connectors/grid2csv.php")


print("loading export")
#<div class="dhxtoolbar_text">Acties</div>
#<div class="btn_sel_text">csv export</div>
#driver.find_element(By.XPATH, "//div[text()='csv export']").click()



#driver.get("https://fifthnet.connectsoftware.nl/tfc/views/opdrachten/connectors/grid2xlsx.php")

src = driver.page_source

print(src)

driver.quit()
