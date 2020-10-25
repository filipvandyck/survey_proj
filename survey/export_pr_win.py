import mod_export_pr as exp 
import mod_sns as sns

f = exp.get_export_pr(HEADLESS = False, PREFERENCE_DRIVER = True)
if f:
    print("export written: " + f)
if f!=0:
    sns.make_sns_report()
else:
    print("fault in creating export. again...")
