import streamlit as st
from firebase_admin import db

def renderizar_pesquisa():
    st.title("🔍 Pesquisar Processos e Ocupantes")
    st.write("Busque por beneficiários, CPF, lote ou quadra em todos os núcleos cadastrados.")
    st.markdown("---")

    # Campo de termo de busca
    termo_busca = st.text_input("Digite o nome do ocupante, CPF ou número do lote:", placeholder="Ex: Almir ou 000.000.000-00")

    if termo_busca:
        termo_limpo = termo_busca.strip().lower()
        
        # Busca todos os projetos e proprietários do Firebase
        projetos_ref = db.reference('REURB_V1/projetos').get() or {}
        proprietarios_ref = db.reference('REURB_V1/proprietarios').get() or {}
        
        resultados = []

        # Varre todos os núcleos e seus respectivos ocupantes
        for id_proj, dados_proj in proprietarios_ref.items():
            nome_nucleo = projetos_ref.get(id_proj, {}).get('nome', 'Núcleo Desconhecido')
            
            for chave_lote, info_oc in dados_proj.items():
                nome_oc = str(info_oc.get('nome', '')).lower()
                cpf_oc = str(info_oc.get('cpf', '')).lower()
                lote_oc = str(info_oc.get('lote', '')).lower()
                quadra_oc = str(info_oc.get('quadra', '')).lower()
                
                # Verifica se o termo digitado bate com alguma das informações
                if (termo_limpo in nome_oc) or (termo_limpo in cpf_oc) or (termo_limpo == lote_oc) or (termo_limpo == quadra_oc):
                    resultados.append({
                        "nucleo": nome_nucleo,
                        "id_proj": id_proj,
                        "quadra": info_oc.get('quadra'),
                        "lote": info_oc.get('lote'),
                        "nome": info_oc.get('nome'),
                        "cpf": info_oc.get('cpf'),
                        "matricula": info_oc.get('matricula')
                    })

        if not resultados:
            st.warning("Nenhum registro encontrado com o termo informado.")
        else:
            st.success(f"Encontrado(s) {len(resultados)} resultado(s):")
            st.markdown("---")
            
            # Exibe os resultados em formato de tabela/cards organizados
            for res in resultados:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    c1.write(f"**Nome:** {res['nome']}")
                    c2.write(f"**Núcleo:** {res['nucleo']}")
                    c3.write(f"**Quadra:** {res['quadra']} | **Lote:** {res['lote']}")
                    
                    if c4.button("Ver", key=f"btn_res_{res['id_proj']}_{res['quadra']}_{res['lote']}"):
                        # Carrega o projeto e redireciona para a quadra correspondente
                        st.session_state.projeto_ativo = projetos_ref.get(res['id_proj'])
                        st.session_state.nome_arquivo_original = res['id_proj']
                        st.session_state["quadra_ativa"] = res['quadra']
                        st.session_state["pagina_atual"] = "detalhes_quadra"
                        st.rerun()
    else:
        st.info("Digite algo acima para iniciar a busca no banco de dados.")