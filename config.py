import json
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db


def configurar_firebase():
  if not firebase_admin._apps:
    try:
      if "firebase" in st.secrets:
        # Pega os segredos do bloco [firebase]
        sec = st.secrets["firebase"]

        # Monta o dicionário de credenciais esperado pelo Firebase
        service_account_info = {
            "type": sec["type"],
            "project_id": sec["project_id"],
            "private_key_id": sec["private_key_id"],
            # Substitui as barras literais por quebras de linha reais na chave
            "private_key": sec["private_key"].replace("\\n", "\n"),
            "client_email": sec["client_email"],
            "client_id": sec["client_id"],
            "auth_uri": sec["auth_uri"],
            "token_uri": sec["token_uri"],
            "auth_provider_x509_cert_url": sec["auth_provider_x509_cert_url"],
            "client_x509_cert_url": sec["client_x509_cert_url"],
            "universe_domain": sec["universe_domain"],
        }

        cred = credentials.Certificate(service_account_info)
        database_url = sec.get(
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
