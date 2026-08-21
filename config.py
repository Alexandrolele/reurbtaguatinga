import json
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db


def configurar_firebase():
  if not firebase_admin._apps:
    try:
      if "firebase_json" in st.secrets:
        # Lê o JSON completo como string e converte para dicionário
        service_account_info = json.loads(st.secrets["firebase_json"])
        cred = credentials.Certificate(service_account_info)
        database_url = service_account_info.get(
            "databaseURL", "https://reurb-1-0-default-rtdb.firebaseio.com/"
        )
      else:
        caminho_json = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "serviceAccountKey.json"
        )
        cred = credentials.Certificate(caminho_json)
        database_url = "https://reurb-1-0-default-rtdb.firebaseio.com/"

      firebase_admin.initialize_app(cred, {"databaseURL": database_url})
    except Exception as e:
      st.error(f"Erro ao inicializar Firebase Admin: {e}")
  return db
