import mod_export_pr as exp 
import mod_sns as sns


f = exp.get_export_pr()
print("export written: " + f)

sns.make_sns_report()
