#=========================================================================================================
# BIBLIOTECAS --------------------------------------------------------------------------------------------

from streamlit_folium import folium_static
from haversine import haversine
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
import folium

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍛', layout='wide')

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
#------------------------------
def distance(df1,fig):
    cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df1['Distance'] = df1.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),         (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1).round(2)
    
    if fig == False:
        df_aux = df1['Distance'].mean().round(2)
        return df_aux
    
    else:
        df_aux = df1.loc[:,['City','Distance']].groupby('City').mean().reset_index().round(2)
        fig = go.Figure(data=[go.Pie(labels=df_aux['City'], values=df_aux['Distance'],pull=[0,0,0.03])])
        return fig
#-----------------------------
def avg_std_time_delivery(df1,yn,op):
    """Esta função calcula a média ou o desvio padrão do tempo de entregas
        Parâmetros:
            Input: 
             -df: Dataframe com os dados necessários para o calculo
             -yn: Realiza os calculos em dias com festivais ou sem festivais
                  'Yes': com festival
                  'No': sem festival
             -op: Tipo de operação a ser realizada.
                  'avg_time': calculará a média dos tempos
                  'std_time': calculará o desvio padrão dos tempos"""
            
    df_aux = df1.loc[:,['Time_taken(min)','Festival']].groupby('Festival').agg(['mean', 'std'])
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = df_aux.loc[df_aux['Festival'] == yn,op].round(2)
    return df_aux
#-----------------------------
def avg_std_time_graf(df1):
    df_aux = df1.loc[:,['City', 'Time_taken(min)']].groupby('City').agg(['mean','std']).round(2)
    df_aux.columns = ['Média', 'Desv.Pad']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x = df_aux['City'], y = df_aux['Média'], error_y = dict(type='data', array=df_aux['Desv.Pad'])))

    fig.update_layout(barmode='group')
    return fig
#-----------------------------
def avg_std_time_traffic(df1):
    df_aux = df1.loc[:,['City','Road_traffic_density','Delivery_person_Ratings']].groupby(['City','Road_traffic_density']).agg(['mean','std']).round(2)
    df_aux.columns = ['Média','Desv.Pad']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path= ['City','Road_traffic_density'], values= 'Média', color = 'Desv.Pad', color_continuous_scale='Portland', color_continuous_midpoint= np.average(df_aux['Desv.Pad']))
    return fig



#=========================================================================================================
#INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO --------------------------------------------------------------------

#Importando/lendo a base de dados
df = pd.read_csv('train.csv')

#Limpeza dos dados
df1 = clean_code(df)


#Barra lateral
#~~~~~~~~~~~~~~

st.header('Marketplace - Visão Restaurantes')
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
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            qnt_entregadores = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregadores',qnt_entregadores)
            
        with col2:
            df_aux = distance(df1,fig=False)
            col2.metric('Distância média',df_aux)

        with col3:
            df_aux = avg_std_time_delivery(df1,yn='Yes',op='avg_time')
            col3.metric('Avg c/ Festivais',df_aux)
            
        with col4:
            df_aux = avg_std_time_delivery(df1,yn='Yes',op='std_time')
            col4.metric('Sdt c/ Festivais',df_aux)
            
        with col5:
            df_aux = avg_std_time_delivery(df1,yn='No',op='avg_time')
            col5.metric('Avg s/ Festivais',df_aux)
            
        with col6:
            df_aux = avg_std_time_delivery(df1,yn='No',op='avg_time')
            col6.metric('Sdt s/ Festivais',df_aux)
    
    with st.container():
        st.markdown('''___''')
        col1, col2 = st.columns(2)
        
        with col1:
            fig = avg_std_time_graf(df1)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            df_aux = df1.loc[:,['City','Type_of_order','Delivery_person_Ratings']].groupby(['City','Type_of_order']).agg(['mean', 'std']).round(2)
            df_aux.columns = ['Média','Desv.Pad']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux, use_container_width=True)

        
    
    with st.container():
        st.markdown('''___''')
        st.title('Distribuição do Tempo')
        col1, col2 = st.columns(2)
        
        with col1:
            fig = distance(df1,fig=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = avg_std_time_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)