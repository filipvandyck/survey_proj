#!/usr/bin/env python3
#my_output.py

import pandas as pd

MENU_WIDTH      = 80

pd.set_option('display.max_rows', None)


def menu_header(header=''):
    print('\n\n')
    print('+'*MENU_WIDTH)
    print(header.center(MENU_WIDTH, ' '))
    print('-'*MENU_WIDTH)
 

def info_file(i,f):

    print(i)
    print('-'*MENU_WIDTH)
    print(f)
    print('\n')


def print_df(df, columns='', i=''):
    
    print(i)
    print(':'*MENU_WIDTH)
    
    if columns: 
        print(df[columns])
    else:
        print(df)

    print('\n')

def print_s(s, i=''):
    
    print(i)
    print(':'*MENU_WIDTH)
    teller = 1
    for item in s:
        print(str(teller) + '.\t' + item)
        teller = teller + 1
    print('\n')


def columnToInt(df, column):
    df[column].fillna(value=0,inplace=True)    
    df[column] = df[column].astype(int)
    return(df)
