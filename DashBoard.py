# noinspection PyPackageRequirements
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Adicione o seguinte código CSS
st.markdown(
    """
    <style>
    .stApp {
        max-width: 1000px;
        margin: 0 auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# st.set_page_config(layout='wide')


def formatar_numero(valor, prefixo=''):
    for unidade in ['', 'MIL']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} M'


st.title('DASHBOARD DE VENDA :shopping_trolley:')
url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')
dados['MesAno'] = dados['Data da Compra'].dt.strftime('%m/%Y')

query = """

    
"""

# region TABELAS
receita_estado = dados.groupby('Local da compra')[['Preço']].sum()
receita_estado = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].\
    merge(receita_estado, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

qtd_vendas_estado = dados.groupby('Local da compra')[['Preço']].count()
qtd_vendas_estado = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].\
    merge(qtd_vendas_estado, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

qtd_vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].count().reset_index()
qtd_vendas_mensal['Ano'] = qtd_vendas_mensal['Data da Compra'].dt.year
qtd_vendas_mensal['Mes'] = qtd_vendas_mensal['Data da Compra'].dt.month_name()

receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)
qtd_vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False)

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))
# endregion

# region FILTROS
filtro_competencia = dados['MesAno'].unique()
# filtro_competencia = filtro_competencia.set_index('MesAno').groupby(pd.Grouper(freq='M'))['MesAno'].
filtro_competencia = st.sidebar.multiselect("Selecione a a Competência",
                                            filtro_competencia,
                                            key="MesAno")
# Armazenando o estado dos filtros
if 'filtros' not in st.session_state:
    st.session_state.filtros = {
        'MesAno': filtro_competencia
    }
# Aplicando os filtros
dados_filtrados = dados.copy()
if filtro_competencia:
    dados_filtrados = dados_filtrados[dados_filtrados['MesAno'].isin(filtro_competencia)]

# Atualizando filtros selecionados
filtro_competencia = st.session_state.filtros['MesAno']

# Exibindo os filtros selecionados
if filtro_competencia:
    st.sidebar.markdown(f"**Filtro de MêsAno:** {', '.join(filtro_competencia)}")
# endregion

# region GRAFICOS
fig_receita_estados = px.bar(receita_estado.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto=True,
                             title='Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title='Receita')

fig_receita_categorias = px.bar(receita_categoria,
                                text_auto=True,
                                title='Rceita pro categoria')
fig_receita_categorias.update_layout(yaxis_title='Receita')

fig_qtd_vendas_categorias = px.bar(qtd_vendas_categorias,
                                   text_auto=True,
                                   title='Quantidade vendas pro categoria')
fig_qtd_vendas_categorias.update_layout(yaxis_title='Quantidade de Vendas')

fig_receita_qtd_vendas_estado = px.bar(qtd_vendas_estado.head(),
                                       x='Local da compra',
                                       y='Preço',
                                       text_auto=True,
                                       title='Top quantidade vendas estados (receita)')
fig_receita_qtd_vendas_estado.update_layout(yaxis_title='Quantidade vendas estado')

fig_mapa_receita = px.scatter_geo(receita_estado,
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon': False},
                                  title='Receita por Estado')
fig_mapa_qtd_receita = px.scatter_geo(qtd_vendas_estado,
                                      lat='lat',
                                      lon='lon',
                                      scope='south america',
                                      size='Preço',
                                      template='seaborn',
                                      hover_name='Local da compra',
                                      hover_data={'lat': False, 'lon': False},
                                      title='Receita por Estado')

fig_receita_mensal = px.line(receita_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0, receita_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_qtd_receita_mensal = px.line(qtd_vendas_mensal,
                                 x='Mes',
                                 y='Preço',
                                 markers=True,
                                 range_y=(0, receita_mensal.max()),
                                 color='Ano',
                                 line_dash='Ano',
                                 title='Receita Mensal')
fig_qtd_receita_mensal.update_layout(yaxis_title='Receita')
# endregion

# VISUALIZAÇÃO
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formatar_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, user_container_width=True)
        st.plotly_chart(fig_receita_estados, user_container_width=True)

    
        st.metric('Quantidade de venda', formatar_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, user_container_width=True)
        st.plotly_chart(fig_receita_categorias, user_container_width=True)
    st.dataframe(dados)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formatar_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_qtd_receita, user_container_width=True)
        st.plotly_chart(fig_receita_qtd_vendas_estado, user_container_width=True)
    with coluna2:
        st.metric('Quantidade de venda', formatar_numero(dados.shape[0]))
        st.plotly_chart(fig_qtd_receita_mensal, user_container_width=True)
        st.plotly_chart(fig_qtd_vendas_categorias, user_container_width=True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade Vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formatar_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x='sum',
                                        y=vendedores[['sum']].sort_values('sum', ascending=False).
                                        head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top{qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)

    with coluna2:
        st.metric('Quantidade de venda', formatar_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                       x='count',
                                       y=vendedores[['count']].sort_values('count', ascending=False).
                                       head(qtd_vendedores).index,
                                       text_auto=True,
                                       title=f'Top{qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores)
# if __name__ == '__main__':
# os.system('streamlit run DashBoard.py')
