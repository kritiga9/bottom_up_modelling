import streamlit as st
import pandas as pd
import streamlit_keboola_api.src.keboola_api as kb
from kbcstorage.client import Client
import duckdb
import plotly.express as px 


st.set_page_config(layout="wide")



client = Client(st.secrets.kbc_url, st.secrets.kbc_token) 

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
marketing_spend = read_df('out.c-ACME_BUM_LFL.SI_MARKETING_SPEND')
conversion_rates = read_df('out.c-ACME_BUM_LFL.SI_CONVERSION_RATES')
cogs = read_df('out.c-ACME_BUM_LFL.SI_COGS_PER_PIECE')
pnl = read_df('out.c-ACME_BUM_LFL.SI_PNL')
web_analytics = read_df('out.c-ACME_DATASET.15_WEB_ANALYTICS')
lfl = read_df('out.c-ACME_BUM_SCENARIO_RESULTS.BUM_IS_FINAL_REASONABLE')


versions =   ["New Scenario"] + [f"{i}" for i in (newsletter[~newsletter["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique())] + [f"{i}" for i in (marketing_spend[~marketing_spend["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique())]


version_selection = st.selectbox("Select option", options=versions, key="version_selection")

# Create text input for user entry
if version_selection == "New Scenario": 
    otherOption = st.text_input("Name your Scenario",key="new_scenario")
else:
    otherOption = st.text_input("Rename to save as new",value = version_selection,key="new_scenario")

#st.button("Calculate Results", key="calculate_result")


tab1,tab2,tab3,tab4,tab5,tab6, tab7 = st.tabs(["Newsletters","Marketing Spend","Conversion Rates","COGS","P&L","Results", "Save"])

## AW: just to make it sligthly more reusable. Checks if key is loaded. If not it creates the key and add value to it.
def check_and_set_state(ss_key,value):
    if ss_key not in st.session_state:
        st.session_state[ss_key] = value

with tab1:
    newsletter_tmp = newsletter.copy()
    category_t1 = newsletter["CATEGORY"].unique() 
    brand_t1 = newsletter["BRAND"].unique()
    source_t1 = newsletter["SOURCE"].unique()

    if (version_selection == "New Scenario") or (version_selection not in newsletter[~newsletter["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        df = newsletter[newsletter["VERSION"]=='LFL']
        newsletter_tmp = newsletter_tmp[newsletter_tmp["VERSION"]=='LFL']

    else:
        df = newsletter[newsletter["VERSION"]==version_selection]
        ## AW: here was an error: changed LFL to "version_selection"
        newsletter_tmp = newsletter_tmp[newsletter_tmp["VERSION"]==version_selection]



     ## AW: Loading to state so we can return to it after rerun.
    check_and_set_state('newsletter_tmp',newsletter_tmp)
    #newsletter_ss = st.session_state['newsletter_tmp']

    column_1,column_2,column_3 = st.columns(3)

    with column_1:
        brand_selection_t1 = st.multiselect("Brand",brand_t1,brand_t1 )

    with column_2:
        source_selection_t1 = st.multiselect("Source",source_t1,source_t1 )

    with column_3:
        category_selection_t1 = st.multiselect("Category",category_t1,category_t1)
    
    tab_11 = st.slider("Newsletters Sent",-100,100,0)
    tab_12 = st.slider("Sent to PDV Rate",-100,100,0)
    df["NEWSLETTERS_SENT"] = df["NEWSLETTERS_SENT"]*(1 + tab_11/100)     
    df["SENT_TO_PDV_RATE"] = df["SENT_TO_PDV_RATE"]*(1 + tab_12/100) 
    df["NEWSLETTERS_SENT"] = df["NEWSLETTERS_SENT"].astype(int)   
    df= df[ ( df["BRAND"].isin(brand_selection_t1)) & (df["CATEGORY"].isin(category_selection_t1)) & (df["SOURCE"].isin(source_selection_t1))]      
    st.write(df[["WEEK","BRAND","CATEGORY","SOURCE","NEWSLETTERS_SENT","SENT_TO_PDV_RATE"]])
    save_state_t1 = st.button("Save filters")
    if save_state_t1:
            ## AW: Writing back to state
        newsletter_tmp.loc[newsletter_tmp.index.isin(df.index), ['NEWSLETTERS_SENT']]= df['NEWSLETTERS_SENT'] 
        newsletter_tmp.loc[newsletter_tmp.index.isin(df.index), ['SENT_TO_PDV_RATE']]= df['SENT_TO_PDV_RATE']
        st.session_state['newsletter_tmp'] = newsletter_tmp



with tab2:
    marketing_spend_tmp = marketing_spend.copy() 
    category_t2 = marketing_spend["CATEGORY"].unique() 
    brand_t2 = marketing_spend["BRAND"].unique()
    source_t2= marketing_spend["SOURCE"].unique()

    if (version_selection == "New Scenario") or (version_selection not in marketing_spend[~marketing_spend["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        df = marketing_spend[marketing_spend["VERSION"]=='LFL']
        marketing_spend_tmp = marketing_spend_tmp[marketing_spend_tmp["VERSION"]=='LFL']

    else:
        df = marketing_spend[marketing_spend["VERSION"]==version_selection]
        marketing_spend_tmp = marketing_spend_tmp[marketing_spend_tmp["VERSION"]==version_selection]

    ## Loading to state so we can return to it after rerun.
    check_and_set_state('marketing_spend_tmp',marketing_spend_tmp)
    #marketing_spend_ss = st.session_state['marketing_spend_tmp']
    
    column_4,column_5,column_6 = st.columns(3)

    with column_4:
        brand_selection_t2 = st.multiselect("Brand ",brand_t2,brand_t2 )

    with column_5:
        source_selection_t2 = st.multiselect("Source ",source_t2,source_t2 )

    with column_6:
        category_selection_t2 = st.multiselect("Category ",category_t2,category_t2)

    tab_21 = st.slider(
                'Spend Eur',
                 -100,100,0)
    tab_22= st.slider(
                'Cost Per click EUR',
                 -100, 100,0)

    df["SPEND_EUR"] = df["SPEND_EUR"]*(1 + tab_21/100)      
    df["COST_PER_CLICK_EUR"] = df["COST_PER_CLICK_EUR"]*(1 + tab_22/100) 
    df["SPEND_EUR"] = df["SPEND_EUR"].astype(int)   
    df= df[ ( df["BRAND"].isin(brand_selection_t2)) & (df["CATEGORY"].isin(category_selection_t2)) & (df["SOURCE"].isin(source_selection_t2))]        
    st.write(df.loc[:, ~df.columns.isin(['VERSION'])])
    save_state_t2 = st.button("Save filters ")
    if save_state_t2:
        ## AW: Writing back to state
        marketing_spend_tmp.loc[marketing_spend_tmp.index.isin(df.index), ['SPEND_EUR']]= df[['SPEND_EUR']] 
        marketing_spend_tmp.loc[marketing_spend_tmp.index.isin(df.index), ['COST_PER_CLICK_EUR']]= df[['COST_PER_CLICK_EUR']] 
        st.session_state['marketing_spend_tmp'] = marketing_spend_tmp

    
     

with tab3:
    conversion_rates_tmp = conversion_rates.copy()
    category_t3= conversion_rates["CATEGORY"].unique() 
    brand_t3 = conversion_rates["BRAND"].unique()
    source_t3= conversion_rates["SOURCE"].unique()

    if (version_selection == "New Scenario") or (version_selection not in conversion_rates[~conversion_rates["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        df = conversion_rates[conversion_rates["VERSION"]=='LFL']
        conversion_rates_tmp = conversion_rates_tmp[conversion_rates_tmp["VERSION"]=='LFL']

    else:
        df = conversion_rates[conversion_rates["VERSION"]==version_selection]
        conversion_rates_tmp = conversion_rates_tmp[conversion_rates_tmp["VERSION"]==version_selection]

    ## AW: Loading to state so we can return to it after rerun.
    check_and_set_state('conversion_rates_tmp',conversion_rates_tmp)
    #conversion_rates_ss = st.session_state['conversion_rates_tmp']
        
    column_7,column_8,column_9 = st.columns(3)

    with column_7:
        brand_selection_t3 = st.multiselect(" Brand",brand_t3,brand_t3 )

    with column_8:
        source_selection_t3 = st.multiselect(" Source",source_t3,source_t3 )

    with column_9:
        category_selection_t3 = st.multiselect(" Category",category_t3,category_t3)

    tab_31= st.slider(
                'Purchase to PDV rate',
                 -100, 100,0)  
 
    df["PURCHASE_TO_PDV_RATE"] = df["PURCHASE_TO_PDV_RATE"]*(1 + tab_31/100)  
    df= df[( df["BRAND"].isin(brand_selection_t3)) & (df["CATEGORY"].isin(category_selection_t3)) & (df["SOURCE"].isin(source_selection_t3))]        
    st.write(df.loc[:, ~df.columns.isin(['VERSION'])])   
    save_state_t3 = st.button("Save filters.")
    if save_state_t3:
        ## AW: Writing back to state
        conversion_rates_tmp.loc[conversion_rates_tmp.index.isin(df.index), ['PURCHASE_TO_PDV_RATE']]= df[['PURCHASE_TO_PDV_RATE']] 
        st.session_state['conversion_rates_tmp'] = conversion_rates_tmp

with tab4:    
    cogs_tmp = cogs.copy() 
    category_t4= cogs["CATEGORY"].unique() 
    brand_t4 = cogs["BRAND"].unique()
    source_t4= cogs["SOURCE"].unique()
    if (version_selection == "New Scenario") or (version_selection not in cogs[~cogs["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        df = cogs[cogs["VERSION"]=='LFL']
        cogs_tmp = cogs_tmp[cogs_tmp["VERSION"]=='LFL']
    else:
        df = cogs[cogs["VERSION"]==version_selection]
        cogs_tmp = cogs_tmp[cogs_tmp["VERSION"]==version_selection]

    ## AW: Loading to state so we can return to it after rerun.
    check_and_set_state('cogs_tmp',cogs_tmp)
    #cogs_ss = st.session_state['cogs_tmp']
    
    column_10,column_11,column_12 = st.columns(3)

    with column_10:
        brand_selection_t4 = st.multiselect("Brand  ",brand_t4,brand_t4 )

    with column_11:
        source_selection_t4 = st.multiselect("Source  ",source_t4,source_t4 )

    with column_12:
        category_selection_t4 = st.multiselect("Category  ",category_t4,category_t4)

    

    tab_42 = st.slider(
                'COGS per piece EUR',
                 -100, 100,0) 
    df["COGS_PER_PIECE_EUR"] = (df["COGS_PER_PIECE_EUR"]*(1 + tab_42/100)   ).round(2)  
    df= df[( df["BRAND"].isin(brand_selection_t4)) & (df["CATEGORY"].isin(category_selection_t4)) & (df["SOURCE"].isin(source_selection_t4))]        
    st.write(df[["WEEK","BRAND","CATEGORY","SOURCE","SKU_NAME","COGS_PER_PIECE_EUR","WEIGHT_BY_PIECES_SOLD"]])
    save_state_t4 = st.button("Save Filter")
    if save_state_t4:
        # AW: writing back to state
        cogs_tmp.loc[cogs_tmp.index.isin(df.index), ['COGS_PER_PIECE_EUR']]= df[['COGS_PER_PIECE_EUR']] 
        st.session_state['cogs_tmp'] = cogs_tmp



with tab5:
    pnl_tmp = pnl.copy() 
    category_t5= pnl["CATEGORY"].unique() 
    brand_t5 = pnl["BRAND"].unique()
    source_t5= pnl["SOURCE"].unique()

    if (version_selection == "New Scenario") or (version_selection not in pnl[~pnl["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        df = pnl[pnl["VERSION"]=='LFL']
        pnl_tmp = pnl_tmp[pnl_tmp["VERSION"]=='LFL']
    else:
        df = pnl[pnl["VERSION"]==version_selection]
        pnl_tmp = pnl_tmp[pnl_tmp["VERSION"]==version_selection]
    
    ## AW: Loading to state so we can return to it after rerun.
    check_and_set_state('pnl_tmp',pnl_tmp)
    #pnl_ss = st.session_state['pnl_tmp']
    
    
    column_13,column_14,column_15 = st.columns(3)

    with column_13:
        brand_selection_t5 = st.multiselect("Brand   ",brand_t5,brand_t5 )

    with column_14:
        source_selection_t5 = st.multiselect("Source   ",source_t5,source_t5 )

    with column_15:
        category_selection_t5 = st.multiselect("Category   ",category_t5,category_t5)


    tab_51= st.slider(
                'Price per piece EUR',
                 -100,100,0) 
    tab_52 = st.slider(
                'EUR bonus per piece',
                 -100, 100,0) 
    tab_53 = st.slider(
                'Bonus EUR as PCT COGS',
                 -100,100,0) 

    df["PRICE_PER_PIECE_EUR"] = (df["PRICE_PER_PIECE_EUR"]*(1 + tab_51/100))    
    df["EUR_BONUS_PER_PIECE"] = df["EUR_BONUS_PER_PIECE"]*(1 + tab_52/100)      
    df["BONUS_EUR_AS_PCT_COGS"] = df["BONUS_EUR_AS_PCT_COGS"]*(1 + tab_53/100)     
    df= df[ ( df["BRAND"].isin(brand_selection_t5)) & (df["CATEGORY"].isin(category_selection_t5)) & (df["SOURCE"].isin(source_selection_t5))]        
    st.write(df.loc[:, ~df.columns.isin(['VERSION'])])
    save_state_t5 = st.button("Save Filter.")
    if save_state_t5:
        # AW: writing back to state
        pnl_tmp.loc[pnl_tmp.index.isin(df.index), ['PRICE_PER_PIECE_EUR']]= df[['PRICE_PER_PIECE_EUR']] 
        pnl_tmp.loc[pnl_tmp.index.isin(df.index), ['EUR_BONUS_PER_PIECE']]= df[['EUR_BONUS_PER_PIECE']] 
        pnl_tmp.loc[pnl_tmp.index.isin(df.index), ['BONUS_EUR_AS_PCT_COGS']]= df[['BONUS_EUR_AS_PCT_COGS']] 
        st.session_state['pnl_tmp'] = pnl_tmp





with tab6:
    # AW: reading from state
    SI_NEWSLETTERS_TMP = st.session_state['newsletter_tmp']
    SI_MARKETING_SPEND_TMP =st.session_state['marketing_spend_tmp']
    WEB_ANALYTICS_TMP = web_analytics
    SI_COGS_PER_PIECE_TMP = st.session_state['cogs_tmp']
    SI_CONVERSION_RATES_TMP = st.session_state['conversion_rates_tmp']
    SI_PNL_TMP = st.session_state['pnl_tmp']
    df_result =(duckdb.query("""

WITH WEB_TRAFFIC AS (
SELECT VERSION,
    WEEK, 
    BRAND,
    CATEGORY,
    SOURCE, 
    NEWSLETTERS_SENT,
    NEWSLETTERS_SENT* (SENT_TO_PDV_RATE) AS PRODUCT_DETAIL_VIEWS 
FROM SI_NEWSLETTERS_TMP

UNION ALL
    
SELECT VERSION,
    WEEK,
    BRAND,
    CATEGORY,
    SOURCE,
    0 AS NEWSLETTERS_SENT,
    SPEND_EUR / COST_PER_CLICK_EUR AS PRODUCT_DETAIL_VIEWS
    FROM SI_MARKETING_SPEND_TMP

    
UNION ALL 
    SELECT

    'ANY' AS VERSION,
    WEEK,
    BRAND,
    CATEGORY,
    SOURCE_CHANNEL AS SOURCE,
    0 AS NEWSLETTERS_SENT,
    SUM(PRODUCT_DETAIL_VIEWS) AS PRODUCT_DETAIL_VIEWS
    FROM "WEB_ANALYTICS_TMP"
    WHERE SOURCE = 'SEARCH' AND YEAR = 4
    GROUP BY VERSION, WEEK, BRAND,CATEGORY,SOURCE     
),

COGS AS (
SELECT 
VERSION,
WEEK,
BRAND,
CATEGORY,
SOURCE,
SUM(COGS_PER_PIECE_EUR * WEIGHT_BY_PIECES_SOLD) AS COGS_PER_PIECE
FROM "SI_COGS_PER_PIECE_TMP"
GROUP BY
VERSION,
WEEK,
BRAND,
CATEGORY,
SOURCE)

SELECT
WT.VERSION,
WT.WEEK,
WT.BRAND,
WT.CATEGORY,
WT.SOURCE,
WT.PRODUCT_DETAIL_VIEWS AS PRODUCT_DETAIL_VIEWS,
MS.SPEND_EUR AS MARKETING_SPEND,
WT.PRODUCT_DETAIL_VIEWS * CR.PURCHASE_TO_PDV_RATE AS PIECES_SOLD,
(WT.PRODUCT_DETAIL_VIEWS * CR.PURCHASE_TO_PDV_RATE) * PNL.PRICE_PER_PIECE_EUR AS REVENUE_EUR,
(WT.PRODUCT_DETAIL_VIEWS * CR.PURCHASE_TO_PDV_RATE) * COGS.COGS_PER_PIECE AS COGS_EUR,
(WT.PRODUCT_DETAIL_VIEWS * CR.PURCHASE_TO_PDV_RATE) * PNL.EUR_BONUS_PER_PIECE AS EUR_BONUS_PER_PIECE,
((WT.PRODUCT_DETAIL_VIEWS * CR.PURCHASE_TO_PDV_RATE) * COGS.COGS_PER_PIECE)*PNL.BONUS_EUR_AS_PCT_COGS AS BONUS_EUR_AS_PCT_COGS


FROM WEB_TRAFFIC AS WT
LEFT JOIN SI_MARKETING_SPEND_TMP AS MS ON WT.VERSION = MS.VERSION AND WT.WEEK = MS.WEEK AND WT.BRAND = MS.BRAND AND WT.CATEGORY = MS.CATEGORY AND WT.SOURCE = MS.SOURCE 
LEFT JOIN SI_CONVERSION_RATES_TMP AS CR ON WT.VERSION = CR.VERSION AND WT.WEEK = CR.WEEK AND WT.BRAND = CR.BRAND AND WT.CATEGORY = CR.CATEGORY AND WT.SOURCE = CR.SOURCE
LEFT JOIN SI_PNL_TMP AS PNL ON WT.VERSION = PNL.VERSION AND WT.WEEK = PNL.WEEK AND WT.BRAND = PNL.BRAND AND WT.CATEGORY = PNL.CATEGORY AND WT.SOURCE = PNL.SOURCE 
LEFT JOIN COGS ON WT.VERSION = COGS.VERSION AND WT.WEEK = COGS.WEEK AND WT.BRAND = COGS.BRAND AND WT.CATEGORY = COGS.CATEGORY AND WT.SOURCE = COGS.SOURCE 
""" ).to_df())

    if version_selection == "New Scenario":
        df_result["VERSION"] = otherOption
    else :
        df_result["VERSION"] = version_selection

    df_agg = pd.DataFrame(df_result.sum(numeric_only=True)).T.drop(columns=["WEEK"])
    df_agg["VERSION"] = df_result["VERSION"].unique()
    lfl = lfl[lfl["VERSION"]=="LFL"]
    lfl_agg = pd.DataFrame(lfl.sum(numeric_only=True)).T.drop(columns=["ROW_COUNT","GROSS_MARGIN_3"])
    lfl_agg["VERSION"] = 'LFL'
    df_final = pd.concat([lfl_agg,df_agg])
    df_final = df_final[["VERSION","PRODUCT_DETAIL_VIEWS","MARKETING_SPEND","PIECES_SOLD","REVENUE_EUR","COGS_EUR","EUR_BONUS_PER_PIECE","BONUS_EUR_AS_PCT_COGS"]]
    df_final[["PRODUCT_DETAIL_VIEWS","MARKETING_SPEND","PIECES_SOLD","REVENUE_EUR","COGS_EUR","EUR_BONUS_PER_PIECE","BONUS_EUR_AS_PCT_COGS"]] =         df_final[["PRODUCT_DETAIL_VIEWS","MARKETING_SPEND","PIECES_SOLD","REVENUE_EUR","COGS_EUR","EUR_BONUS_PER_PIECE","BONUS_EUR_AS_PCT_COGS"]].astype(int)
    df_final["GROSS_MARGIN_1"] = df_final["REVENUE_EUR"] - df_final["COGS_EUR"]
    df_final["GROSS_MARGIN_2"] = df_final["GROSS_MARGIN_1"] + df_final["EUR_BONUS_PER_PIECE"] + df_final["BONUS_EUR_AS_PCT_COGS"]
    df_final["GROSS_MARGIN_3"] = df_final["GROSS_MARGIN_2"] - df_final["MARKETING_SPEND"]
    st.write(df_final)


    #Plot of the difference between LFL model and the selected one
    fig_df = pd.DataFrame(df_final._get_numeric_data().diff()[-1:].T.reset_index())
    fig_df = fig_df.rename(columns={ fig_df.columns[0]: "Metrics", fig_df.columns[1] : "Values" })
    fig=px.bar(fig_df,x='Values',y='Metrics', orientation='h')
    st.write(fig)


    #Plot of the  % difference between LFL model and the selected one
    fig_df = pd.DataFrame(df_final._get_numeric_data().pct_change()[-1:].T.reset_index())
    fig_df = fig_df.rename(columns={ fig_df.columns[0]: "Metrics", fig_df.columns[1] : "Values" })
    fig=px.bar(fig_df,x='Values',y='Metrics', orientation='h')
    st.write(fig)



    @st.experimental_memo
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')


    csv = convert_df(df_result)

    st.download_button(
    "Press to Download",
    csv,
    "file.csv",
    "text/csv",
    key='download-csv'
    )



with tab7:       
    if (version_selection == "New Scenario"):
        table_list = ["SI_NEWSLETTERS","SI_MARKETING_SPEND","SI_COGS_PER_PIECE","SI_CONVERSION_RATES","SI_PNL"]
        df_list = [newsletter_tmp,marketing_spend_tmp,cogs_tmp,conversion_rates_tmp,pnl_tmp]   
        key_value="one"
        for table,data  in zip(table_list, df_list):
            data["VERSION"] = otherOption
            data.to_csv("new.csv",index=False)
            value = kb.keboola_create_update(keboola_URL=st.secrets.kbc_url, 
                        keboola_key=st.secrets.kbc_token, 
                        keboola_table_name=table, 
                        keboola_bucket_id="out.c-ACME_BUM_LFL", 
                        keboola_file_path="new.csv", 
                        keboola_is_incremental= True,
                        keboola_primary_key=["VERSION", "WEEK", "CATEGORY", "SOURCE", "BRAND", "SKU_NAME"],
                        #Button Label
                        label="SEND TO KEBOOLA"+" "+table,
                        # Key is mandatory and has to be unique
                        key=key_value,
                        # if api_only= True than the button is not shown and the api call is fired directly
                        api_only=False
                        )
            value
            key_value +="one"
