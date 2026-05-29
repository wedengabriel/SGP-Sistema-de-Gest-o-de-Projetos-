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

if "os_id_selecionada" not in st.session_state:
    st.session_state.os_id_selecionada = None

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

paginas = [
    "Visão Geral",
    "Projeto Individual",
    "Cadastrar Projeto",
    "Cadastrar OS",
    "Cadastrar Técnicos da OS",
    "Cadastrar Material",
    "OS Individual"
]

opcao = st.sidebar.radio(
    "Escolha uma visão:",
    paginas,
    index=paginas.index(st.session_state.pagina)
)

st.session_state.pagina = opcao

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

            aba_resumo, aba_custos, aba_materiais, aba_ordens = st.tabs([
                "Resumo",
                "Custos",
                "Materiais",
                "Ordens de Serviço"
            ])

            with aba_resumo:
                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Valor Cobrado", formatar_moeda(custo["valor_cobrado"]))
                col2.metric("Recebimento Líquido", formatar_moeda(custo["recebimento_liquido"]))
                col3.metric("Custo Total", formatar_moeda(custo["custo_total"]))
                col4.metric("Lucro", formatar_moeda(custo["lucro_reais"]))

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

            with aba_custos:
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

                if not dados_grafico.empty:
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
                else:
                    st.info("Nenhum custo registrado para este projeto.")

                st.divider()

                st.subheader("Detalhamento")

                col7, col8, col9, col10 = st.columns(4)

                col7.metric("Mão de Obra", formatar_moeda(custo["custo_mao_obra"]))
                col8.metric("Deslocamento", formatar_moeda(custo["custo_deslocamento"]))
                col9.metric("Refeição", formatar_moeda(custo["custo_refeicao"]))
                col10.metric("Materiais", formatar_moeda(custo["custo_materiais"]))

            with aba_materiais:
                st.subheader("Materiais Utilizados")

                if materiais_projeto:
                    dados_materiais = pd.DataFrame(materiais_projeto)
                    dados_materiais = dados_materiais[dados_materiais["valor_total"] > 0]

                    if not dados_materiais.empty:
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
                        st.info("Nenhum material com valor cadastrado para este projeto.")
                else:
                    st.info("Nenhum material cadastrado para este projeto.")

            with aba_ordens:
                st.subheader("Ordens de Serviço")

                response_os = requests.get(f"{API_URL}/ordens-servico")
                todas_os = response_os.json() if response_os.status_code == 200 else []

                os_projeto = [
                    os for os in todas_os
                    if os["projeto_id"] == projeto_id
                ]

                if os_projeto:
                    for os in os_projeto:
                        with st.container(border=True):
                            col_os1, col_os2, col_os3, col_os4 = st.columns(4)

                            col_os1.metric("OS", os["id"])
                            col_os2.metric("Data", os["data_servico"])
                            col_os3.metric("KM Rodado", os["km_retorno"] - os["km_saida"])
                            col_os4.metric("Deslocamento", formatar_moeda(os["valor_deslocamento"]))

                            st.write(f"**Tipo de Serviço:** {os['tipo_servico']}")
                            st.write(f"**Equipamento/TAG/Local:** {os['equipamento_tag_local']}")
                            st.write(f"**Descrição:** {os['descricao_servico']}")

                            response_tecnicos_os = requests.get(
                                f"{API_URL}/ordens-servico/{os['id']}/tecnicos"
                            )

                            tecnicos_os = (
                                response_tecnicos_os.json()
                                if response_tecnicos_os.status_code == 200
                                else []
                            )

                            if tecnicos_os:
                                st.markdown("#### Equipe")

                                total_mao_obra_os = 0

                                for tecnico in tecnicos_os:
                                    total_mao_obra_os += tecnico["valor_total"]

                                    st.write(
                                        f"**{tecnico['tecnico']}** — "
                                        f"{tecnico['horas_trabalhadas']}h — "
                                        f"{formatar_moeda(tecnico['valor_total'])}"
                                    )

                                st.metric(
                                    "Custo de Mão de Obra da OS",
                                    formatar_moeda(total_mao_obra_os)
                                )
                            else:
                                st.info("Nenhum técnico vinculado a esta OS.")

                            if st.button("Ver Detalhes da OS", key=f"os_detalhe_{os['id']}"):
                                st.session_state.os_id_selecionada = os["id"]
                                st.session_state.pagina = "OS Individual"
                                st.rerun()

                else:
                    st.info("Nenhuma OS cadastrada para este projeto.")

if opcao == "Cadastrar Projeto":
    st.subheader("Cadastrar Novo Projeto")

    with st.form("form_cadastro_projeto"):
        numero_projeto = st.text_input("Número do Projeto")
        cliente = st.text_input("Cliente")
        cidade = st.text_input("Cidade")
        uf = st.text_input("UF", max_chars=2)
        unidade = st.text_input("Unidade")

        valor_cobrado = st.number_input(
            "Valor Cobrado",
            min_value=0.0,
            step=100.0
        )

        aliquota_municipal = st.number_input(
            "Alíquota Municipal (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.5
        )

        status = st.selectbox(
            "Status",
            ["Em andamento", "Finalizado", "Stand By", "Cancelado"]
        )

        data_inicio = st.date_input("Data de Início")
        possui_data_fim = st.checkbox("Projeto já possui data fim?")

        data_fim = None

        if possui_data_fim:
            data_fim = st.date_input("Data Fim")

        botao_salvar = st.form_submit_button("Salvar Projeto")

        if botao_salvar:
            dados_projeto = {
                "numero_projeto": numero_projeto,
                "cliente": cliente,
                "cidade": cidade,
                "uf": uf.upper(),
                "unidade": unidade,
                "valor_cobrado": valor_cobrado,
                "aliquota_municipal": aliquota_municipal,
                "status": status,
                "data_inicio": str(data_inicio),
                "data_fim": str(data_fim) if data_fim else None
            }

            resposta = requests.post(
                f"{API_URL}/projetos",
                json=dados_projeto
            )

            if resposta.status_code == 200:
                st.success("Projeto cadastrado com sucesso!")
                st.session_state.pagina = "Visão Geral"
                st.rerun()
            else:
                st.error("Erro ao cadastrar projeto.")
                st.write(resposta.json())

if opcao == "Cadastrar OS":
    st.subheader("Cadastrar Ordem de Serviço")

    if not projetos:
        st.info("Cadastre um projeto antes de lançar uma OS.")
    else:
        opcoes_projetos = {
            f"{p['numero_projeto']} - {p['cliente']}": p["id"]
            for p in projetos
        }

        with st.form("form_cadastro_os"):
            projeto_selecionado = st.selectbox(
                "Projeto",
                list(opcoes_projetos.keys())
            )

            projeto_id = opcoes_projetos[projeto_selecionado]

            data_servico = st.date_input("Data do Serviço")

            col1, col2 = st.columns(2)

            with col1:
                km_saida = st.number_input("KM Saída", min_value=0.0, step=1.0)
                hora_saida = st.time_input("Hora Saída")
                hora_inicio = st.time_input("Hora Início")

            with col2:
                km_retorno = st.number_input("KM Retorno", min_value=0.0, step=1.0)
                hora_termino = st.time_input("Hora Término")
                hora_retorno = st.time_input("Hora Retorno")

            quantidade_tecnicos = st.number_input(
                "Quantidade de Técnicos",
                min_value=1,
                step=1
            )

            acompanhado_por = st.text_input("Acompanhado por")

            tipo_servico = st.selectbox(
                "Tipo de Serviço",
                ["Atendimento programado", "Atendimento emergencial", "Outro"]
            )

            equipamento_tag_local = st.text_input("Equipamento / TAG / Local")

            diagnostico = st.text_area("Diagnóstico Técnico")

            descricao_servico = st.text_area("Descrição dos Serviços Executados")

            status = st.selectbox(
                "Status da OS",
                ["Em andamento", "Finalizado"]
            )

            botao_salvar_os = st.form_submit_button("Salvar OS")

            if botao_salvar_os:
                erros = []

                if km_retorno <= km_saida:
                    erros.append("O KM de retorno deve ser maior que o KM de saída.")

                if hora_retorno <= hora_saida:
                    erros.append("A hora de retorno deve ser maior que a hora de saída.")

                if not acompanhado_por.strip():
                    erros.append("Informe quem acompanhou o serviço.")

                if not equipamento_tag_local.strip():
                    erros.append("Informe o equipamento, TAG ou local.")

                if not diagnostico.strip():
                    erros.append("Informe o diagnóstico técnico.")

                if not descricao_servico.strip():
                    erros.append("Informe a descrição dos serviços executados.")

                if erros:
                    for erro in erros:
                        st.warning(erro)
                    st.stop()

                dados_os = {
                    "projeto_id": projeto_id,
                    "data_servico": str(data_servico),
                    "km_saida": km_saida,
                    "km_retorno": km_retorno,
                    "hora_saida": str(hora_saida),
                    "hora_inicio": str(hora_inicio),
                    "hora_termino": str(hora_termino),
                    "hora_retorno": str(hora_retorno),
                    "quantidade_tecnicos": quantidade_tecnicos,
                    "acompanhado_por": acompanhado_por,
                    "tipo_servico": tipo_servico,
                    "equipamento_tag_local": equipamento_tag_local,
                    "diagnostico": diagnostico,
                    "descricao_servico": descricao_servico,
                    "status": status
                }

                resposta = requests.post(
                    f"{API_URL}/ordens-servico",
                    json=dados_os
                )

                if resposta.status_code == 200:
                    st.success("OS cadastrada com sucesso!")
                    st.session_state.pagina = "Projeto Individual"
                    st.session_state.projeto_id_selecionado = projeto_id
                    st.rerun()
                else:
                    st.error("Erro ao cadastrar OS.")
                    st.write(resposta.json())

if opcao == "Cadastrar Técnicos da OS":
    st.subheader("Cadastrar Técnicos da OS")

    response_os = requests.get(f"{API_URL}/ordens-servico")
    ordens_servico = response_os.json() if response_os.status_code == 200 else []

    response_tecnicos = requests.get(f"{API_URL}/tecnicos")
    tecnicos = response_tecnicos.json() if response_tecnicos.status_code == 200 else []

    if not projetos:
        st.info("Cadastre um projeto antes de vincular técnicos.")
    elif not ordens_servico:
        st.info("Cadastre uma OS antes de vincular técnicos.")
    elif not tecnicos:
        st.info("Cadastre técnicos antes de vincular à OS.")
    else:
        opcoes_projetos = {
            p["numero_projeto"]: p
            for p in projetos
        }

        numero_projeto = st.selectbox(
            "Número do Projeto",
            list(opcoes_projetos.keys())
        )

        projeto_escolhido = opcoes_projetos[numero_projeto]
        projeto_id = projeto_escolhido["id"]

        st.write(f"**Cliente:** {projeto_escolhido['cliente']}")

        ordens_filtradas = [
            os for os in ordens_servico
            if os["projeto_id"] == projeto_id
        ]

        if not ordens_filtradas:
            st.warning("Nenhuma OS encontrada para este projeto.")
        else:
            opcoes_os = {
                f"OS {os['id']} | Data: {os['data_servico']} | Saída: {os['hora_saida']} | Retorno: {os['hora_retorno']}": os["id"]
                for os in ordens_filtradas
            }

            opcoes_tecnicos = {
                t["nome"]: t["id"]
                for t in tecnicos
            }

            with st.form("form_os_tecnico"):
                os_selecionada = st.selectbox(
                    "Ordem de Serviço",
                    list(opcoes_os.keys())
                )

                st.markdown("### Técnicos da OS")

                tecnico_1 = st.selectbox("Técnico 1", [""] + list(opcoes_tecnicos.keys()))
                tecnico_2 = st.selectbox("Técnico 2", [""] + list(opcoes_tecnicos.keys()))
                tecnico_3 = st.selectbox("Técnico 3", [""] + list(opcoes_tecnicos.keys()))
                tecnico_4 = st.selectbox("Técnico 4", [""] + list(opcoes_tecnicos.keys()))
                tecnico_5 = st.selectbox("Técnico 5", [""] + list(opcoes_tecnicos.keys()))
                tecnico_6 = st.selectbox("Técnico 6", [""] + list(opcoes_tecnicos.keys()))

                botao_salvar = st.form_submit_button("Adicionar Equipe à OS")

                if botao_salvar:
                    tecnicos_selecionados = [
                        tecnico_1,
                        tecnico_2,
                        tecnico_3,
                        tecnico_4,
                        tecnico_5,
                        tecnico_6
                    ]

                    tecnicos_selecionados = [
                        t for t in tecnicos_selecionados
                        if t != ""
                    ]

                    tecnicos_unicos = list(dict.fromkeys(tecnicos_selecionados))

                    if not tecnicos_unicos:
                        st.warning("Selecione pelo menos um técnico.")
                    else:
                        os_id = opcoes_os[os_selecionada]

                        erros = []
                        sucessos = []

                        for nome_tecnico in tecnicos_unicos:
                            dados = {
                                "ordem_servico_id": os_id,
                                "tecnico_id": opcoes_tecnicos[nome_tecnico]
                            }

                            resposta = requests.post(
                                f"{API_URL}/os-tecnicos",
                                json=dados
                            )

                            if resposta.status_code == 200:
                                resultado = resposta.json()
                                sucessos.append(
                                    f"{nome_tecnico} - {formatar_moeda(resultado['valor_total'])}"
                                )
                            else:
                                erros.append(nome_tecnico)

                        if sucessos:
                            st.success("Equipe vinculada à OS com sucesso!")
                            for item in sucessos:
                                st.write(item)

                        if erros:
                            st.error("Alguns técnicos não foram vinculados:")
                            for item in erros:
                                st.write(item)

if opcao == "Cadastrar Material":
    st.subheader("Cadastrar Material")

    if not projetos:
        st.info("Cadastre um projeto antes de lançar materiais.")

    else:

        opcoes_projetos = {
            f"{p['numero_projeto']} - {p['cliente']}": p["id"]
            for p in projetos
        }

        with st.form("form_material"):

            projeto_selecionado = st.selectbox(
                "Projeto",
                list(opcoes_projetos.keys())
            )

            projeto_id = opcoes_projetos[projeto_selecionado]

            response_os = requests.get(f"{API_URL}/ordens-servico")
            ordens_servico = response_os.json() if response_os.status_code == 200 else []

            ordens_filtradas = [
                os for os in ordens_servico
                if os["projeto_id"] == projeto_id
            ]

            if ordens_filtradas:
                opcoes_os = {
                    f"OS {os['id']} - {os['data_servico']}": os["id"]
                    for os in ordens_filtradas
                }

                os_selecionada = st.selectbox(
                    "Ordem de Serviço",
                    list(opcoes_os.keys()),
                    key="material_os"
                )

                ordem_servico_id = opcoes_os[os_selecionada]

            else:
                st.warning("Nenhuma OS cadastrada para este projeto.")
                st.stop()

            data_compra = st.date_input("Data da Compra")

            item = st.text_input("Material")

            quantidade = st.number_input(
                "Quantidade",
                min_value=0.0,
                step=1.0
            )

            valor_unitario = st.number_input(
                "Valor Unitário",
                min_value=0.0,
                step=0.01
            )

            botao_salvar = st.form_submit_button(
                "Salvar Material"
            )

            if botao_salvar:

                erros = []

                if not item.strip():
                    erros.append("Informe o material.")

                if quantidade <= 0:
                    erros.append("Quantidade deve ser maior que zero.")

                if valor_unitario <= 0:
                    erros.append("Valor unitário deve ser maior que zero.")

                if erros:
                    for erro in erros:
                        st.warning(erro)

                else:

                    dados_material = {
                        "projeto_id": projeto_id,
                        "ordem_servico_id": ordem_servico_id,
                        "data_compra": str(data_compra),
                        "item": item,
                        "quantidade": quantidade,
                        "valor_unitario": valor_unitario
                    }

                    resposta = requests.post(
                        f"{API_URL}/materiais",
                        json=dados_material
                    )

                    if resposta.status_code == 200:

                        valor_total = (
                            quantidade * valor_unitario
                        )

                        st.success(
                            f"Material cadastrado com sucesso! "
                            f"Total: {formatar_moeda(valor_total)}"
                        )

                    else:
                        st.error("Erro ao cadastrar material.")
                        st.write(resposta.json())

if opcao == "OS Individual":
    st.subheader("Detalhamento da Ordem de Serviço")

    response_os = requests.get(f"{API_URL}/ordens-servico")
    todas_os = response_os.json() if response_os.status_code == 200 else []

    os_encontrada = None

    for os in todas_os:
        if os["id"] == st.session_state.os_id_selecionada:
            os_encontrada = os
            break

    if os_encontrada is None:
        st.info("Selecione uma OS na página de Projeto Individual.")
    else:
        projeto_da_os = None

        for projeto in projetos:
            if projeto["id"] == os_encontrada["projeto_id"]:
                projeto_da_os = projeto
                break

        if projeto_da_os:
            st.title(
                f"OS {os_encontrada['id']} - Projeto {projeto_da_os['numero_projeto']}"
            )
            st.subheader(projeto_da_os["cliente"])
        else:
            st.title(f"OS {os_encontrada['id']}")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Data", os_encontrada["data_servico"])
        col2.metric("KM Rodado", os_encontrada["km_retorno"] - os_encontrada["km_saida"])
        col3.metric("Deslocamento", formatar_moeda(os_encontrada["valor_deslocamento"]))
        col4.metric("Refeição", formatar_moeda(os_encontrada["valor_refeicao"]))

        st.divider()

        st.subheader("Informações da OS")

        st.write(f"**Tipo de Serviço:** {os_encontrada['tipo_servico']}")
        st.write(f"**Acompanhado por:** {os_encontrada['acompanhado_por']}")
        st.write(f"**Equipamento / TAG / Local:** {os_encontrada['equipamento_tag_local']}")
        st.write(f"**Diagnóstico:** {os_encontrada['diagnostico']}")
        st.write(f"**Descrição:** {os_encontrada['descricao_servico']}")
        st.write(f"**Status:** {os_encontrada['status']}")

        st.divider()

        response_tecnicos_os = requests.get(
            f"{API_URL}/ordens-servico/{os_encontrada['id']}/tecnicos"
        )

        tecnicos_os = (
            response_tecnicos_os.json()
            if response_tecnicos_os.status_code == 200
            else []
        )

        st.subheader("Equipe Técnica")

        if tecnicos_os:
            total_mao_obra = 0

            for tecnico in tecnicos_os:
                total_mao_obra += tecnico["valor_total"]

                with st.container(border=True):
                    col_t1, col_t2, col_t3 = st.columns(3)

                    col_t1.write(f"**{tecnico['tecnico']}**")
                    col_t2.metric("Horas", f"{tecnico['horas_trabalhadas']}h")
                    col_t3.metric("Custo", formatar_moeda(tecnico["valor_total"]))

            st.metric("Total Mão de Obra", formatar_moeda(total_mao_obra))
        else:
            st.info("Nenhum técnico vinculado a esta OS.")
    
