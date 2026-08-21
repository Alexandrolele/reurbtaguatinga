import json
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db


def configurar_firebase():
  if not firebase_admin._apps:
    try:
      # Aponta diretamente para o arquivo serviceAccountKey.json na raiz do projeto
      caminho_json = os.path.join(
          os.path.dirname(os.path.abspath(__file__)), "serviceAccountKey.json"
      )

      if os.path.exists(caminho_json):
        cred = credentials.Certificate(caminho_json)
      else:
        raise FileNotFoundError(
            f"Arquivo de credenciais não encontrado em: {caminho_json}"
        )

      firebase_admin.initialize_app(
          cred, {"databaseURL": "https://reurb-1-0-default-rtdb.firebaseio.com/"}
      )
    except Exception as e:
      st.error(f"Erro ao inicializar Firebase Admin: {e}")
  return db
