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

st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')

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
#--------------------------------
def top_delivers(df1, top_asc):
    df_aux = (df1.loc[:,['City','Delivery_person_ID','Time_taken(min)']]
                 .groupby(['City','Delivery_person_ID'])
                 .mean()
                 .round(2)
                 .sort_values(['City','Time_taken(min)'], ascending=top_asc)
                 .reset_index())
    df01 = df_aux.loc[df_aux['City'] == 'Metropolitian',:].head(10)
    df02 = df_aux.loc[df_aux['City'] == 'Urban',:].head(10)
    df03 = df_aux.loc[df_aux['City'] == 'Semi-Urban',:].head(10)
    df_aux = pd.concat([df01,df02,df03]).reset_index(drop=True)
    return df_aux
#------------------------------


#=========================================================================================================
#INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO --------------------------------------------------------------------

#Importando/lendo a base de dados
df = pd.read_csv('train.csv')

#Limpeza dos dados
df1 = clean_code(df)


#Barra lateral
#~~~~~~~~~~~~~~

st.header('Marketplace - Visão Entregadores')
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


# Layout Streamlit
#~~~~~~~~~~~~~~~~~

tab1, tab2, tab3 = st.tabs(['visao1', 'visao2', 'visao3'])
with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade',maior_idade)
        with col2:
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade',menor_idade)
        with col3:
            melhor = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição veículos',melhor)
        with col4:
            pior = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição veículos',pior)
    
    
    with st.container():
        st.markdown('''___''')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação Média Por Entregador')
            av_med = (df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                      .groupby('Delivery_person_ID')
                      .mean()
                      .reset_index()
                      .round(2))
            
            st.dataframe(av_med)
            
        with col2:
            st.markdown('##### Avaliação Média Por Transito')
            df_aux = (df1.loc[:,['Road_traffic_density','Delivery_person_Ratings']]
                          .groupby('Road_traffic_density')
                          .agg(['mean','std'])
                          .round(2))
            # mudança do nome das colunas
            df_aux.columns = ['Média','Des.Pad']

            #reset do index
            df_aux.reset_index()
            st.dataframe(df_aux)
            
            st.markdown('##### Avaliação Média Por Clima')
            df_aux = (df1.loc[:,['Weatherconditions','Delivery_person_Ratings']]
                          .groupby('Weatherconditions')
                          .agg(['mean','std'])
                          .round(2))

            # mudança do nome das colunas
            df_aux.columns = ['Média','Des.Pad']

            #reset do index
            df_aux.reset_index()
            st.dataframe(df_aux)
    
    
    with st.container():
        st.markdown('''___''')
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df_aux = top_delivers(df1, top_asc=True)
            st.dataframe(df_aux)
            
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df_aux = top_delivers(df1,top_asc=False)
            st.dataframe(df_aux)