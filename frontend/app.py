import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000"


def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.set_page_config(
    page_title="SGP",
    layout="wide"
)

st.title("SGP - Sistema de Gestão de Projetos")

if "pagina" not in st.session_state:
    st.session_state.pagina = "Visão Geral"

if "projeto_id_selecionado" not in st.session_state:
    st.session_state.projeto_id_selecionado = None

response = requests.get(f"{API_URL}/projetos")
projetos = response.json() if response.status_code == 200 else []

dados_custos = []

for projeto in projetos:
    response_custos = requests.get(f"{API_URL}/projetos/{projeto['id']}/custos")

    if response_custos.status_code == 200:
        custo = response_custos.json()
        dados_custos.append(custo)

df_custos = pd.DataFrame(dados_custos)

st.sidebar.title("Navegação")

opcao = st.sidebar.radio(
    "Escolha uma visão:",
    ["Visão Geral", "Projeto Individual"],
    index=0 if st.session_state.pagina == "Visão Geral" else 1
)

st.session_state.pagina = opcao


if opcao == "Visão Geral":
    st.subheader("Dashboard Geral")

    total_projetos = len(projetos)
    total_custo = df_custos["custo_total"].sum() if not df_custos.empty else 0
    total_lucro = df_custos["lucro_reais"].sum() if not df_custos.empty else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Total de Projetos", total_projetos)
    col2.metric("Custo Total", formatar_moeda(total_custo))
    col3.metric("Lucro Total", formatar_moeda(total_lucro))

    st.divider()

    st.subheader("Projetos")

    if not df_custos.empty:
        for projeto in dados_custos:
            with st.container(border=True):
                col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 2, 2, 2, 1])

                col1.markdown(f"### {projeto['numero_projeto']}")
                col2.markdown(f"### {projeto['cliente']}")
                col3.metric(
                    "Custo Total",
                    formatar_moeda(projeto["custo_total"])
                )

                margem = projeto["lucro_percentual"]
                delta_meta = margem - 70

                col4.metric(
                    "Lucro",
                    formatar_moeda(projeto["lucro_reais"]),
                )

                if margem < 60:
                    col5.error("🔴 Crítico")
                elif margem < 70:
                    col5.warning("🟡 Atenção")
                else:
                    col5.success("🟢 Saudável")

                if col6.button("Ver", key=f"card_{projeto['projeto_id']}"):
                    st.session_state.pagina = "Projeto Individual"
                    st.session_state.projeto_id_selecionado = projeto["projeto_id"]
                    st.rerun()
    else:
        st.info("Nenhum projeto cadastrado.")

if opcao == "Projeto Individual":
    st.subheader("Análise Individual do Projeto")

    if not projetos:
        st.info("Nenhum projeto cadastrado.")
    else:
        opcoes_projetos = {
            f"{p['numero_projeto']} - {p['cliente']}": p["id"]
            for p in projetos
        }

        ids_projetos = list(opcoes_projetos.values())

        index_padrao = 0

        if st.session_state.projeto_id_selecionado in ids_projetos:
            index_padrao = ids_projetos.index(st.session_state.projeto_id_selecionado)

        projeto_selecionado = st.selectbox(
            "Selecione o projeto:",
            list(opcoes_projetos.keys()),
            index=index_padrao
        )

        projeto_id = opcoes_projetos[projeto_selecionado]
        st.session_state.projeto_id_selecionado = projeto_id

        response_custo = requests.get(f"{API_URL}/projetos/{projeto_id}/custos")

        if response_custo.status_code == 200:
            custo = response_custo.json()

            response_materiais = requests.get(f"{API_URL}/materiais")

            if response_materiais.status_code == 200:
                todos_materiais = response_materiais.json()
                materiais_projeto = [
                    m for m in todos_materiais
                    if m["projeto_id"] == projeto_id
                ]
            else:
                materiais_projeto = []

            st.title(f"Projeto {custo['numero_projeto']} - {custo['cliente']}")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Valor Cobrado", formatar_moeda(custo["valor_cobrado"]))
            col2.metric("Recebimento Líquido", formatar_moeda(custo["recebimento_liquido"]))
            col3.metric("Custo Total", formatar_moeda(custo["custo_total"]))
            col4.metric("Lucro", formatar_moeda(custo["lucro_reais"]))

            st.divider()

            col5, col6 = st.columns(2)

            with col5:
                st.subheader("Distribuição dos Custos")

                dados_grafico = pd.DataFrame({
                    "Categoria": [
                        "Mão de Obra",
                        "Deslocamento",
                        "Refeição",
                        "Materiais"
                    ],
                    "Valor": [
                        custo["custo_mao_obra"],
                        custo["custo_deslocamento"],
                        custo["custo_refeicao"],
                        custo["custo_materiais"]
                    ]
                })

                dados_grafico = dados_grafico[dados_grafico["Valor"] > 0]

                fig = px.bar(
                dados_grafico,
                x="Categoria",
                y="Valor",
                text="Valor",
                title="Distribuição dos Custos"
                )

                fig.update_traces(
                texttemplate='R$ %{y:,.2f}',
                textposition='outside'
                )

                fig.update_layout(
                yaxis_title="Valor (R$)",
                xaxis_title="",
                height=500
                )

                st.plotly_chart(fig, use_container_width=True)

            with col6:
                st.subheader("Materiais Utilizados")

                if materiais_projeto:
                    dados_materiais = pd.DataFrame(materiais_projeto)

                    dados_materiais = dados_materiais[dados_materiais["valor_total"] > 0]

                    fig_materiais = px.bar(
                        dados_materiais,
                        x="item",
                        y="valor_total",
                        text="valor_total",
                        title="Custo por Material"
                    )

                    fig_materiais.update_traces(
                        texttemplate='R$ %{y:,.2f}',
                        textposition='outside'
                    )

                    fig_materiais.update_layout(
                        yaxis_title="Valor (R$)",
                        xaxis_title="Material",
                        height=500
                    )

                    st.plotly_chart(fig_materiais, use_container_width=True)

                    st.dataframe(
                        dados_materiais[[
                            "data_compra",
                            "item",
                            "quantidade",
                            "valor_unitario",
                            "valor_total"
                        ]],
                        use_container_width=True
                    )
                else:
                    st.info("Nenhum material cadastrado para este projeto.")


            st.divider()

            st.subheader("Detalhamento")

            col7, col8, col9, col10 = st.columns(4)

            col7.metric("Mão de Obra", formatar_moeda(custo["custo_mao_obra"]))
            col8.metric("Deslocamento", formatar_moeda(custo["custo_deslocamento"]))
            col9.metric("Refeição", formatar_moeda(custo["custo_refeicao"]))
            col10.metric("Materiais", formatar_moeda(custo["custo_materiais"]))

            st.divider()

            margem = custo["lucro_percentual"]

            col_a, col_b = st.columns(2)

            col_a.metric(
                "Margem de Lucro",
                f"{margem:.2f}%"
            )

            if margem < 60:
                col_b.metric("Status", "🔴 Crítico")
            elif margem < 70:
                col_b.metric("Status", "🟡 Atenção")
            else:
                col_b.metric("Status", "🟢 Saudável")