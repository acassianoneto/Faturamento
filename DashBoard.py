import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

def formatar_numero(valor, prefixo = ''):
    for unidade in ['', 'MIL']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} M'

st.title('DASHBOARD DE VENDA :shopping_trolley:')

url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')
## TABELAS

receita_estado = dados.groupby('Local da compra')[['Preço']].sum()
receita_estado = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].\
    merge(receita_estado, left_on = 'Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

## GRAFICOS
fig_receita_estados = px.bar(receita_estado.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto=True,
                             title='Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categoria,
                                text_auto=True,
                                title='Rceita pro categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')


fig_mapa_receita = px.scatter_geo(receita_estado,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Preço',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat':False,'lon':False},
                                   title = 'Receita por Estado')

fig_receita_mensal = px.line(receita_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0,receita_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Receita Mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')


## VISUALIZAÇÃO
coluna1, coluna2 = st.columns(2)

with coluna1:
    st.metric('Receita', formatar_numero(dados['Preço'].sum(), 'R$'))
    st.plotly_chart(fig_mapa_receita, user_container_width=True)
    st.plotly_chart(fig_receita_estados, user_container_width=True)

with coluna2:
    st.metric('Quantidade de venda', formatar_numero(dados.shape[0]))
    st.plotly_chart(fig_receita_mensal, user_container_width=True)
    st.plotly_chart(fig_receita_categorias, user_container_width=True)

st.dataframe(dados)


#if __name__ == '__main__':
#    os.system('streamlit run DashBoard.py')
