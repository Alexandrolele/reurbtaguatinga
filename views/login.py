import base64
import os
import streamlit as st


def renderizar_login():
  # Injetando CSS com um gradiente azul suave e elegante
  st.markdown(
      """
        <style>
            .stApp {
                background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
            }
            .block-container {
                max-width: 900px !important;
                padding-top: 2rem !important;
            }
            .stTextInput input {
                border-radius: 8px !important;
                border: 1px solid #cbd5e1 !important;
                padding: 12px !important;
                background-color: #ffffff !important;
            }
            .stTextInput input:focus {
                border-color: #2563eb !important;
                box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
            }
            .stButton button {
                background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%) !important;
                color: white !important;
                border-radius: 8px !important;
                font-weight: bold !important;
                padding: 12px !important;
                transition: all 0.3s ease;
            }
            .stButton button:hover {
                background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
            }
        </style>
    """,
      unsafe_allow_html=True,
  )

  st.write("<br>", unsafe_allow_html=True)

  col1, col2, col3 = st.columns([0.8, 2.2, 0.8])

  with col2:
    with st.container(border=True):
      try:
        if os.path.exists("logo_prefeitura.png"):
          with open("logo_prefeitura.png", "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()

          st.markdown(
              f"""
                    <div style='text-align: center; width: 100%; padding: 10px;'>
                        <div style="display: block; margin-left: auto; margin-right: auto; width: 140px; margin-bottom: 12px;">
                            <img src="data:image/png;base64,{img_base64}" width="140">
                        </div>
                        <div style='line-height: 1.2;'>
                            <h1 style='margin: 0; padding: 0; font-size: 2rem; color: #1e3a8a; font-weight: 800;'>SISTEMA REURB</h1>
                            <p style='margin: 4px 0; padding: 0; color: #475569; font-size: 0.95rem; font-weight: bold; letter-spacing: 1.5px;'>ESTADO DO TOCANTINS</p>
                            <p style='margin: 4px 0; padding: 0; color: #0f172a; font-size: 1.1rem; font-weight: 800;'>PREFEITURA MUNICIPAL DE TAGUATINGA</p>
                            <p style='margin: 4px 0; padding: 0; color: #2563eb; font-style: italic; font-size: 0.9rem; font-weight: 600;'>“O PROGRESSO CONTINUA!”</p>
                            <div style="margin: 15px auto; width: 50px; height: 3px; background-color: #2563eb; border-radius: 2px;"></div>
                            <p style='margin: 0; padding: 0; font-size: 1.15rem; font-weight: bold; color: #0f172a; text-transform: uppercase;'>DEPARTAMENTO DE REGULARIZAÇÃO FUNDIÁRIA</p>
                        </div>
                    </div>
                    """,
              unsafe_allow_html=True,
          )
      except Exception:
        st.error("Erro ao carregar cabeçalho visual.")

      st.divider()

      usuario = st.text_input("Usuário", value="Michelaine")
      senha = st.text_input("Senha", type="password")

      st.write("<br>", unsafe_allow_html=True)

      if st.button("Acessar Sistema", use_container_width=True):
        senha_correta = (
            st.secrets.get("SENHA_ADMIN", "lele4619")
            if "SENHA_ADMIN" in st.secrets
            else "lele4619"
        )
        if senha == senha_correta:
          if "realizar_backup" in globals():
            realizar_backup()
          st.session_state.usuario_logado = usuario
          st.session_state.autenticado = True
          st.success("✨ Login realizado com sucesso!")
          st.rerun()
        else:
          st.error("⚠️ Senha incorreta. Tente novamente.")