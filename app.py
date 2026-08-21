import streamlit as st
from config import configurar_firebase
from views.login import renderizar_login
from views.cadastrar import renderizar_cadastro
from views.quadras import renderizar_quadra
from views.pesquisar import renderizar_pesquisa  # <--- 1. IMPORTAÇÃO ADICIONADA AQUI
from firebase_admin import db
from views.certidao import renderizar_relatorios
from views.certidao_nucleo import renderizar_certidao_nucleo
from views.autorizacao import exibir_pagina as renderizar_autorizacao

# Configuração da página
st.set_page_config(
    page_title="REURB Taguatinga - TO",
    page_icon="logo_prefeitura.png",
    layout="wide"
)

# Inicializa o banco
db_instance = configurar_firebase()

# Funções de Apoio (Firebase) para a listagem na tela inicial
def listar_projetos():
    """Retorna as chaves dos projetos salvos no Realtime Database."""
    try:
        ref = db.reference('REURB_V1/projetos')
        dados = ref.get()
        if dados:
            return list(dados.keys())
    except Exception as e:
        st.error(f"Erro ao listar projetos do Firebase: {e}")
    return []

def carregar_projeto(id_projeto):
    """Carrega os dados de um projeto específico do Firebase."""
    try:
        ref = db.reference(f'REURB_V1/projetos/{id_projeto}')
        return ref.get()
    except Exception as e:
        st.error(f"Erro ao carregar projeto: {e}")
    return None

# Estado de autenticação e navegação
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None

if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = "Início"

if "projeto_ativo" not in st.session_state:
    st.session_state["projeto_ativo"] = None

if "nome_arquivo_original" not in st.session_state:
    st.session_state["nome_arquivo_original"] = None

# Controle de rotas / blocos
if not st.session_state["autenticado"]:
    renderizar_login()
else:
    # --- MENU LATERAL EM FORMATO DE BOTÕES ---
    usuario_atual = st.session_state.get('usuario', 'Operador')
    st.sidebar.title(f"Operador: {str(usuario_atual).capitalize()}")
    st.sidebar.markdown("---")

    if st.sidebar.button("🏠 Início", use_container_width=True):
        st.session_state["pagina_atual"] = "Início"
        st.session_state["projeto_ativo"] = None
        st.session_state["nome_arquivo_original"] = None
        st.rerun()
    
    if st.sidebar.button("➕ Novo Núcleo", use_container_width=True):
        st.session_state["pagina_atual"] = "Novo Núcleo"
        st.session_state["projeto_ativo"] = None
        st.session_state["nome_arquivo_original"] = None
        st.session_state["pagina"] = 'cadastro_nucleo'
        st.rerun()
        
    if st.sidebar.button("🔍 Pesquisar", use_container_width=True):
        st.session_state["pagina_atual"] = "Pesquisar"
        st.rerun()
        
    if st.sidebar.button("📊 Relatórios", use_container_width=True):
        st.session_state["pagina_atual"] = "Relatórios"
        st.rerun()
        
    if st.sidebar.button("📜 Certidão REURB", use_container_width=True):
        st.session_state["pagina_atual"] = "Certidão REURB"
        st.rerun()
        
    if st.sidebar.button("📄 Autorização", use_container_width=True):
        st.session_state["pagina_atual"] = "Autorização"
        st.rerun()

    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Sair do Sistema", use_container_width=True):
        st.session_state["autenticado"] = False
        st.session_state["usuario"] = None
        st.session_state["pagina_atual"] = "Início"
        st.rerun()

    # --- RENDERIZAÇÃO DA TELA SELECIONADA ---
    pagina = st.session_state["pagina_atual"]

    if pagina == "Início":
        st.title("📊 Painel Geral REURB")
        st.write("Indicadores e visão geral dos núcleos cadastrados no sistema.")
        st.divider()
        
        ids_projetos = listar_projetos()
        if not ids_projetos:
            st.info("Nenhum núcleo cadastrado no momento. Utilize o menu lateral para criar um 'Novo Núcleo'.")
        else:
            cols = st.columns(3)
            for idx, id_proj in enumerate(ids_projetos):
                dados = carregar_projeto(id_proj)
                if dados:
                    with cols[idx % 3]:
                        with st.container(border=True):
                            st.subheader(f"📍 {dados.get('nome', 'Sem Nome')}")
                            
                            crf_n = dados.get('num_crf', dados.get('num_decreto', '')) 
                            ano_c = dados.get('ano_crf', dados.get('ano_decreto', ''))
                            
                            if crf_n and ano_c:
                                st.markdown(f"**CRF Nº:** {crf_n}/{ano_c}")
                            else:
                                st.markdown("*CRF: Não informada*")
                                
                            st.write(f"**Local:** {dados.get('local', 'Não informado')}")
                            
                            if st.button(f"Abrir Detalhes", key=f"abrir_{id_proj}", use_container_width=True):
                                st.session_state.projeto_ativo = dados
                                st.session_state.nome_arquivo_original = id_proj
                                st.session_state["pagina_atual"] = "detalhes_projeto"
                                st.rerun()

    elif pagina == "detalhes_projeto":
        p = st.session_state.get('projeto_ativo')
        if p:
            col_topo1, col_topo2 = st.columns([1, 4])
            with col_topo1:
                if st.button("✏️ Editar Dados / Excluir"):
                    st.session_state["pagina_atual"] = "Novo Núcleo"
                    st.rerun()
            with col_topo2:
                if st.button("⬅️ Voltar ao Painel"):
                    st.session_state["pagina_atual"] = "Início"
                    st.session_state["projeto_ativo"] = None
                    st.rerun()

            st.markdown(f"## 📍 {p.get('nome', '')}")
            
            with st.expander("📄 Dados Técnicos", expanded=True):
                tc1, tc2, tc3 = st.columns(3)
                tc1.write(f"**Modalidade:** {p.get('modalidade', '')}")
                
                area_t = p.get('area_total', 0)
                try:
                    area_t_fmt = f"{float(area_t):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                except:
                    area_t_fmt = str(area_t)
                tc2.write(f"**Área Total:** {area_t_fmt} m²")
                
                area_v = p.get('area_viaria', 0)
                try:
                    area_v_fmt = f"{float(area_v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                except:
                    area_v_fmt = str(area_v)
                tc3.write(f"**Área Viária:** {area_v_fmt} m²")
                
                crf_n = p.get('num_crf', p.get('num_decreto', '')) 
                ano_c = p.get('ano_crf', p.get('ano_decreto', ''))
                st.write(f"**CRF de Regulamentação:** {crf_n}/{ano_c}")

            st.markdown("---")
            
            quadras = p.get('quadras', [])
            if not quadras:
                st.info("Nenhuma quadra cadastrada neste núcleo.")
            else:
                cols_q = st.columns(5)
                for idx, q_info in enumerate(quadras):
                    nome_quadra = q_info.get('quadra', f"{idx+1}")
                    with cols_q[idx % 5]:
                        if st.button(f"QUADRA {nome_quadra}", key=f"btn_q_{idx}", use_container_width=True):
                            st.session_state["quadra_ativa"] = nome_quadra
                            st.session_state["pagina_atual"] = "detalhes_quadra"
                            st.rerun()
        else:
            st.warning("Nenhum projeto selecionado.")
            if st.button("Voltar"):
                st.session_state["pagina_atual"] = "Início"
                st.rerun()

    elif pagina == "detalhes_quadra":
        renderizar_quadra()
        
    elif pagina == "Novo Núcleo":
        st.session_state['pagina'] = 'cadastro_nucleo'
        renderizar_cadastro()
        
    elif pagina == "Pesquisar":
        renderizar_pesquisa()  # <--- 2. CHAMADA DA TELA DE PESQUISA AQUI
        
    elif pagina == "Relatórios":
        renderizar_certidao_nucleo()
           
        
    elif pagina == "Certidão REURB":
        renderizar_relatorios()
        
    elif pagina == "Autorização":
      renderizar_autorizacao()