import json
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db


def configurar_firebase():
  if not firebase_admin._apps:
    try:
      # Tenta carregar via st.secrets se estiver disponível na nuvem
      if "firebase" in st.secrets:
        # Converte explicitamente o secret do Streamlit em um dicionário puro do Python
        key_dict = dict(st.secrets["firebase"])

        # Garante o tratamento correto da chave privada (substitui string literal por quebra de linha real)
        if "private_key" in key_dict:
          pk = str(key_dict["private_key"])
          key_dict["private_key"] = pk.replace("\\n", "\n")

        cred = credentials.Certificate(key_dict)
      else:
        # Fallback para o arquivo JSON físico local
        caminho_json = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "serviceAccountKey.json"
        )
        cred = credentials.Certificate(caminho_json)

      firebase_admin.initialize_app(
          cred, {"databaseURL": "https://reurb-1-0-default-rtdb.firebaseio.com/"}
      )
    except Exception as e:
      st.error(f"Erro ao inicializar Firebase Admin: {e}")
  return db
