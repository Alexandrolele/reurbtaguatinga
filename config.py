import json
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db


def configurar_firebase():
  if not firebase_admin._apps:
    try:
      if "firebase" in st.secrets:
        secret_dict = dict(st.secrets["firebase"])

        # Garante a formatação correta das quebras de linha na chave privada
        if "private_key" in secret_dict:
          pk = secret_dict["private_key"]
          # Se vier com \n literal ou escapado, normaliza para quebra real
          pk = pk.replace("\\n", "\n")
          secret_dict["private_key"] = pk

        cred = credentials.Certificate(secret_dict)
        database_url = secret_dict.get(
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
