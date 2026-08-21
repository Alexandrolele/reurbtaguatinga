import re
from validate_docbr import CPF, CNPJ
import streamlit as st
from firebase_admin import db


def renderizar_quadra():
  p = st.session_state.get("projeto_ativo", {})
  id_proj = st.session_state.get("nome_arquivo_original", "")
  q_ativa = st.session_state.get("quadra_ativa", "")

  # Botão Voltar para o Núcleo
  if st.button("⬅️ Voltar"):
    st.session_state["pagina_atual"] = "detalhes_projeto"
    st.rerun()

  st.title(f"👤 Cadastro - Quadra {q_ativa}")
  st.markdown("---")

  # Consulta os ocupantes já cadastrados nesta quadra no Firebase
  ref_prop = db.reference(f"REURB_V1/proprietarios/{id_proj}")
  dados_proprietarios = ref_prop.get() or {}

  ocupantes_quadra = {}
  for chave_lote, info_lote in dados_proprietarios.items():
    if str(info_lote.get("quadra")) == str(q_ativa):
      ocupantes_quadra[chave_lote] = info_lote

  # Opção de copiar dados de ocupante já cadastrado
  opcoes_copia = [
      "-- Selecione para copiar dados (Múltiplos Lotes) --"
  ] + [
      f"Lote {v.get('lote')} - {v.get('nome', '')}"
      for v in ocupantes_quadra.values()
  ]
  escolha_copia = st.selectbox(
      "Copiar dados de ocupante já cadastrado:", opcoes_copia
  )

  dados_copiados = {}
  if escolha_copia != "-- Selecione para copiar dados (Múltiplos Lotes) --":
    nome_selecionado = escolha_copia.split(" - ")[1]
    for v in ocupantes_quadra.values():
      if v.get("nome") == nome_selecionado:
        dados_copiados = v
        break

  # Formulário de Cadastro do Ocupante
  with st.form("form_ocupante", clear_on_submit=True):
    st.subheader("Dados do Ocupante")
    c1, c2, c3 = st.columns(3)

    lote = c1.text_input("Lote Nº", value="")
    matricula = c2.text_input(
        "Matrícula", value=str(dados_copiados.get("matricula", ""))
    )
    nome = c3.text_input(
        "Nome Completo", value=str(dados_copiados.get("nome", ""))
    )

    c4, c5, c6 = st.columns(3)
    estado_civil = c4.selectbox(
        "Estado Civil",
        [
            "Solteiro(a)",
            "Casado(a)",
            "Divorciado(a)",
            "Viúvo(a)",
            "União Estável",
            "Não Aplicável (Pessoa Jurídica)",
        ],
        index=0,
    )
    profissao = c5.text_input(
        "Profissão", value=str(dados_copiados.get("profissao", ""))
    )
    cpf = c6.text_input(
        "CPF ou CNPJ",
        value=str(dados_copiados.get("cpf", "")),
        placeholder="000.000.000-00 ou CNPJ",
    )

    c7, c8, c9 = st.columns(3)
    rg = c7.text_input(
        "CI/RG",
        value=str(dados_copiados.get("rg", "")),
        placeholder="Opcional para CNPJ",
    )
    ssp = c8.text_input("SSP/UF", value=str(dados_copiados.get("ssp", "")))
    endereco = c9.text_input(
        "Endereço", value=str(dados_copiados.get("endereco", ""))
    )

    c10, c11, c12 = st.columns(3)
    bairro = c10.text_input("Bairro", value=str(dados_copiados.get("bairro", "")))
    cidade = c11.text_input(
        "Cidade", value=str(dados_copiados.get("cidade", "Taguatinga"))
    )
    uf = c12.text_input("UF", value=str(dados_copiados.get("uf", "TO")))

    st.markdown("---")
    st.subheader("Dados do Cônjuge / Herdeiro 🔗")

    cc1, cc2, cc3 = st.columns(3)
    nome_conj = cc1.text_input(
        "Nome (Cônjuge/Herdeiro)", value=str(dados_copiados.get("nome_conj", ""))
    )
    ec_conj = cc2.selectbox(
        "Estado Civil (Cônjuge/Herdeiro)",
        ["N/A", "Solteiro(a)", "Casado(a)", "União Estável"],
        index=0,
    )
    prof_conj = cc3.text_input(
        "Profissão (Cônjuge/Herdeiro)",
        value=str(dados_copiados.get("prof_conj", "")),
    )

    cc4, cc5, cc6 = st.columns(3)
    rg_conj = cc4.text_input(
        "CI/RG (Cônjuge/Herdeiro)", value=str(dados_copiados.get("rg_conj", ""))
    )
    ssp_conj = cc5.text_input(
        "SSP/UF (Cônjuge/Herdeiro)",
        value=str(dados_copiados.get("ssp_conj", "")),
    )
    cpf_conj = cc6.text_input(
        "CPF (Cônjuge/Herdeiro)",
        value=str(dados_copiados.get("cpf_conj", "")),
        placeholder="000.000.000-00",
    )

    salvar_oc = st.form_submit_button("Salvar Cadastro")

    if salvar_oc:
      doc_limpo = re.sub(r"\D", "", cpf)
      rg_limpo = re.sub(r"[\s.-]", "", rg)

      validador_cpf = CPF()
      validador_cnpj = CNPJ()

      doc_valido = False
      if len(doc_limpo) == 11:
        doc_valido = validador_cpf.validate(doc_limpo)
      elif len(doc_limpo) == 14:
        doc_valido = validador_cnpj.validate(doc_limpo)

      if not lote or not nome:
        st.error("Preencha ao menos o Lote Nº e o Nome Completo.")
      elif not doc_valido:
        st.error(
            "❌ Documento inválido! Certifique-se de digitar um CPF (11 dígitos)"
            " ou um CNPJ (14 dígitos) correto."
        )
      elif rg and not rg_limpo.isdigit():
        st.error("❌ RG INVÁLIDO: Digite apenas números.")
      else:
        chave_registro = f"q_{q_ativa}_lote_{lote}"
        dados_salvar = {
            "quadra": q_ativa,
            "lote": lote,
            "matricula": matricula,
            "nome": nome,
            "estado_civil": estado_civil,
            "profissao": profissao,
            "cpf": doc_limpo,
            "rg": rg.strip().upper(),
            "ssp": ssp,
            "endereco": endereco,
            "bairro": bairro,
            "cidade": cidade,
            "uf": uf,
            "nome_conj": nome_conj,
            "ec_conj": ec_conj,
            "prof_conj": prof_conj,
            "rg_conj": rg_conj,
            "ssp_conj": ssp_conj,
            "cpf_conj": cpf_conj,
        }
        db.reference(
            f"REURB_V1/proprietarios/{id_proj}/{chave_registro}"
        ).set(dados_salvar)
        st.success(f"Ocupante do Lote {lote} salvo com sucesso!")
        st.rerun()

  st.markdown("---")
  st.subheader(f"📋 Lista de Ocupantes - Quadra {q_ativa}")

  if not ocupantes_quadra:
    st.info("Nenhum ocupante cadastrado nesta quadra ainda.")
  else:
    # Cabeçalho da tabela com os nomes das colunas
    col_l_cab, col_m_cab, col_n_cab, col_a_cab = st.columns([1, 2, 5, 2])
    col_l_cab.markdown("**Lote**")
    col_m_cab.markdown("**Matrícula**")
    col_n_cab.markdown("**Nome**")
    col_a_cab.markdown("**Ações**")
    st.markdown("<hr style='margin: 5px 0 15px 0;'>", unsafe_allow_html=True)

    # Itens da lista
    for chave, dados_oc in ocupantes_quadra.items():
      col_l, col_m, col_n, col_a1, col_a2 = st.columns([1, 2, 5, 1, 1])
      col_l.write(f"{dados_oc.get('lote')}")
      col_m.write(f"{dados_oc.get('matricula', '')}")
      col_n.write(f"{dados_oc.get('nome', '')}")

      if col_a1.button("📝", key=f"edit_{chave}"):
        st.info(f"Função de edição para o lote {dados_oc.get('lote')}")
      if col_a2.button("🗑️", key=f"del_{chave}"):
        db.reference(f"REURB_V1/proprietarios/{id_proj}/{chave}").delete()
        st.success("Removido com sucesso!")
        st.rerun()