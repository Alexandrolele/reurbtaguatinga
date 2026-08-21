import json
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db


def configurar_firebase():
  if not firebase_admin._apps:
    try:
      # Verifica se estamos no Streamlit Cloud e se as Secrets do firebase existem
      if "firebase" in st.secrets:
        # Carrega os dados direto das Secrets do Streamlit Cloud
        firebase_secrets = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_secrets)
      else:
        # Se não estiver nas Secrets, tenta usar o arquivo JSON local (computador)
        caminho_json = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "serviceAccountKey.json"
        )
        cred = credentials.Certificate(caminho_json)

      database_url = (
          st.secrets["firebase"]["databaseURL"]
          if "firebase" in st.secrets
          else "https://reurb-1-0-default-rtdb.firebaseio.com/"
      )

      firebase_admin.initialize_app(cred, {"databaseURL": database_url})
    except Exception as e:
      st.error(f"Erro ao inicializar Firebase Admin: {e}")
  return db
