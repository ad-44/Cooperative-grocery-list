'''
Functions pour l'appli de liste de course !
Date : 2026/07/06    
'''

#%% Imports
import pandas as pd
import numpy as np
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials


#%% Access google sheet
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def get_spreadsheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp-service-account"],
        scopes=SCOPES,
    )

    client = gspread.authorize(creds)
    
    return client.open_by_url("https://docs.google.com/spreadsheets/d/12HSo_myjERC3GOc8q9BkB8OiRFQLqsOF5hFCN02l4z0/edit?pli=1&gid=0#gid=0")

spreadsheet = get_spreadsheet()

#%% Google sheet functions

#Common functions
@st.cach_data(ttl=30)
def get_worksheets_name():
    names = [ws.title for ws in spreadsheet.worksheets()]
    return names

@st_cach_data(ttl=30)
def get_recipes(ws):
    sheet = spreadsheet.worksheet(str(ws))
    if sheet.acell("A1").value != None :
        list = sheet.get_all_values()
    else :
        list = []

    return list

def update_chart(chart,ws):
    sheet = spreadsheet.worksheet(str(ws))
    list = chart.to_numpy().tolist()
    sheet.clear()
    sheet.update("A1",list)
    return

@st.cach_data(ttl=30)
def read_and_merge(sheet_type:str, columns):
    ws_title = get_worksheets_name()
    
    dfs = pd.DataFrame()

    for ws in spreadsheet.worksheets():
        if sheet_type not in ws.title:
            continue

        values = ws.get_all_values()

        if len(values) == 1 and len(values[0])==0:
            continue
        
        df = pd.DataFrame(values,columns=columns)    
        name = ws.title.split("_")[0]
        df['Personne'] = name
        dfs = pd.concat([dfs,df], ignore_index=True)

    return dfs

def aggregate_lists(df):
    df["Ingrédients"] = (df["Ingrédients"]
        .str.strip()
        .str.lower()
        )
        
    df["Unité de mesure"] = (
        df["Unité de mesure"]
        .fillna("")
        .str.strip()
    )

    df["Quantité"] = pd.to_numeric(
        df["Quantité"],
        errors="coerce"
    )

    final_df = (
        df.groupby(["Ingrédients", "Unité de mesure"], as_index=False)
        .agg(
            Quantité = ("Quantité", "sum"),
            Personne = ("Personne", lambda x: ", ".join(sorted(set(x))))
        )
    )

    return final_df

def aggregate_list_2(df):
    df["Ingrédients"] = (df["Ingrédients"]
        .str.strip()
        .str.lower()
        )
    
    final_df = (
        df.groupby(["Ingrédients"], as_index=False)
        .agg(
            Personne = ("Personne", lambda x: ", ".join(sorted(set(x))))
        )
    )

    return final_df
        
def aggregate_list_3(df):
    df["Objets"] = (df["Objets"]
        .str.strip()
        .str.lower()
        )
    
    final_df = (
        df.groupby(["Objets"], as_index=False)
        .agg(
            Personne = ("Personne", lambda x: ", ".join(sorted(set(x))))
        )
    )

    return final_df

#Sheet with names + recipes
def save_recipes(name, recipe):
    sheet = spreadsheet.worksheet("Recipes")
    if sheet.acell("A1").value != None :
        list = sheet.get_all_values()
    else :
        list = []

    if len(list) != 0 :
        for item in list:
            if str(name) in item:
                index = list.index(item)
                list[index] = [name,recipe]
            else :
                list.append([name,recipe])
    else :
        list.append([name,recipe])
             
    sheet.clear()
    sheet.update("A1",list)
    return

  
#Sheet for every person recipe

def save_ingredients(name,df,ingredient_kind):
    ws_names = get_worksheets_name()

    if str(name)+"_"+str(ingredient_kind) in ws_names :
        sheet = spreadsheet.worksheet(str(name)+"_"+str(ingredient_kind))
    else :
        sheet = spreadsheet.add_worksheet(title=str(name)+"_"+str(ingredient_kind), rows=100, cols=10)

    if sheet.acell("A1").value != None :
        list = sheet.get_all_values()
        list.extend(df.to_numpy().tolist())
    else:
        list = df.to_numpy().tolist()

    sheet.clear()
    sheet.update("A1",list)
    return



    
