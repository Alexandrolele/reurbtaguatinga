from validate_docbr import CPF
from firebase_admin import db
import pandas as pd
import re
import streamlit as st


def renderizar_cadastro():
  # Verifica se está editando ou criando um novo núcleo
  editando = st.session_state.get('projeto_ativo') is not None
  st.title('📋 ' + ('Editar Núcleo' if editando else 'Novo Núcleo'))
  p = st.session_state.projeto_ativo if editando else {}

  if editando:
    with st.expander('⚠️ Zona de Perigo'):
      if st.button('🗑️ EXCLUIR ESTE NÚCLEO DEFINITIVAMENTE'):
        try:
          id_proj = st.session_state.get('nome_arquivo_original')
          if id_proj:
            db.reference(f'REURB_V1/projetos/{id_proj}').delete()
            db.reference(f'REURB_V1/proprietarios/{id_proj}').delete()

            st.session_state['pagina_atual'] = 'Início'
            st.session_state['projeto_ativo'] = None
            st.session_state['nome_arquivo_original'] = None
            st.success('Núcleo excluído com sucesso!')
            st.rerun()
        except Exception as e:
          st.error(f'Erro ao excluir núcleo: {e}')

  with st.form('form_n'):
    c1, c2 = st.columns(2)
    nome_n = c1.text_input('Nome do Núcleo', value=p.get('nome', ''))
    local = c1.text_input('Localização', value=p.get('local', ''))
    mod = c1.selectbox(
        'Modalidade',
        ['Reurb-S (Social)', 'Reurb-E (Específica)'],
        index=(
            0
            if p.get('modalidade') == 'Reurb-S (Social)'
            else (1 if p.get('modalidade') == 'Reurb-E (Específica)' else 0)
        ),
    )

    num_crf = c1.text_input(
        'Número da CRF',
        value=p.get('num_crf', p.get('num_decreto', '')),
        placeholder='Ex: 01',
    )
    ano_crf = c1.text_input(
        'Ano da CRF',
        value=p.get('ano_crf', p.get('ano_decreto', '')),
        placeholder='Ex: 2026',
    )

    val_area_original = p.get('area_total', '0,00')
    if isinstance(val_area_original, (int, float)):
      val_area_str = (
          f'{val_area_original:,.2f}'
          .replace(',', 'X')
          .replace('.', ',')
          .replace('X', '.')
      )
    else:
      val_area_str = str(val_area_original)

    val_viaria_original = p.get('area_viaria', '0,00')
    if isinstance(val_viaria_original, (int, float)):
      val_viaria_str = (
          f'{val_viaria_original:,.2f}'
          .replace(',', 'X')
          .replace('.', ',')
          .replace('X', '.')
      )
    else:
      val_viaria_str = str(val_viaria_original)

    area_txt = c2.text_input(
        'Área Total (m²)', value=val_area_str, placeholder='00.000,00'
    )
    ruas = c2.number_input('Qtd Ruas', step=1, value=int(p.get('ruas', 0)))
    viario_txt = c2.text_input(
        'Área Viária (m²)', value=val_viaria_str, placeholder='00.000,00'
    )

    padrao_q = len(p.get('quadras', [])) if editando else 1
    qtd_q = st.number_input(
        'Quantidade de Quadras', min_value=1, step=1, value=max(1, padrao_q)
    )

    lista_q = []
    col_q = st.columns(4)
    for i in range(int(qtd_q)):
      val_q = (
          p['quadras'][i]['quadra']
          if editando and i < len(p['quadras'])
          else f'{i+1}'
      )
      val_l = (
          p['quadras'][i]['lotes'] if editando and i < len(p['quadras']) else 0
      )
      with col_q[i % 4]:
        qid = st.text_input(f'Nº Q. {i+1}', value=val_q, key=f'nq_{i}')
        qlt = st.number_input(
            f'Lotes Q.{qid}',
            min_value=0,
            step=1,
            value=int(val_l),
            key=f'nl_{i}',
        )
        lista_q.append({'quadra': qid, 'lotes': qlt})

    if st.form_submit_button('Salvar'):
      try:
        area_limpa = area_txt.replace('.', '').replace(',', '.')
        area_float = float(area_limpa) if area_limpa else 0.0
      except ValueError:
        area_float = 0.0

      try:
        viario_limpo = viario_txt.replace('.', '').replace(',', '.')
        viario_float = float(viario_limpo) if viario_limpo else 0.0
      except ValueError:
        viario_float = 0.0

      novo_p = {
          'nome': nome_n,
          'local': local,
          'modalidade': mod,
          'num_crf': num_crf,
          'ano_crf': ano_crf,
          'area_total': area_float,
          'ruas': ruas,
          'area_viaria': viario_float,
          'quadras': lista_q,
      }

      crf_sufixo = (
          f"_crf_{num_crf.strip()}_{ano_crf.strip()}"
          if num_crf.strip() and ano_crf.strip()
          else ''
      )
      novo_id = f"projeto_{nome_n.replace(' ', '_').lower()}{crf_sufixo}"

      if editando and st.session_state.get('nome_arquivo_original'):
        antigo_id = st.session_state['nome_arquivo_original']
        if antigo_id != novo_id:
          dados_prop = db.reference(f'REURB_V1/proprietarios/{antigo_id}').get()
          if dados_prop:
            db.reference(f'REURB_V1/proprietarios/{novo_id}').set(dados_prop)
            db.reference(f'REURB_V1/proprietarios/{antigo_id}').delete()
          db.reference(f'REURB_V1/projetos/{antigo_id}').delete()

      db.reference(f'REURB_V1/projetos/{novo_id}').set(novo_p)

      st.session_state['pagina_atual'] = 'Início'
      st.session_state['projeto_ativo'] = None
      st.session_state['nome_arquivo_original'] = None
      st.rerun()