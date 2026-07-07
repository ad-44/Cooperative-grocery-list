'''
Gestion de la liste de courses pour des vacances entre copains !
date : 2026/07/06    
'''

#%% Imports
import pandas as pd
import numpy as np
import streamlit as st
import func 


#%% Interface
st.title("La liste de :red[course] pour _Arêches_ ! :sunglasses:")

tab1, tab2, tab3, tab4 = st.tabs(["Ajoute des ingrédients à la liste", "La liste des recettes", "La liste de courses", "La liste des objets"])

# Tab 1 : user input

with tab1:
    
    # Input name
    user_name = st.text_input("Qui est tu ?", placeholder="Un.e petit.e filou.te qui ne veux pas donner son prénom !")

    # Input recipe name
    recipe_name = st.text_input("Quelle recette vas-tu nous préparer ?", placeholder="Une tarte au concombre ;P")

    # Input ingredients recipe
    ingredients_df = pd.DataFrame(columns=["Ingrédients","Quantité","Unité de mesure"])
    
    st.header("Ingrédients pour ta recette :carrot: :cucumber: :eggplant:", divider="green", text_alignment="center")
    edited_ingredients_df = st.data_editor(ingredients_df, num_rows="dynamic")

    # Input other ingredients
    other_ingredients_df = pd.DataFrame(columns=["Items"])

    st.header("D'autres envies ? :candy: :beer: :peanuts: :cupcake: ", divider="green", text_alignment="center")
    st.info("Marque ici les articles de course dont tu aurais envie (e.g. fruits, gateaux, chips, alcool, un cd de Feu! Chatterton pour écouter pendant l'apéro, etc.)", icon=":material/info_i:")
    edited_other_ingredients_df = st.data_editor(other_ingredients_df, num_rows="dynamic")

    # Input other stuff

    other_df = pd.DataFrame(columns=["Autres choses"])

    st.header("Tu amènes d'autres choses ? :soccer: :guitar: :teddy_bear:", divider="green", text_alignment="center")
    st.info("Ici, c'est la liste de tous autres objets que tu souhaites amener et qui pourrait bénéficier à tous le monde (e.g. crème solaire, enceinte bluetooth, boule de pétanque, etc.)", icon=":material/info:")
    edited_other_df = st.data_editor(other_df, num_rows="dynamic")

    st.space("medium")
    validate_button = st.button("J'ai fini ma liste ! :confetti_ball: :tada:", type="primary")

    if validate_button :
        func.save_recipes(user_name,recipe_name)
        func.save_ingredients(user_name,edited_ingredients_df,"main_course")
        func.save_ingredients(user_name,edited_other_ingredients_df,"apero")
        func.save_ingredients(user_name,edited_other_df,"other_stuff")

        func.get_worksheets_name.clear()
        func.get_recipes.clear()
        func.read_and_merge.clear()
        
        st.success("Ta recette a été ajouté!")

with tab2 :
    recipe_list = func.get_recipes("Recipes")
    df_recipe = pd.DataFrame(recipe_list)
    edited_df_recipe = st.data_editor(df_recipe)
 
    if not edited_df_recipe.equals(df_recipe):
        func.update_chart(edited_df_recipe,"Recipes")
    

with tab3:
    st.header("Liste de course pour les plats principaux", divider="green", text_alignment="center")
    main_list = func.read_and_merge("main_course",ingredients_df.columns)

    if main_list.empty == True:
        st.text("Personne n'a complété la liste pour le moment.")
        
    else:
        agg_main_list = func.aggregate_lists(main_list)
        edited_df_main = st.data_editor(agg_main_list)

    st.header("Liste pour les autres produits", divider="green", text_alignment="center")
    apero_list = func.read_and_merge("apero",["Ingrédients"])

    if apero_list.empty == True:
        st.text("Personne n'a complété la liste pour le moment.")        

    else:
        agg_apero_list = func.aggregate_list_2(apero_list)
        edited_df_apero = st.data_editor(agg_apero_list)
            
with tab4:
    stuff_list = func.read_and_merge("other_stuff",["Objets"])

    if stuff_list.empty == True:
        st.text("Personne n'a complété la liste pour le moment.")
        
    else:
        agg_stuff_list = func.aggregate_list_3(stuff_list)
        edited_df_stuff = st.data_editor(agg_stuff_list)
