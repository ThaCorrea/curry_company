#=========================================================================================================
# BIBLIOTECAS --------------------------------------------------------------------------------------------

from streamlit_folium import folium_static
from haversine import haversine
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
import folium

st.set_page_config(page_title='Visão Empresa', page_icon='📉', layout='wide')

#=========================================================================================================
#FUNÇÕES -------------------------------------------------------------------------------------------------

def clean_code(df1):
    
    """ Esta função é responsável pela limpeza da base.
    1. Remover de strings/object espaços extras no início e no fim;
    1.2 Revomer texto específico de uma coluna númerica: '24 (min)' -> 24;
    2. Remover os valores vazios de algumas colunas (NaN, Null, Nulo, Vazio, NA,...);
    3. Alterar o tipo de dado de algumas das colunas 
    
    Input: Dataframe
    Output: Dataframe """
    #1. 
    df1['ID'] = df1['ID'].str.strip()
    df1['Delivery_person_ID'] = df1['Delivery_person_ID'].str.strip()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].str.strip()
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].str.strip()
    df1['Order_Date'] = df1['Order_Date'].str.strip()
    df1['Time_Orderd'] = df1['Time_Orderd'].str.strip()
    df1['Time_Order_picked'] = df1['Time_Order_picked'].str.strip()
    df1['Weatherconditions'] = df1['Weatherconditions'].str.strip()
    df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()
    df1['Type_of_order'] = df1['Type_of_order'].str.strip()
    df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.strip()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].str.strip()
    df1['Festival'] = df1['Festival'].str.strip()
    df1['City'] = df1['City'].str.strip()
    
    #1.2
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.strip('(min) ')
    
    #2. 
    linhas_idade = df1['Delivery_person_ID'] != 'NaN'
    linhas_ranking = df1['Delivery_person_Ratings'] != 'NaN'
    linhas_data = df1['Order_Date'] != 'NaN'
    linhas_tempo = df1['Time_taken(min)'] != 'NaN'
    linhas_trafego = df1['Road_traffic_density'] !='NaN'
    linhas_cidades = df1['City'] != 'NaN'

    df1 = df1.loc[linhas_idade,:].copy()
    df1 = df1.loc[linhas_ranking,:].copy()
    df1 = df1.loc[linhas_data,:].copy()
    df1 = df1.loc[linhas_tempo,:].copy()
    df1 = df1.loc[linhas_trafego,:].copy()
    df1 = df1.loc[linhas_cidades,:].copy()

    #3. 
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1
#-------------------------------------------
def order_date(df1):
            cols = ['ID','Order_Date']
            df_aux = df1.loc[:,cols].groupby('Order_Date').count().reset_index()
            graf = px.bar(df_aux, x='Order_Date', y='ID')
            return graf
#-----------------------------------------
def traffic_share(df1):
            df_aux = df1.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            df_aux['Entregas_perc'] = df_aux['ID']/df_aux['ID'].sum()
            graf = px.pie(df_aux, values='Entregas_perc', names='Road_traffic_density')
            return graf
#-----------------------------------------       
def traffic_city(df1):
            cols = ['ID','City','Road_traffic_density']
            df_aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).count().reset_index()
            graf = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            return graf
#-----------------------------------------
def order_by_week(df1):
            df1['Week_of_Year'] = df1['Order_Date'].dt.strftime('%U')
            df_aux = df1.loc[:,['ID','Week_of_Year']].groupby('Week_of_Year').count().reset_index()
            graf = px.line(df_aux, x='Week_of_Year', y='ID')
            return graf
#-----------------------------------------
def share_week(df1):
            df_aux1 = df1.loc[:,['ID','Week_of_Year']].groupby('Week_of_Year').count().reset_index() #qnt de pedidos por semana
            df_aux2 = df1.loc[:,['Delivery_person_ID','Week_of_Year']].groupby('Week_of_Year').nunique().reset_index() #qnt de entregadores na semana
            df_aux = pd.merge(df_aux1, df_aux2, how='inner')
            df_aux['Order_by_Delivery'] = (df_aux['ID']/df_aux['Delivery_person_ID']).round(2)
            graf = px.line(df_aux, x='Week_of_Year', y='Order_by_Delivery')
            return graf
#----------------------------------------
def country_maps(df1):
        cols = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
        df_aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).median().reset_index()
        map = folium.Map()
        for index, location_info in df_aux.iterrows():
              folium.Marker([location_info['Delivery_location_latitude'],location_info['Delivery_location_longitude']], popup=location_info[['City','Road_traffic_density']]).add_to(map)
        folium_static(map, width=1024,height=600)
        return None



#=========================================================================================================
#INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO --------------------------------------------------------------------

#Importando/lendo a base de dados
df = pd.read_csv('train.csv')

#Limpeza dos dados
df1 = clean_code(df)


#Barra lateral
#~~~~~~~~~~~~~~

st.header('Marketplace - Visão Cliente')
#logo_caminho = '/Users/Tatah/Documents/curry.png'
logo = Image.open( 'curry.png' )
st.sidebar.image( logo, width=300 )
st.sidebar.markdown('# Curry Company')


st.sidebar.markdown('## Fasted Delivery in Town')
st.sidebar.markdown('''_____''')

st.sidebar.markdown('### Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime( 2022, 4, 13 ),
    min_value=pd.datetime(2022, 2, 11 ),
    max_value=pd.datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY')
    
st.sidebar.markdown('''____''')


trafego = st.sidebar.multiselect('Qual o tráfego?',
                                 ['Low', 'Medium', 'High', 'Jam'],
                                 default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown('''____''')
st.sidebar.markdown('Powered by Thalita - Comunidade DS')

#filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(trafego)
df1 = df1.loc[linhas_selecionadas,:]




# LAYOUT STREAMLIT
#~~~~~~~~~~~~~~~~~~

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        st.header('Orders by Day')
        graf = order_date(df1)
        st.plotly_chart(graf, use_container_width=True)
        st.markdown('''___''')

    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.header('Traffic Order Share')
            graf = traffic_share(df1)
            st.plotly_chart(graf, use_container_width=True)
                    
        with col2:
            st.header('Traffic Order City')
            graf = traffic_city(df1)
            st.plotly_chart(graf, use_container_width=True)
            

with tab2:
    with st.container():
        st.header('Order by Week')
        graf = order_by_week(df1)
        st.plotly_chart(graf, use_container_width=True)
        
    with st.container():
        st.header('Order Share by Week')
        graf = share_week(df1)
        st.plotly_chart(graf, use_container_width=True)
        

with tab3:
    st.header('Country Maps')
    country_maps(df1)