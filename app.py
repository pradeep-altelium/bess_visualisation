

import pandas as pd

import psycopg2


from scipy import stats
import streamlit as st

# streamlit_app.py


# Initialize connection.
# Uses st.cache to only run once.
@st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

# Perform query.
# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(allow_output_mutation=True)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()
# def load_Data_from_sql(battery_pack_id):
#     # some options to make dataframes display better on screen:
#     pd.set_option('display.max_columns', None)
#     pd.set_option('expand_frame_repr', False)
#     # print('Getting data from server for battery: ',str(battery_id) )
#     # set up input data connection:
#     # conn_details = ['postgres', 'energylancaster',
#     #                 'database-dapp-prod-01.ciw65t1507ge.eu-west-2.rds.amazonaws.com', 'postgres']
#     # conn = psycopg2.connect(database=conn_details[3], user=conn_details[0],
#     #                         password=conn_details[1], host=conn_details[2], port="5432")
#     # cur = conn.cursor()
#
#     sql_query = 'select *  FROM parsed_data_bess​."Pack_Timeseries" where battery_pack_id=' + battery_pack_id + ' ;'
#     # get all data
#     print('sql_query - 1 : ', sql_query)
#
#     # run the query (can take a while) and bring the results into a dataframe:
#     #df = pd.read_sql(sql_query, conn)
#     df = run_query(sql_query)
#     sql_query2 = 'select *  FROM calculated_data."calculate_data_SOH_bess" where battery_pack_id=' + battery_pack_id + ' ;'
#     print('sql_query - 2: ', sql_query2)
#     df2 = run_query(sql_query2)
#     #df2 = pd.read_sql(sql_query2, conn)
#     # columns_names=df.columns
#     # close the inbound connection:
#     return df, df2  # ,df_bat_details


df_temp_list = []
df_temp_list2 = []
for battery_pack_id in range(501, 507):
    print(battery_pack_id)
    sql_query = 'select *  FROM parsed_data_bess​."Pack_Timeseries" where battery_pack_id=' +battery_pack_id + ' ;'
    sql_query2 = 'select *  FROM calculated_data."calculate_data_SOH_bess" where battery_pack_id=' +battery_pack_id + ' ;'
    df_temp = run_query(sql_query)
    df_temp2 = run_query(sql_query2)
    #df_temp, df_temp2 = load_Data_from_sql(str(battery_pack_id))
    df_temp_list.append(df_temp)
    df_temp_list2.append(df_temp2)

df_all = pd.concat(df_temp_list, ignore_index=True)
df_all_SOH_cal = pd.concat(df_temp_list2, ignore_index=True)
# df_all.columns
# In[ ]: load data

url_bess_specs ='https://raw.githubusercontent.com/pradeep-altelium/bess_visualisation/main/bess_specs.csv'
url_battery_usage_summary = 'https://raw.githubusercontent.com/pradeep-altelium/bess_visualisation/main/Battery_Usage_Summary.csv'
url_battery_health = 'https://raw.githubusercontent.com/pradeep-altelium/bess_visualisation/main/battery_health.csv'
df_specs = pd.read_csv(url_bess_specs,index_col=0)
df_health = pd.read_csv(url_battery_health,index_col=0)
df_usage = pd.read_csv(url_battery_usage_summary,index_col=0)
# df_all=pd.read_csv(r'C:\Users\PanagiotisErodotou\OneDrive - Altelium\Documents\Python Scripts\Altelium_codes\CE\dashboard_bess_fake\df_all.csv')
# df_all.to_csv(r'C:\Users\PanagiotisErodotou\OneDrive - Altelium\Documents\Python Scripts\Altelium_codes\CE\dashboard_bess_fake\df_all.csv')
# print('get min and max and group by id took : ',str((time.time() - start_time)/60)+'minutes')
# In[ ]: START
df_all_soc_grouped = df_all.groupby(['battery_pack_id', 'pack_soc_percent'])['pack_soc_percent'].count()


import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

st.sidebar.image(r'C:\Users\PradeepManickam\OneDrive - Altelium\Documents\Pradeep\DashBoard\ms_almin\logo.svg', use_column_width=True)
page = st.sidebar.selectbox('Select page',
                            ['Overview', 'BESS data', 'Pack data', "Bonus page"])

if page == 'Overview':
    col1, col2, col3 = st.columns([2, 10, 3])
    col2.title("Welcome to BESS Dashboard!")
    f = open(r'C:\Users\PradeepManickam\OneDrive - Altelium\Documents\Pradeep\DashBoard\ms_almin\battery-svgrepo-com.svg', "r")
    lines = f.readlines()
    line_string = ''.join(lines)
    # col2.image(r"C:\Users\PanagiotisErodotou\OneDrive - Altelium\Downloads\battery-svgrepo-com (7).svg", width=60)
    col1.write(line_string, unsafe_allow_html=True, width=60, height=30)

    # st.title("Welcome to BESS Dashboard!")
    st.markdown("### Health overview​")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Battery health", "97 %", "+1.2 %")
    col2.metric("Thermal stability", "73 %", "-8%")
    col3.metric("Fire risk", "15%", "3%")
    col4.metric("Gas alert", "False")

    st.markdown("### BESS Info and Specs")

    st.table(df_specs.assign(hack='').set_index('hack'))

    st.markdown("### Usage Overview")

    st.table(df_usage.reset_index(drop=True).assign(hack='').set_index('hack'))

    st.markdown("### Throughput Overview")
    fig = px.bar(df_all_SOH_cal, x='battery_pack_id', y='throughput_value')
    st.plotly_chart(fig, use_container_width=True, width=900)

    st.markdown("### Battery Packs Health")

    st.table(df_health.assign(hack='').set_index('hack'))

if page == 'Pack data':
    st.markdown("### Pack Monitor")
    num_yrs = st.slider('Select number of days', min_value=1, max_value=580)
    df = df_all.iloc[-num_yrs * 60 * 24:]
    clist = df_all['battery_pack_id'].unique()
    battery_pack_id = st.selectbox("Select a Battery ID:", clist)
    # col1, col2, col3 = st.columns(3)
    # col1 = st.columns(1)
    st.write("Max Temperature")
    fig = px.line(df[df['battery_pack_id'] == battery_pack_id],
                  x="timestamp_utc", y="max_pack_temp_deg_c", title="Max Temperature")
    st.plotly_chart(fig, use_container_width=True, width=900)

    st.write("Max Cell Voltage")
    fig = px.line(df[df['battery_pack_id'] == battery_pack_id],
                  x="timestamp_utc", y="max_cell_voltage_v", title="Max Cell Voltage")
    st.plotly_chart(fig, use_container_width=True)

    st.write("Pack Current")
    fig = px.line(df[df['battery_pack_id'] == battery_pack_id],
                  x="timestamp_utc", y="pack_current_amp", title="Max Cell Voltage")

    st.plotly_chart(fig, use_container_width=True)

if page == 'BESS data':
    st.markdown("### BESS Monitor")
    num_yrs = st.slider('Select number of days', min_value=1, max_value=580)

    df = df_all.iloc[-num_yrs * 60 * 24:]

    fig = px.line(df,
                  x="timestamp_utc", y="max_pack_temp_deg_c",
                  title="Max Temperature", color='battery_pack_id')

    st.plotly_chart(fig, use_container_width=True, width=900)

    fig = px.line(df,
                  x="timestamp_utc", y="max_cell_voltage_v",
                  title="Max Cell Voltage", color='battery_pack_id')
    st.plotly_chart(fig, use_container_width=True, width=900)

    fig = px.line(df,
                  x="timestamp_utc", y="pack_current_amp",
                  title="Current", color='battery_pack_id')
    st.plotly_chart(fig, use_container_width=True, width=900)

if page == "Bonus page":
    st.balloons()
    st.markdown("### Thanks for visiting BESS Dashboard!")

    f = open(r"C:\Users\PanagiotisErodotou\OneDrive - Altelium\Downloads\battery-svgrepo-com (6).svg", "r")
    lines = f.readlines()
    line_string = ''.join(lines)

    col1, col2, col3 = st.columns([10, 15, 10])

    col2.write(line_string, unsafe_allow_html=True, width=60, height=30)