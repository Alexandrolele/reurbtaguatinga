import json
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db


def configurar_firebase():
  if not firebase_admin._apps:
    try:
      # Se estiver usando o Streamlit Secrets na nuvem
      if "firebase" in st.secrets:
        key_dict = dict(st.secrets["firebase"])

        # Corrige as quebras de linha da chave privada
        if "private_key" in key_dict:
          key_dict["private_key"] = str(key_dict["private_key"]).replace(
              "\\n", "\n"
          )

        # Cria um arquivo JSON temporário na memória/disco do servidor a partir das secrets
        temp_json_path = "/tmp/temp_service_account.json"
        with open(temp_json_path, "w") as f:
          json.dump(key_dict, f)

        cred = credentials.Certificate(temp_json_path)
      else:
        # Fallback para o arquivo local
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
