#!/usr/bin/env pythoni3
#
# mod_sns_chart.py
import os
import pandas as pd
import plotly.express as px
import glob
import fileinput
import datetime

SNSFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/documents/SNS/'
HTMLFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/documents/SNS/html/'
SITEFOLDER = os.path.dirname(os.path.realpath(__file__)) + '/documents/SNS/html/site/'
EXPORT_FILE = SNSFOLDER + 'report.csv'

REPORT_FIS_SDU     = SNSFOLDER + 'report_fis_sdu.csv'
REPORT_FIS_MISSING = SNSFOLDER + 'report_fis_mdu_missing.csv'
REPORT_FIS         = SNSFOLDER + 'report_fis.csv'


TOP_HTML    = SITEFOLDER + 'top.html'
NAV_HTML    = SITEFOLDER + 'navigation.html'



def make_site():

    with open(TOP_HTML, 'r') as myfile:
        top = myfile.read()  


    print('report csv to html bar charts')

    #report csv to html bar charts
    df = pd.read_csv(EXPORT_FILE, delimiter=';', encoding = "ISO-8859-1")
    df = df[df['ZONE_NAME'].str[0]=='W']
    df['ZONE_NAME'] = df['ZONE_NAME'].str[6:]
    df = df.sort_values(by=['ZONE_NAME'])
    df = df.rename(columns={"BUILDINGS_TOTAL": "BUILDINGS", "MDU_TOTAL": "MDU", "SDU_TOTAL": "SDU", "UNITS_TOTAL": "UNITS", "MDU_SSV": "SSV"})



    def set_fig(df,title='',yaxis=''):
        fig = px.bar(df, x='ZONE_NAME', y=yaxis, color=yaxis, title=title)
        fig.update_traces(textposition='outside')
        fig.update_xaxes(tickangle=45, tickfont=dict(size=8))
        fig.update_layout(yaxis=dict(range=[0,100]),xaxis_title='',yaxis_title='')
        return(fig)


    fig_sts = set_fig(df,yaxis='STS_PROCENT',title='Street surveys all fiberhoods')
    #fig_sts.show()


    df_sts_progress = df[df['STS_PROCENT']>0]
    df_sts_progress = df_sts_progress[df_sts_progress['STS_PROCENT']<100]

    fig_sts_progress = set_fig(df_sts_progress, yaxis='STS_PROCENT', title='Street surveys in progress')
    #fig_sts_progress.show()

    fig_ssv = set_fig(df, yaxis='SSV_PROCENT', title='Site surveys all fiberhoods')
    #fig_ssv.show()

    df_ssv_progress = df[df['SSV_PROCENT']>0]
    df_ssv_progress = df_ssv_progress[df_ssv_progress['SSV_PROCENT']<100]

    fig_ssv_progress = set_fig(df_ssv_progress, yaxis='SSV_PROCENT', title='Site surveys in progress')
    #fig_ssv_progress.show()


    fig_fis = set_fig(df, yaxis='FIS_PROCENT', title='SNS FIS all fiberhoods')
    #fig_fis.show()



    fig_sts.write_html(HTMLFOLDER + "chart_sts.html")
    fig_sts_progress.write_html(HTMLFOLDER + "chart_sts_progress.html")
    fig_ssv_progress.write_html(HTMLFOLDER + "chart_ssv_progress.html")
    fig_ssv.write_html(HTMLFOLDER + "chart_ssv.html")
    fig_fis.write_html(HTMLFOLDER + "chart_fis.html")

    file_list = glob.glob(HTMLFOLDER + "*.html")

    with open(SNSFOLDER + 'result_progress.html', 'w') as file:
        input_lines = fileinput.input(file_list)
        file.writelines(input_lines)

    print('report fis csv to html file')
    #reports fis csv to html file 
    df_report_fis_missing = pd.read_csv(REPORT_FIS_MISSING, delimiter=';', encoding = "ISO-8859-1")

    table = "<H1>MDU with missing fis</H1>" + df_report_fis_missing.to_html()

    with open(HTMLFOLDER + "fis_mdu_missing.html", "w") as text_file:
        text_file.write(table)


    df_report_fis_sdu = pd.read_csv(REPORT_FIS_SDU, delimiter=';', encoding = "ISO-8859-1")
    table = "<H1>SDU with fis</H1>" + df_report_fis_sdu.to_html()

    with open(HTMLFOLDER + "fis_sdu.html", "w") as text_file:
        text_file.write(table)
    
    print(df)    
    df_fis_report = df[['ZONE_NAME','BUILDINGS','MDU','SDU','FIS_MDU','FIS_SDU','FIS_PROCENT','FTS_TOTAL','FTS','FTS_PROCENT']]

    fis_report_html = df_fis_report.to_html()

    with open(HTMLFOLDER + "fis_report.html", "w") as text_file:
        text_file.write(fis_report_html)
  

    df_survey_report = df[['ZONE_NAME','BUILDINGS','MDU','SDU','UNITS','STS','STS_TODO','STS_PROCENT','SSV','SSV_TODO','SSV_PROCENT']]

    survey_report_html = df_survey_report.to_html()

    with open(HTMLFOLDER + "survey_report.html", "w") as text_file:
        text_file.write(survey_report_html)
  






    print('export to site html')
    file_list = glob.glob(HTMLFOLDER + "*.html")

    links = ''
    for f in file_list:
        base = os.path.basename(f)
        the_file = os.path.splitext(base)[0]
        site_file = the_file + '.html'

        links = links + '[<a href="'+site_file+'">'+the_file+'</a>]'

    the_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    links = links + '(' + the_time + ')'

    for f in file_list:
        with open(f, 'r') as myfile:
            data = myfile.read()  


        base=os.path.basename(f)
        the_file = os.path.splitext(base)[0]
        site_file = SITEFOLDER+the_file + '.html'
    
        site_html = top + links + data

        with open(site_file, "w") as text_file:
            text_file.write(site_html)



#make_site()
