import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲')

#logo_caminho = '/Users/Tatah/Documents/curry.png'
logo = Image.open( 'curry.png' )
st.sidebar.image( logo, width=300 )

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fasted Delivery in Town')
st.sidebar.markdown('''_____''')

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento do entregadores e restaurantes.
    ### Como utilizar este Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento
        - Visão Tática: Indicadores semanais de crescimento
        - Visão Geográfica: Insights de geolocalização
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurantes:
        - Indicadores semanais de crescimentos dos restaurantes
    ##### Ask for help
        - Time eu mesma no canal do Discord
        @Thalita
""")