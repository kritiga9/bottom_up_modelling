#importing necessary libraries
import streamlit as st
import pandas as pd
from kbcstorage.client import Client
import duckdb


# Initialize the KBC Storage client using Streamlit secrets
client = Client(st.secrets.url, st.secrets.key) 

# Define a function to read data from KBC Storage and export to a file
@st.experimental_memo(ttl=7200)
def read_df(table_id, index_col=None, date_col=None):
    client.tables.export_to_file(table_id, '.')
    table_name = table_id.split(".")[-1]
    return pd.read_csv(table_name, index_col=index_col, parse_dates=date_col)


# Define a function to read data from KBC Storage and export to a file (segmented)
def read_df_segment(table_id, index_col=None, date_col=None):
    client.tables.export_to_file(table_id, '.')
    table_name = table_id.split(".")[-1]
    return pd.read_csv(table_name, index_col=index_col, parse_dates=date_col)

# Define a function to save a file
def saveFile(uploaded):
    with open(os.path.join(os.getcwd(),uploaded.name),"w") as f:
        strIo= StringIO(uploaded.getvalue().decode("utf-8"))
        f.write(strIo.read())
        return os.path.join(os.getcwd(),uploaded.name)

# Function to check and set session state
def check_and_set_state(ss_key,value):
    if ss_key not in st.session_state:
        st.session_state[ss_key] = value

# Read data from KBC Storage into dataframes
newsletter = read_df('out.c-bum_final.SI_NEWSLETTERS')
marketing_spend = read_df('out.c-bum_final.SI_MARKETING_SPEND')
conversion_rates = read_df('out.c-bum_final.SI_CONVERSION_RATES')
cogs = read_df('out.c-bum_final.SI_COGS_PER_PIECE')
pnl = read_df('out.c-bum_final.SI_PNL')
web_analytics = read_df('out.c-bum_final.web_analytics')
lfl = read_df('out.c-bum_final.BUM_IS_FINAL_REASONABLE')


# Extract unique values for the multiselect option
category = web_analytics["CATEGORY"].unique()
brand = web_analytics["BRAND"].unique()
source = web_analytics["SOURCE_CHANNEL"].unique()

# Create a list of scenario versions for selection
versions =  ["New Scenario"]+[f"{i}" for i in (newsletter[~newsletter["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique())] + [f"{i}" for i in (marketing_spend[~marketing_spend["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique())] 
# Create a selectbox for choosing a version
version_selection = st.selectbox("Select option", options=versions, key="version_selection")


# Allow users to input a scenario name if "New Scenario" is selected, or rename if a version is selected
if version_selection == "New Scenario": 
    otherOption = st.text_input("Name your Scenario",key="new_scenario")
else:
    otherOption = st.text_input("Rename to save as new",value = version_selection,key="new_scenario")


# Create tabs for different sections of the analysis
tab1,tab2,tab3,tab4,tab5,tab6, tab7 = st.tabs(["Newsletters","Marketing Spend","Conversion Rates","COGS","P&L","Results", "Save"])


# Within the "Newsletters" tab
with tab1:
    # Create a copy of the 'newsletter' dataframe
    newsletter_tmp = newsletter.copy()
    category_t1 = newsletter["CATEGORY"].unique() 
    brand_t1 = newsletter["BRAND"].unique()
    source_t1 = newsletter["SOURCE"].unique()
    
    # Extract unique values from specific columns in the 'newsletter' dataframe
    if (version_selection == "New Scenario") or (version_selection not in newsletter[~newsletter["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        # If "New Scenario" or not in the list, filter the dataframe for "LFL" version
        df = newsletter[newsletter["VERSION"]=='LFL']
        newsletter_tmp = newsletter_tmp[newsletter_tmp["VERSION"]=='LFL']

    else:
        # If a specific version is selected, filter the dataframe accordingly
        df = newsletter[newsletter["VERSION"]==version_selection]
        newsletter_tmp = newsletter_tmp[newsletter_tmp["VERSION"]==version_selection]


    # Set or update the session state with the filtered 'newsletter_tmp' dataframe
    check_and_set_state('newsletter_tmp',newsletter_tmp)
    newsletter_ss = st.session_state['newsletter_tmp']

    # Divide the multiselect option into three columns
    column_1,column_2,column_3 = st.columns(3)

    # Within the brand multiselect
    with column_1:
        # Multiselect widget for selecting brands
        brand_selection_t1 = st.multiselect("Brand",brand_t1,brand_t1 )

    # Within the source multiselect
    with column_2:
        # Multiselect widget for selecting source
        source_selection_t1 = st.multiselect("Source",source_t1,source_t1 )

    # Within the category multiselect
    with column_3:
        # Multiselect widget for category
        category_selection_t1 = st.multiselect("Category",category_t1,category_t1)
    
    # Create sliders to adjust 'Newsletters Sent' and 'Sent to PDV Rate'
    tab_11 = st.slider("Newsletters Sent",-100,100,0)
    tab_12 = st.slider("Sent to PDV Rate",-100,100,0)

    # Update the 'NEWSLETTERS_SENT' and 'SENT_TO_PDV_RATE' columns in the dataframe based on slider values
    df["NEWSLETTERS_SENT"] = df["NEWSLETTERS_SENT"]*(1 + tab_11/100)     
    df["SENT_TO_PDV_RATE"] = df["SENT_TO_PDV_RATE"]*(1 + tab_12/100) 

     # Convert 'NEWSLETTERS_SENT' to integer
    df["NEWSLETTERS_SENT"] = df["NEWSLETTERS_SENT"].astype(int) 

    # Filter the dataframe based on brand, category, and source selections  
    df= df[ ( df["BRAND"].isin(brand_selection_t1)) & (df["CATEGORY"].isin(category_selection_t1)) & (df["SOURCE"].isin(source_selection_t1))]      
    
    # Display the filtered dataframe columns in a table
    st.write(df[["WEEK","BRAND","CATEGORY","SOURCE","NEWSLETTERS_SENT","SENT_TO_PDV_RATE"]])

    # Create a button to save the applied filters
    save_state_t1 = st.button("Save filters")

    # If the "Save filters" button is clicked
    if save_state_t1:
        # Update the session state with the filtered 'NEWSLETTERS_SENT' and 'SENT_TO_PDV_RATE' values
        newsletter_ss.loc[newsletter_ss.index.isin(df.index), ['NEWSLETTERS_SENT']]= df['NEWSLETTERS_SENT'] 
        newsletter_ss.loc[newsletter_ss.index.isin(df.index), ['SENT_TO_PDV_RATE']]= df['SENT_TO_PDV_RATE']
      



# Within the "Marketing Spend" tab
with tab2:
    # Create a copy of the "marketing spend" dataframe
    marketing_spend_tmp = marketing_spend.copy()
    # Extract unique values from specific columns in the 'marketing_spend' dataframe
    category_t2 = marketing_spend["CATEGORY"].unique() 
    brand_t2 = marketing_spend["BRAND"].unique()
    source_t2= marketing_spend["SOURCE"].unique()

    # Check if the selected version is "New Scenario" or not in the list of unique versions
    if (version_selection == "New Scenario") or (version_selection not in marketing_spend[~marketing_spend["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        # If "New Scenario" or not in the list, filter the dataframe for "LFL" version
        df = marketing_spend[marketing_spend["VERSION"]=='LFL']
        marketing_spend_tmp = marketing_spend_tmp[marketing_spend_tmp["VERSION"]=='LFL']

    else:
         # If a specific version is selected, filter the dataframe accordingly
        df = marketing_spend[marketing_spend["VERSION"]==version_selection]
        marketing_spend_tmp = marketing_spend_tmp[marketing_spend_tmp["VERSION"]==version_selection]

    # Set or update the session state with the filtered 'marketing_spend_tmp' dataframe
    check_and_set_state('marketing_spend_tmp',marketing_spend_tmp)
    marketing_spend_ss = st.session_state['marketing_spend_tmp']
    
    # Divide the multiselect option into 3 columns
    column_4,column_5,column_6 = st.columns(3)

    # Within the brand multiselect
    with column_4:
        # Create a multiselect widget for selecting brands
        brand_selection_t2 = st.multiselect("Brand ",brand_t2,brand_t2 )

    # Within the source multiselect
    with column_5:
        # Create a multiselect widget for selecting sources
        source_selection_t2 = st.multiselect("Source ",source_t2,source_t2 )

    # Within the category multiselect
    with column_6:
        # Create a multiselect widget for selecting category
        category_selection_t2 = st.multiselect("Category ",category_t2,category_t2)


    # Create sliders to adjust 'Spend' and 'Cost Per Click'
    tab_21 = st.slider(
                'Spend',
                 -100,100,0)
    tab_22= st.slider(
                'Cost Per click ',
                 -100, 100,0)

    # Update the 'SPEND' and 'COST_PER_CLICK' columns in the dataframe based on slider values
    df["SPEND"] = df["SPEND"]*(1 + tab_21/100)      
    df["COST_PER_CLICK"] = df["COST_PER_CLICK"]*(1 + tab_22/100) 

    # Convert 'SPEND' to integer
    df["SPEND"] = df["SPEND"].astype(int)  

    # Filter the dataframe based on brand, category, and source selections
    df= df[ ( df["BRAND"].isin(brand_selection_t2)) & (df["CATEGORY"].isin(category_selection_t2)) & (df["SOURCE"].isin(source_selection_t2))]        
    
    # Display the filtered dataframe columns in a table (excluding 'VERSION' column)
    st.write(df.loc[:, ~df.columns.isin(['VERSION'])])

    # Create a button to save the applied filters
    save_state_t2 = st.button("Save filters ")

    # If the "Save filters" button is clicked
    if save_state_t2:
        # Update the session state with the filtered 'SPEND' and 'COST_PER_CLICK' values
        marketing_spend_ss.loc[marketing_spend_ss.index.isin(df.index), ['SPEND']]= df[['SPEND']] 
        marketing_spend_ss.loc[marketing_spend_ss.index.isin(df.index), ['COST_PER_CLICK']]= df[['COST_PER_CLICK']] 
           
     
# Within the "Conversion Rates" tab
with tab3:
    # Create a copy of the 'conversion_rates' dataframe
    conversion_rates_tmp = conversion_rates.copy()

    # Extract unique values from specific columns in the 'conversion_rates' dataframe
    category_t3= conversion_rates["CATEGORY"].unique() 
    brand_t3 = conversion_rates["BRAND"].unique()
    source_t3= conversion_rates["SOURCE"].unique()

    # Check if the selected version is "New Scenario" or not in the list of unique versions
    if (version_selection == "New Scenario") or (version_selection not in conversion_rates[~conversion_rates["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        # If "New Scenario" or not in the list, filter the dataframe for "LFL" version
        df = conversion_rates[conversion_rates["VERSION"]=='LFL']
        conversion_rates_tmp = conversion_rates_tmp[conversion_rates_tmp["VERSION"]=='LFL']

    else:
        df = conversion_rates[conversion_rates["VERSION"]==version_selection]
        conversion_rates_tmp = conversion_rates_tmp[conversion_rates_tmp["VERSION"]==version_selection]

    # Set or update the session state with the filtered 'conversion_rates_tmp' dataframe
    check_and_set_state('conversion_rates_tmp',conversion_rates_tmp)
    conversion_rates_ss = st.session_state['conversion_rates_tmp']

    # Divide the multiselect option into 3 columns
    column_7,column_8,column_9 = st.columns(3)

    # Within the brand multiselect
    with column_7:
        # Create a multiselect widget for selecting brands
        brand_selection_t3 = st.multiselect(" Brand",brand_t3,brand_t3 )

    # Within the source multiselect
    with column_8:
        # Create a multiselect widget for selecting sources
        source_selection_t3 = st.multiselect(" Source",source_t3,source_t3 )

    # Within the category multiselect
    with column_9:
        # Create a multiselect widget for selecting category
        category_selection_t3 = st.multiselect(" Category",category_t3,category_t3)


    # Create a slider to adjust 'Purchase to PDV rate'
    tab_31= st.slider(
                'Purchase to PDV rate',
                 -100, 100,0) 

    # Update the 'PURCHASE_TO_PDV_RATE' column in the dataframe based on slider value
    df["PURCHASE_TO_PDV_RATE"] = df["PURCHASE_TO_PDV_RATE"]*(1 + tab_31/100) 
    
    # Filter the dataframe based on brand, category, and source selections 
    df= df[( df["BRAND"].isin(brand_selection_t3)) & (df["CATEGORY"].isin(category_selection_t3)) & (df["SOURCE"].isin(source_selection_t3))]        
    
    # Display the filtered dataframe columns in a table (excluding 'VERSION' column)
    st.write(df.loc[:, ~df.columns.isin(['VERSION'])])   
    
    # Create a button to save the applied filters
    save_state_t3 = st.button("Save filters.")

    # If the "Save filters" button is clicked
    if save_state_t3:
        # Update the session state with the filtered 'PURCHASE_TO_PDV_RATE' values
        conversion_rates_ss.loc[conversion_rates_ss.index.isin(df.index), ['PURCHASE_TO_PDV_RATE']]= df[['PURCHASE_TO_PDV_RATE']] 
  
# Within the "COGS" (Cost of Goods Sold) tab
with tab4:    
    # Create a copy of the 'cogs' dataframe
    cogs_tmp = cogs.copy() 

    # Extract unique values from specific columns in the 'cogs' dataframe
    category_t4= cogs["CATEGORY"].unique() 
    brand_t4 = cogs["BRAND"].unique()
    source_t4= cogs["SOURCE"].unique()

    # Check if the selected version is "New Scenario" or not in the list of unique versions
    if (version_selection == "New Scenario") or (version_selection not in cogs[~cogs["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        # If "New Scenario" or not in the list, filter the dataframe for "LFL" version
        df = cogs[cogs["VERSION"]=='LFL']
        cogs_tmp = cogs_tmp[cogs_tmp["VERSION"]=='LFL']
    else:
        # If a specific version is selected, filter the dataframe accordingly
        df = cogs[cogs["VERSION"]==version_selection]
        cogs_tmp = cogs_tmp[cogs_tmp["VERSION"]==version_selection]

    # Set or update the session state with the filtered 'cogs_tmp' dataframe
    check_and_set_state('cogs_tmp',cogs_tmp)
    cogs_ss = st.session_state['cogs_tmp']
    
    # Divide the multiselect option into 3 columns
    column_10,column_11,column_12 = st.columns(3)

    # Within the brand multiselect
    with column_10:
        # Create a multiselect widget for selecting brands
        brand_selection_t4 = st.multiselect("Brand  ",brand_t4,brand_t4 )

    # Within the source multiselect
    with column_11:
        # Create a multiselect widget for selecting sources
        source_selection_t4 = st.multiselect("Source  ",source_t4,source_t4 )

    # Within the category multiselect
    with column_12:
        # Create a multiselect widget for selecting categories
        category_selection_t4 = st.multiselect("Category  ",category_t4,category_t4)

    

    # Create a slider to adjust 'COGS per piece'
    tab_42 = st.slider(
                'COGS per piece',
                 -100, 100,0) 

    # Update the 'COGS_PER_PIECE' column in the dataframe based on slider value (rounded to 2 decimal places)
    df["COGS_PER_PIECE"] = (df["COGS_PER_PIECE"]*(1 + tab_42/100)   ).round(2)  

    # Filter the dataframe based on brand, category, and source selections
    df= df[( df["BRAND"].isin(brand_selection_t4)) & (df["CATEGORY"].isin(category_selection_t4)) & (df["SOURCE"].isin(source_selection_t4))]        

    # Display the filtered dataframe columns in a table
    st.write(df[["WEEK","BRAND","CATEGORY","SOURCE","SKU_NAME","COGS_PER_PIECE","WEIGHT_BY_PIECES_SOLD"]])

    # Create a button to save the applied filters
    save_state_t4 = st.button("Save Filter")
    
    # If the "Save Filter" button is clicked
    if save_state_t4:
        # Update the session state with the filtered 'COGS_PER_PIECE' values
        cogs_ss.loc[cogs_ss.index.isin(df.index), ['COGS_PER_PIECE']]= df[['COGS_PER_PIECE']] 


# Within the "P&L" (Profit and Loss) tab
with tab5:
    # Create a copy of the 'pnl' (Profit and Loss) dataframe
    pnl_tmp = pnl.copy() 

    # Extract unique values from specific columns in the 'pnl' dataframe
    category_t5= pnl["CATEGORY"].unique() 
    brand_t5 = pnl["BRAND"].unique()
    source_t5= pnl["SOURCE"].unique()

    # Check if the selected version is "New Scenario" or not in the list of unique versions
    if (version_selection == "New Scenario") or (version_selection not in pnl[~pnl["VERSION"].isin(["LFL","FINAL"])]["VERSION"].unique()):
        # If "New Scenario" or not in the list, filter the dataframe for "LFL" version
        df = pnl[pnl["VERSION"]=='LFL']
        pnl_tmp = pnl_tmp[pnl_tmp["VERSION"]=='LFL']
    else:
        # If a specific version is selected, filter the dataframe accordingly
        df = pnl[pnl["VERSION"]==version_selection]
        pnl_tmp = pnl_tmp[pnl_tmp["VERSION"]==version_selection]
    
    # Set or update the session state with the filtered 'pnl_tmp' dataframe
    check_and_set_state('pnl_tmp',pnl_tmp)
    pnl_ss = st.session_state['pnl_tmp']
    
    
    # Divide the multiselect option into 3 columns
    column_13,column_14,column_15 = st.columns(3)

    # Within the brand multiselect
    with column_13:
        brand_selection_t5 = st.multiselect("Brand   ",brand_t5,brand_t5 )

    # Within the source multiselect
    with column_14:
        source_selection_t5 = st.multiselect("Source   ",source_t5,source_t5 )

    # Within the category multiselect
    with column_15:
        category_selection_t5 = st.multiselect("Category   ",category_t5,category_t5)


    # Create sliders to adjust various price and bonus parameters
    tab_51= st.slider(
                'Price per piece ',
                 -100,100,0) 
    tab_52 = st.slider(
                'Bonus per piece',
                 -100, 100,0) 
    tab_53 = st.slider(
                'Bonus as PCT COGS',
                 -100,100,0) 

    # Update the relevant columns in the dataframe based on slider values
    df["PRICE_PER_PIECE"] = (df["PRICE_PER_PIECE"]*(1 + tab_51/100))    
    df["BONUS_PER_PIECE"] = df["BONUS_PER_PIECE"]*(1 + tab_52/100)      
    df["BONUS_AS_PCT_COGS"] = df["BONUS_AS_PCT_COGS"]*(1 + tab_53/100)     
    
    # Filter the dataframe based on brand, category, and source selections
    df= df[ ( df["BRAND"].isin(brand_selection_t5)) & (df["CATEGORY"].isin(category_selection_t5)) & (df["SOURCE"].isin(source_selection_t5))]        

    # Display the filtered dataframe columns in a table (excluding 'VERSION' column)
    st.write(df.loc[:, ~df.columns.isin(['VERSION'])])

    # Create a button to save the applied filters
    save_state_t5 = st.button("Save Filter.")
    
    # If the "Save Filter" button is clicked
    if save_state_t5:
        # Update the session state with the filtered values for price, bonus, and bonus as a percentage of COGS
        pnl_ss.loc[pnl_ss.index.isin(df.index), ['PRICE_PER_PIECE']]= df[['PRICE_PER_PIECE']] 
        pnl_ss.loc[pnl_ss.index.isin(df.index), ['BONUS_PER_PIECE']]= df[['BONUS_PER_PIECE']] 
        pnl_ss.loc[pnl_ss.index.isin(df.index), ['BONUS_AS_PCT_COGS']]= df[['BONUS_AS_PCT_COGS']] 




# Within the "Results" tab
with tab6:
    # Create temporary dataframes for various data sources
    SI_NEWSLETTERS_TMP = newsletter_ss
    SI_MARKETING_SPEND_TMP =marketing_spend_ss
    WEB_ANALYTICS_TMP = web_analytics
    SI_COGS_PER_PIECE_TMP = cogs_ss
    SI_CONVERSION_RATES_TMP = conversion_rates_ss
    SI_PNL_TMP = pnl_ss
    
    
    # Define a query to calculate results based on the selected data
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
    SPEND/ COST_PER_CLICK AS PRODUCT_DETAIL_VIEWS
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
    WHERE SOURCE = 'SEARCH' 
    GROUP BY VERSION, WEEK, BRAND,CATEGORY,SOURCE     
),

COGS AS (
SELECT 
VERSION,
WEEK,
BRAND,
CATEGORY,
SOURCE,
SUM(COGS_PER_PIECE * WEIGHT_BY_PIECES_SOLD) AS COGS_PER_PIECE
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
MS.SPEND AS MARKETING_SPEND,
WT.PRODUCT_DETAIL_VIEWS * CR.PURCHASE_TO_PDV_RATE AS PIECES_SOLD,
(WT.PRODUCT_DETAIL_VIEWS * CR.PURCHASE_TO_PDV_RATE) * PNL.PRICE_PER_PIECE AS REVENUE,
(WT.PRODUCT_DETAIL_VIEWS * CR.PURCHASE_TO_PDV_RATE) * COGS.COGS_PER_PIECE AS COGS,
(WT.PRODUCT_DETAIL_VIEWS * CR.PURCHASE_TO_PDV_RATE) * PNL.BONUS_PER_PIECE AS BONUS_PER_PIECE,
((WT.PRODUCT_DETAIL_VIEWS * CR.PURCHASE_TO_PDV_RATE) * COGS.COGS_PER_PIECE)*PNL.BONUS_AS_PCT_COGS AS BONUS_AS_PCT_COGS


FROM WEB_TRAFFIC AS WT
LEFT JOIN SI_MARKETING_SPEND_TMP AS MS ON WT.VERSION = MS.VERSION AND WT.WEEK = MS.WEEK AND WT.BRAND = MS.BRAND AND WT.CATEGORY = MS.CATEGORY AND WT.SOURCE = MS.SOURCE 
LEFT JOIN SI_CONVERSION_RATES_TMP AS CR ON WT.VERSION = CR.VERSION AND WT.WEEK = CR.WEEK AND WT.BRAND = CR.BRAND AND WT.CATEGORY = CR.CATEGORY AND WT.SOURCE = CR.SOURCE
LEFT JOIN SI_PNL_TMP AS PNL ON WT.VERSION = PNL.VERSION AND WT.WEEK = PNL.WEEK AND WT.BRAND = PNL.BRAND AND WT.CATEGORY = PNL.CATEGORY AND WT.SOURCE = PNL.SOURCE 
LEFT JOIN COGS ON WT.VERSION = COGS.VERSION AND WT.WEEK = COGS.WEEK AND WT.BRAND = COGS.BRAND AND WT.CATEGORY = COGS.CATEGORY AND WT.SOURCE = COGS.SOURCE 
""" ).to_df())

    # Check if the selected version is "New Scenario"
    if version_selection == "New Scenario":
        df_result["VERSION"] = otherOption
    else :
        df_result["VERSION"] = version_selection

    # Aggregate the calculated metrics and create a summary dataframe
    df_agg = pd.DataFrame(df_result.sum(numeric_only=True)).T.drop(columns=["WEEK"])
    df_agg["VERSION"] = df_result["VERSION"].unique()

    # Extract LFL (Last Full Year) data and calculate its summary
    lfl = lfl[lfl["VERSION"]=="LFL"]
    lfl_agg = pd.DataFrame(lfl.sum(numeric_only=True)).T.drop(columns=["ROW_COUNT","GROSS_MARGIN_3"])
    lfl_agg["VERSION"] = 'LFL'

    # Concatenate LFL summary and the calculated summary for selected version
    df_final = pd.concat([lfl_agg,df_agg])

    # Select specific columns for the final output dataframe
    df_final = df_final[["VERSION","PRODUCT_DETAIL_VIEWS","MARKETING_SPEND","PIECES_SOLD","REVENUE","COGS","BONUS_PER_PIECE","BONUS_AS_PCT_COGS"]]

    # Convert certain columns to integers
    df_final[["PRODUCT_DETAIL_VIEWS","MARKETING_SPEND","PIECES_SOLD","REVENUE","COGS","BONUS_PER_PIECE","BONUS_AS_PCT_COGS"]] =         df_final[["PRODUCT_DETAIL_VIEWS","MARKETING_SPEND","PIECES_SOLD","REVENUE","COGS","BONUS_PER_PIECE","BONUS_AS_PCT_COGS"]].astype(int)

    # Calculate additional metrics related to gross margin
    df_final["GROSS_MARGIN_1"] = df_final["REVENUE"] - df_final["COGS"]
    df_final["GROSS_MARGIN_2"] = df_final["GROSS_MARGIN_1"] + df_final["BONUS_PER_PIECE"] + df_final["BONUS_AS_PCT_COGS"]
    df_final["GROSS_MARGIN_3"] = df_final["GROSS_MARGIN_2"] - df_final["MARKETING_SPEND"]

    # Display the final dataframe with calculated metrics
    st.write(df_final)


    # Plot the difference between the selected version and LFL model
    fig_df = pd.DataFrame(df_final._get_numeric_data().diff()[-1:].T.reset_index())
    fig_df = fig_df.rename(columns={ fig_df.columns[0]: "Metrics", fig_df.columns[1] : "Values" })
    fig=px.bar(fig_df,x='Values',y='Metrics', orientation='h')
    st.write(fig)


    # Plot the percentage difference between the selected version and LFL model
    fig_df = pd.DataFrame(df_final._get_numeric_data().pct_change()[-1:].T.reset_index())
    fig_df = fig_df.rename(columns={ fig_df.columns[0]: "Metrics", fig_df.columns[1] : "Values" })
    fig=px.bar(fig_df,x='Values',y='Metrics', orientation='h')
    st.write(fig)


    # Function to convert the dataframe to CSV format
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    # Convert the result dataframe to CSV format and provide a download button
    csv = convert_df(df_result)

    st.download_button(
    "Press to Download",
    csv,
    "file.csv",
    "text/csv",
    key='download-csv'
    )

 
# Within the "Save" tab
with tab7:       
    # Check if the selected version is "New Scenario"
    if (version_selection == "New Scenario"):
        # Define a list of table names and their corresponding dataframes
        table_list = ["SI_NEWSLETTERS","SI_MARKETING_SPEND","SI_COGS_PER_PIECE","SI_CONVERSION_RATES","SI_PNL"]
        df_list = [newsletter_tmp,marketing_spend_tmp,cogs_tmp,conversion_rates_tmp,pnl_tmp]   

        # Initialize a key value
        key_value="one"

        # Iterate over the table list and dataframes
        for table,data  in zip(table_list, df_list):
            # Set the "VERSION" column to the selected scenario name
            data["VERSION"] = otherOption

            # Save the dataframe to a CSV file named "new.csv"
            data.to_csv("new.csv",index=False)
            
            # Use the keboola_create_update function to send the data to Keboola
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

            # Increment the key value for the next iteration
            key_value +="one"
