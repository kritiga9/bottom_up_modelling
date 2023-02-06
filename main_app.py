import streamlit as st
import pandas as pd
import streamlit_keboola_api.src.keboola_api as kb
import os
from io import StringIO
from st_aggrid import AgGrid, GridUpdateMode, DataReturnMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import ColumnsAutoSizeMode
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
#import cred

client = Client(st.secrets.url, st.secrets.key) 

@st.experimental_memo(ttl=7200)
def read_df(table_id, index_col=None, date_col=None):
    client.tables.export_to_file(table_id, '.')
    table_name = table_id.split(".")[-1]
    return pd.read_csv(table_name, index_col=index_col, parse_dates=date_col)

def read_df_segment(table_id, index_col=None, date_col=None):
    client.tables.export_to_file(table_id, '.')
    table_name = table_id.split(".")[-1]
    return pd.read_csv(table_name, index_col=index_col, parse_dates=date_col)


def saveFile(uploaded):
    with open(os.path.join(os.getcwd(),uploaded.name),"w") as f:
        strIo= StringIO(uploaded.getvalue().decode("utf-8"))
        f.write(strIo.read())
        return os.path.join(os.getcwd(),uploaded.name)

newsletter = read_df('out.c-ACME_BUM_LFL.SI_NEWSLETTERS')
#newsletter = newsletter[["VERSION","WEEK","CATEGORY","BRAND","SOURCE","NEWSLETTERS_SENT","SENT_TO_PDV_RATE"]]
marketing_spend = read_df('out.c-ACME_BUM_LFL.SI_MARKETING_SPEND')
conversion_rates = read_df('out.c-ACME_BUM_LFL.SI_CONVERSION_RATES')
cogs = read_df('out.c-ACME_BUM_LFL.SI_COGS_PER_PIECE')
pnl = read_df('out.c-ACME_BUM_LFL.SI_PNL')
web_analytics = read_df('out.c-ACME_DATASET.15_WEB_ANALYTICS')


L1 = [1, 2, 3,4,5]
d1 = dict.fromkeys(L1, 'January')

L2 = [6,7,8,9]
d2 = dict.fromkeys(L2, 'February')

L3 = [10,11,12,13]
d3 = dict.fromkeys(L3, 'March')

L4 = [14,15,16,17,18]
d4 = dict.fromkeys(L4, 'April')

L5 = [19,20,21,22]
d5 = dict.fromkeys(L5, 'May')

L6 = [23,24,25,26]
d6 = dict.fromkeys(L6, 'June')

L7 = [27,28,29,30,31]
d7 = dict.fromkeys(L7, 'July')

L8 = [32,33,34,35]
d8 = dict.fromkeys(L8,'August')

L9 = [36,37,38,39]
d9 = dict.fromkeys(L9,'September')

L10 = [40,41,42,43,44]
d10 = dict.fromkeys(L10,'October')

L11 = [45,46,47,48]
d11 = dict.fromkeys(L11,'November')

L12 = [49,50,51,52]
d12 = dict.fromkeys(L12,'December')


#d = {**d1, **d2,**d3,**d4,**d5,**d6,**d7,**d8,**d9,**d10,**d11,**d12}


#newsletter['MONTH'] = newsletter['WEEK'].map(d)
#st.write(newsletter.groupby(['VERSION',"MONTH",'BRAND','CATEGORY','SOURCE'])[])
#st.write(newsletter["VERSION"].unique())

#create a new column % of newsletters sent so that you can filter it out
# Create selectbox


# Just to show the selected option
#if selection != "Another option...":
#    st.info(f":white_check_mark: The selected option is {selection} ")
#else: 
#    st.info(f":white_check_mark: The written option is {otherOption} ")

# need to write something to disable the filters

weeks = web_analytics["WEEK"].unique() 
category = web_analytics["CATEGORY"].unique() 
brand = web_analytics["BRAND"].unique()
source = web_analytics["SOURCE_CHANNEL"].unique()

#st.session_state.diabled=False

with st.sidebar:

    column_1,column_2 = st.columns(2)

    with column_1:
        week_selection = st.multiselect("Week",weeks,weeks)

    with column_2:
        category_selection = st.multiselect("Category",category,category)

    column_3,column_4 = st.columns(2)

    with column_3:
        brand_selection = st.multiselect("Brand",brand,brand )

    with column_4:
        source_selection = st.multiselect("Source",source,source )

#st.checkbox("Disable filters", key="disabled")



versions = [f"{i}" for i in (newsletter[~newsletter["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique())] + [f"{i}" for i in (marketing_spend[~marketing_spend["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique())] + ["New Scenario"]


version_selection = st.selectbox("Select option", options=versions, key="version_selection")

# Create text input for user entry
if version_selection == "New Scenario": 
    otherOption = st.text_input("Name your Scenario",key="new_scenario")

col2,col3 = st.columns(2)
with col2:
    st.button("Save Inputs", key="save_input")

with col3:
    st.button("Calculate Results", key="calculate_result")


tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs(["Newsletters","Marketing Spend","Conversion Rates","COGS","P&L","Results"])

with tab1:

    if (version_selection == "New Scenario") or (version_selection not in newsletter[~newsletter["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        df = newsletter[newsletter["VERSION"]=='LFL']
    else:
        df = newsletter[newsletter["VERSION"]==version_selection]


    tab_11 = st.slider("Newsletters Sent",-100,100,0)
    tab_12 = st.slider("Sent to PDV Rate",-100,100,0)
    df["NEWSLETTERS_SENT"] = df["NEWSLETTERS_SENT"]*(1 + tab_11/100)     
    df["SENT_TO_PDV_RATE"] = df["SENT_TO_PDV_RATE"]*(1 + tab_12/100) 
    df= df[( df["WEEK"].isin(week_selection)) & ( df["BRAND"].isin(brand_selection)) & (df["CATEGORY"].isin(category_selection)) & (df["SOURCE"].isin(source_selection))]      
    st.write(df)


    newsletter_tmp = df
    # #need to capture the filters from the primary keys->TODO
    # gd_1 = GridOptionsBuilder.from_dataframe(df)
    # #gd_1.configure_default_column(editable=True,groupable=True)
    # #gd_1.configure_selection(selection_mode="multiple", use_checkbox=True)
    # gridoptions = gd_1.build()
    # grid_table_1 = AgGrid(df,gridOptions=gridoptions,
    #                     update_mode= GridUpdateMode.FILTERING_CHANGED,
    #                     data_return_mode = DataReturnMode.FILTERED,
    #                     fit_columns_on_grid_load= True,
    #                     allow_unsafe_jscode=True,
    #                     height = 700,
    #                     #columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    #                     width = 10,
    # )
    # newsletter_tmp = pd.DataFrame(grid_table_1["data"])


with tab2:

    if (version_selection == "New Scenario") or (version_selection not in marketing_spend[~marketing_spend["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        df = marketing_spend[marketing_spend["VERSION"]=='LFL']
    else:
        df = marketing_spend[marketing_spend["VERSION"]==version_selection]
    

    tab_21 = st.slider(
                'Spend Eur',
                 -100,100,0)
    tab_22= st.slider(
                'Cost Per click EUR',
                 -100, 100,0)

    df["SPEND_EUR"] = df["SPEND_EUR"]*(1 + tab_21/100)      
    df["COST_PER_CLICK_EUR"] = df["COST_PER_CLICK_EUR"]*(1 + tab_22/100) 
    df= df[( df["WEEK"].isin(week_selection)) & ( df["BRAND"].isin(brand_selection)) & (df["CATEGORY"].isin(category_selection)) & (df["SOURCE"].isin(source_selection))]        
    st.write(df)
    marketing_spend_tmp = df
     
    # gd_2 = GridOptionsBuilder.from_dataframe(df)
    # gd_2.configure_default_column(editable=True,groupable=True)
    # gd_2.configure_selection(selection_mode="multiple", use_checkbox=True)
    # gridoptions = gd_2.build()
    # grid_table_2 = AgGrid(df,gridOptions=gridoptions,
    #                     update_mode= GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED,
    #                     allow_unsafe_jscode=True,
    #                     height = 700
    # )
    # marketing_spend_tmp = pd.DataFrame(grid_table_2["data"])

with tab3:
    if (version_selection == "New Scenario") or (version_selection not in conversion_rates[~conversion_rates["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        df = conversion_rates[conversion_rates["VERSION"]=='LFL']
    else:
        df = conversion_rates[conversion_rates["VERSION"]==version_selection]
    

    tab_31= st.slider(
                'Purchase to PDV rate',
                 -100, 100,0)  
 
    df["PURCHASE_TO_PDV_RATE"] = df["PURCHASE_TO_PDV_RATE"]*(1 + tab_31/100)    
    df= df[( df["WEEK"].isin(week_selection)) & ( df["BRAND"].isin(brand_selection)) & (df["CATEGORY"].isin(category_selection)) & (df["SOURCE"].isin(source_selection))]        
    st.write(df)   
    conversion_rates_tmp = df
  
    # gd_3 = GridOptionsBuilder.from_dataframe(df)
    # gd_3.configure_default_column(editable=True,groupable=True)
    # gd_3.configure_selection(selection_mode="multiple", use_checkbox=True)
    # gridoptions = gd_3.build()
    # grid_table_3 = AgGrid(df,gridOptions=gridoptions,
    #                     update_mode= GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED,                        
    #                     allow_unsafe_jscode=True,
    #                     height = 700
    # )
    # conversion_rates_tmp = pd.DataFrame(grid_table_3["data"])


with tab4:    
    if (version_selection == "New Scenario") or (version_selection not in cogs[~cogs["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        df = cogs[cogs["VERSION"]=='LFL']
    else:
        df = cogs[cogs["VERSION"]==version_selection]
    

    tab_41= st.slider(
                'Weight by pieces sold',
                 -100,100,0) 
    tab_42 = st.slider(
                'COGS per piece EUR',
                 -100, 100,0) 
    df["WEIGHT_BY_PIECES_SOLD"] = df["WEIGHT_BY_PIECES_SOLD"]*(1 + tab_41/100)      
    df["COGS_PER_PIECE_EUR"] = df["COGS_PER_PIECE_EUR"]*(1 + tab_42/100)      
    df= df[( df["WEEK"].isin(week_selection)) & ( df["BRAND"].isin(brand_selection)) & (df["CATEGORY"].isin(category_selection)) & (df["SOURCE"].isin(source_selection))]        
    st.write(df)
    cogs_tmp = df

    # gd_4 = GridOptionsBuilder.from_dataframe(df)
    # gd_4.configure_default_column(editable=True,groupable=True)
    # gd_4.configure_selection(selection_mode="multiple", use_checkbox=True)
    # gridoptions = gd_4.build()
    # grid_table_4 = AgGrid(df,gridOptions=gridoptions,
    #                     update_mode= GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED,
    #                     allow_unsafe_jscode=True,
    #                     height = 700
    # )
    # cogs_tmp = pd.DataFrame(grid_table_4["data"])

with tab5:
    if (version_selection == "New Scenario") or (version_selection not in pnl[~pnl["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        df = pnl[pnl["VERSION"]=='LFL']
    else:
        df = pnl[pnl["VERSION"]==version_selection]


        
    tab_51= st.slider(
                'Price per piece EUR',
                 -100,100,0) 
    tab_52 = st.slider(
                'EUR bonus per piece',
                 -100, 100,0) 
    tab_53 = st.slider(
                'Bonus EUR as PCT COGS',
                 -100,100,0) 

    df["PRICE_PER_PIECE_EUR"] = df["PRICE_PER_PIECE_EUR"]*(1 + tab_51/100)      
    df["EUR_BONUS_PER_PIECE"] = df["EUR_BONUS_PER_PIECE"]*(1 + tab_52/100)      
    df["BONUS_EUR_AS_PCT_COGS"] = df["BONUS_EUR_AS_PCT_COGS"]*(1 + tab_53/100)      
    df= df[( df["WEEK"].isin(week_selection)) & ( df["BRAND"].isin(brand_selection)) & (df["CATEGORY"].isin(category_selection)) & (df["SOURCE"].isin(source_selection))]        
    st.write(df)
    pnl_tmp = df

    # gd_5 = GridOptionsBuilder.from_dataframe(df)
    # gd_5.configure_default_column(editable=True,groupable=True)
    # gd_5.configure_selection(selection_mode="multiple", use_checkbox=True)
    # gridoptions = gd_5.build()
    # grid_table_5 = AgGrid(df,gridOptions=gridoptions,
    #                     update_mode= GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SELECTION_CHANGED,
    #                     allow_unsafe_json=True,
    #                     height = 700
    # )
    # pnl_tmp = pd.DataFrame(grid_table_5["data"])
if st.session_state.calculate_result:
    with tab6:
        # all these df's should be the new version and not the final one right? / the edits made within the df
        si_newsletters_tmp = newsletter_tmp
        si_newsletters_tmp['PRODUCT_DETAIL_VIEWS'] = si_newsletters_tmp['NEWSLETTERS_SENT'] * ( si_newsletters_tmp['SENT_TO_PDV_RATE_NL_ONLY'] + si_newsletters_tmp['NL_TO_WA_BALANCING_FIGURE']) 
        si_newsletters_tmp = si_newsletters_tmp[["VERSION",'WEEK','BRAND','CATEGORY','SOURCE','NEWSLETTERS_SENT','PRODUCT_DETAIL_VIEWS']]
        si_marketing_spend_tmp =marketing_spend_tmp
        si_marketing_spend_tmp['NEWSLETTERS_SENT'] = 0
        si_marketing_spend_tmp['PRODUCT_DETAIL_VIEWS'] = si_marketing_spend_tmp["SPEND_EUR"] / si_marketing_spend_tmp['COST_PER_CLICK_EUR']
        si_marketing_spend_tmp = si_marketing_spend_tmp[["VERSION",'WEEK','BRAND','CATEGORY','SOURCE','NEWSLETTERS_SENT','PRODUCT_DETAIL_VIEWS']] 
        web_analytics_tmp = web_analytics[(web_analytics["SOURCE_CHANNEL"]=='SEARCH') & (web_analytics['YEAR']==4)].groupby(["WEEK",'BRAND','CATEGORY','SOURCE_CHANNEL'])['PRODUCT_DETAIL_VIEWS'].sum().reset_index().rename({'SOURCE_CHANNEL':'SOURCE'},axis='columns')
        web_analytics_tmp["NEWSLETTERS_SENT"] = 0
        web_analytics_tmp["VERSION"] = "ANY"
        web_analytics_tmp = web_analytics_tmp[["VERSION",'WEEK','BRAND','CATEGORY','SOURCE','NEWSLETTERS_SENT','PRODUCT_DETAIL_VIEWS']]
        web_traffic = pd.concat([si_newsletters_tmp,si_marketing_spend_tmp,web_analytics_tmp])
        si_cogs_tmp = cogs_tmp
        si_cogs_tmp["COGS_PER_PIECE"] = si_cogs_tmp['COGS_PER_PIECE_EUR'] * si_cogs_tmp['WEIGHT_BY_PIECES_SOLD']
        si_cogs_tmp = si_cogs_tmp.groupby(['VERSION',"WEEK",'BRAND','CATEGORY','SOURCE'])['COGS_PER_PIECE'].sum().reset_index()
        si_conversion_rates_tmp = conversion_rates_tmp
        si_pnl_tmp = pnl_tmp

        # TO CHECK, SOMETHING NOT RIGHT WITH THE MERGES
        # join dataframes
        df_result = (
            web_traffic.merge(
                si_marketing_spend_tmp,
                how="left",
                on=["VERSION", "WEEK", "BRAND", "CATEGORY", "SOURCE"],
            )
            .merge(
                marketing_spend_tmp[["VERSION", "WEEK", "BRAND", "CATEGORY", "SOURCE","SPEND_EUR"]],
                how="left",
                on=["VERSION", "WEEK", "BRAND", "CATEGORY", "SOURCE"],
            )      
            .merge(
                si_conversion_rates_tmp,
                how="left",
                on=["VERSION", "WEEK", "BRAND", "CATEGORY", "SOURCE"],
            )
            .merge(
                si_pnl_tmp,
                how="left",
                on=["VERSION", "WEEK", "BRAND", "CATEGORY", "SOURCE"],
            )
            .merge(si_cogs_tmp, how="left", on=["VERSION", "WEEK", "BRAND", "CATEGORY", "SOURCE"])
        )
        # SELECT
        df_result["PIECES_SOLD"] = df_result["PRODUCT_DETAIL_VIEWS_x"] * df_result["PURCHASE_TO_PDV_RATE"]
        df_result["REVENUE_EUR"] = df_result["PIECES_SOLD"] * df_result["PURCHASE_TO_PDV_RATE"]
        df_result["COGS_EUR"] = df_result["PIECES_SOLD"] * df_result["COGS_PER_PIECE"]
        df_result["EUR_BONUS_PER_PIECE"] = df_result["PIECES_SOLD"] * df_result["EUR_BONUS_PER_PIECE"]
        df_result["BONUS_EUR_AS_PCT_COGS"] = df_result["COGS_EUR"] * df_result["BONUS_EUR_AS_PCT_COGS"]
        df_result = df_result[
            [
                "VERSION",
                "WEEK",
                "BRAND",
                "CATEGORY",
                "SOURCE",
                "PRODUCT_DETAIL_VIEWS_x",
                "SPEND_EUR",
                "PIECES_SOLD",
                "REVENUE_EUR",
                "COGS_EUR",
                'EUR_BONUS_PER_PIECE',
                "BONUS_EUR_AS_PCT_COGS"
            ]
        ]
        st.write(df_result)

