import json
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db


def configurar_firebase():
  if not firebase_admin._apps:
    try:
      # Verifica se as secrets estão configuradas no formato segmentado
      if "firebase_type" in st.secrets:
        service_account_info = {
            "type": st.secrets["firebase_type"],
            "project_id": st.secrets["firebase_project_id"],
            "private_key_id": st.secrets["firebase_private_key_id"],
            "private_key": st.secrets["firebase_private_key"].replace(
                "\\n", "\n"
            ),
            "client_email": st.secrets["firebase_client_email"],
            "client_id": st.secrets["firebase_client_id"],
            "auth_uri": st.secrets["firebase_auth_uri"],
            "token_uri": st.secrets["firebase_token_uri"],
            "auth_provider_x509_cert_url": st.secrets[
                "firebase_auth_provider_x509_cert_url"
            ],
            "client_x509_cert_url": st.secrets[
                "firebase_client_x509_cert_url"
            ],
            "universe_domain": st.secrets["firebase_universe_domain"],
        }
        cred = credentials.Certificate(service_account_info)
        database_url = st.secrets.get(
            "firebase_databaseURL",
            "https://reurb-1-0-default-rtdb.firebaseio.com/",
        )
      else:
        # Modo local via arquivo JSON
        caminho_json = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "serviceAccountKey.json"
        )
        cred = credentials.Certificate(caminho_json)
        database_url = "https://reurb-1-0-default-rtdb.firebaseio.com/"

      firebase_admin.initialize_app(cred, {"databaseURL": database_url})
    except Exception as e:
      st.error(f"Erro ao inicializar Firebase Admin: {e}")
  return db
