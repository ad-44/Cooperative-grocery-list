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
@st.cache_data(ttl=30)
def get_worksheets_name():
    names = [ws.title.strip().lower() for ws in spreadsheet.worksheets()]
    return names

@st.cache_data(ttl=30)
def get_recipes(ws):
    sheet = spreadsheet.worksheet(str(ws))
    if sheet.acell("A1").value != None :
        list = sheet.get_all_values()
    else :
        list = []

    return list

@st.cache_data(ttl=30)
def read_final_main_df():
    sheet = spreadsheet.worksheet("Final_df")

    values = sheet.get("A:D")

    if not values or values == [[]]:
        
        main = pd.DataFrame(
            columns=["Ingrédients","Quantités","Unité de mesure","Personne"]
        )

    else:

        main = pd.DataFrame(
            values,
            columns = ["Ingrédients","Quantités","Unité de mesure","Personne"]
        )

    return main

@st.cache_data(ttl=30)
def read_final_apero_df():
    sheet = spreadsheet.worksheet("Final_df")

    values = sheet.get("F:G")

    if not values or values == [[]]:
        main = pd.DataFrame(
            columns=["Articles","Personne"]
        )
        
    else:   
        main = pd.DataFrame(
            sheet.get("F:G"),
            columns=["Articles","Personne"]
        )

    return main

@st.cache_data(ttl=30)
def read_final_objects_df():
    sheet = spreadsheet.worksheet("Final_df")

    values = sheet.get("I:J")

    if not values or values == [[]]:
        main = pd.DataFrame(
            columns=["Objets","Personne"]
        )

    else:   
        main = pd.DataFrame(
            sheet.get("I:J"),
            columns=["Objets","Personne"]
        )

    return main

def update_chart(chart,ws,df_name):
    sheet = spreadsheet.worksheet(str(ws))
    list_df = chart.to_numpy().tolist()
    
    if ws == "Recipes" and df_name=="recipe":
        sheet.clear()
        sheet.update("A1",list_df)
        return

    elif ws == "Final_df" and df_name=="main":
        sheet.batch_clear(["A1:D"])
        sheet.update("A1:D",list_df)
        return

    elif ws == "Final_df" and df_name=="apero":
        sheet.batch_clear(["F1:G"])
        sheet.update("F1:G",list_df)
        return

    elif ws == "Final_df" and df_name=="object":
        sheet.batch_clear(["I1:J"])
        sheet.update("I1:J", list_df)
        return

@st.cache_data(ttl=30)
def read_merge_aggregate():

    #Read and merge dataframe
    dfs_recipe = pd.DataFrame()
    dfs_other_food = pd.DataFrame()
    dfs_objects = pd.DataFrame()

    sheet_not_to_read = ["Recipes", "Final_food", "Final_other_food","Final_objects"]
    
    for ws in spreadsheet.worksheets():

        if ws.title in sheet_not_to_read:
            continue
        
        values_recipe = ws.get("A:C")
        values_other_food = ws.get("E:E")
        values_objects = ws.get("G:G")

        name = ws.title

        if not any([
            values_recipe,
            values_other_food,
            values_objects
        ]):
            continue
        
        df_recipe = pd.DataFrame(values_recipe,columns=["Ingrédients","Quantité","Unité de mesure"])
        df_recipe['Personne'] = name
        df_other_food = pd.DataFrame(values_other_food,columns=["Articles"])
        df_other_food['Personne'] = name
        df_objects = pd.DataFrame(values_object,columns=["Objets"])
        df_objects['Personne'] = name
                
        dfs_recipe = pd.concat([dfs_recipe,df_recipe], ignore_index=True)
        dfs_other_food = pd.concat([dfs_other_food,df_other_food], ignore_index=True)
        dfs_objects = pd.concat([dfs_objects,df_objects], ignore_index=True)

    #Aggregate dataframe
    dfs_recipe_final = aggregate_lists(dfs_recipe)
    dfs_other_food_final = aggregate_list_2(dfs_other_food)
    dfs_objects_final = aggregate_list_3(dfs_objects)
    
    return dfs_recipe_final, dfs_other_food_final, dfs_objects_final

def save_merge_data_to_sheet(df_recipe, df_other_food, df_objects):
    sheet = spreadsheet.worksheet("Final_df")

    sheet.batch_clear([
                          "A:D",
                          "F:G",
                          "I:J"
                      ])
    
    sheet.update("A1:D", df_recipe)
    sheet.update("F1:G", df_other_food)
    sheet.update("I1:J", df_objects)

    return

    

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
    df["Articles"] = (df["Articles"]
        .str.strip()
        .str.lower()
        )
    
    final_df = (
        df.groupby(["Articles"], as_index=False)
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
    name_norm = name.strip().lower()
    sheet = spreadsheet.worksheet("Recipes")

    values = sheet.get_all_values()

    if values == [[]]:
        values = []

    found = False

    for i, row in enumerate(values):
        if row and row[0].strip().lower() == name_norm:
            values[i] = [name, recipe]
            found = True
            break

    if not found:
        values.append([name, recipe])             
    print(values)
    sheet.clear()
    sheet.update("A1",values)
    print(values)
    return

  
#Sheet for every person recipe

def save_data_to_sheet(name, df_recipe, df_other_food, df_objects):
    name_norm = name.strip().lower()
    ws_names = get_worksheets_name()

    if str(name_norm) in ws_names :
        sheet = spreadsheet.worksheet(str(name_norm))
    else :
        sheet = spreadsheet.add_worksheet(title=str(name_norm), rows=100, cols=10)

    list_recipe = sheet.get("A:C")
    if not list_recipe:
        list_recipe.extend(df_recipe.to_numpy().tolist())
    else:
        list_recipe = df_recipe.to_numpy().tolist()

    list_other_food = sheet.get("E:E")
    if not list_other_food:
        list_other_food.extend(df_other_food.to_numpy().tolist())
    else:
        list_other_food = df_other_food.to_numpy().tolist()

    list_objects = sheet.get("G:G")
    if not list_objects:
        list_objects.extend(df_objects.to_numpy().tolist())
    else:
        list_objects = df_objects.to_numpy().tolist()

    sheet.batch_clear([
        "A:C",
        "E:E",
        "G:G"
    ])
    
    sheet.update("A1:C",list_recipe)
    sheet.update("E1:E",list_other_food)
    sheet.update("G1:G",list_objects)
    
    return



    
