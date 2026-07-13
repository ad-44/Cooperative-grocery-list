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

    units = [
        "",
        "g",
        "kg",
        "mL",
        "L",
        "pièce",
        "boîte",
        "bouteille",
    ]
        
    st.header("Ingrédients pour ta recette :carrot: :cucumber: :eggplant:", divider="green", text_alignment="center")
    edited_ingredients_df = st.data_editor(ingredients_df, num_rows="dynamic",column_config={"Unité de mesure":st.column_config.SelectboxColumn("Unité de mesure",options=units,required=False)})

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
    validate_button = st.button("J'ai fini ma liste ! :confetti_ball: :tada:", type="primary",key="main_button")

    if validate_button :
        with st.spinner("Traitement en cours...", show_time=True):
            list_error = [user_name,recipe_name]
            if any(not item for item in list_error):
                st.error("Tu as oublié de remplir ton prénom ou ton plat!", icon=":material/error:")
                st.stop()
        
            func.save_recipes(user_name,recipe_name)
            func.save_data_to_sheet(user_name, edited_ingredients_df, edited_other_ingredients_df,edited_other_df)
            main_df, apero_df, object_df = func.read_merge_aggregate()
            func.save_merge_data_to_sheet(main_df,apero_df,object_df)

            func.get_worksheets_name.clear()
            func.get_recipes.clear()
            func.read_merge_aggregate.clear()

            st.rerun()
        
        st.success("Ta recette a été ajouté!")

with tab2 :
    recipe_list = func.get_recipes("Recipes")
    df_recipe = pd.DataFrame(recipe_list)
    edited_df_recipe = st.data_editor(df_recipe)

    update_recipe_button = st.button("Sauvegarde les changements! :floppy_disk:", type="primary", key="update_recipe")
 
    if update_recipe_button:
        func.update_chart(edited_df_recipe,"Recipes","recipe")
    

with tab3:
    st.header("Liste de course pour les plats principaux", divider="green", text_alignment="center")

    main_df = func.read_final_main_df()

    if main_df.empty == True:
        st.text("Personne n'a complété la liste pour le moment.")
        
    else:
        edited_df_main = st.data_editor(main_df)
        update_food_button = st.button("Sauvegard les changements! :floppy_disk:", type="primary",key="update_food")

        if update_food_button :
            func.update_chart(edited_df_main,"Final_df","main")

    st.header("Liste pour les autres produits", divider="green", text_alignment="center")

    apero_df = func.read_final_apero_df()

    if apero_df.empty == True:
        st.text("Personne n'a complété la liste pour le moment.")        

    else:
        edited_df_apero = st.data_editor(apero_df)
        update_apero_button = st.button("Sauvegard les changements! :floppy_disk:", type="primary", key="update_apero")

        if update_apero_button :
            func.update_chart(edited_df_apero,"Final_df","apero")
           
with tab4:
    
    object_df = func.read_final_objects_df()
    
    if object_df.empty == True:
        st.text("Personne n'a complété la liste pour le moment.")
        
    else:
        edited_df_object = st.data_editor(object_df)
        
        update_object_button = st.button("Sauvegard les changements! :floppy_disk:", type="primary",key="update_objects")

        if update_object_button :
            func.update_chart(edited_df_object,"Final_df","object")
