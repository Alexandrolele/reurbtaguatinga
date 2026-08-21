import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db


def configurar_firebase():
  if not firebase_admin._apps:
    if "firebase" in st.secrets:
      key_dict = dict(st.secrets["firebase"])
      # Converte a string \n literal em quebra de linha real do PEM
      if "private_key" in key_dict:
        key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
      cred = credentials.Certificate(key_dict)
    else:
      caminho_json = os.path.join(
          os.path.dirname(os.path.abspath(__file__)), "serviceAccountKey.json"
      )
      cred = credentials.Certificate(caminho_json)

    firebase_admin.initialize_app(
        cred, {"databaseURL": "https://reurb-1-0-default-rtdb.firebaseio.com/"}
    )
  return db
