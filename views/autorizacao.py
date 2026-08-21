from datetime import datetime
import os
import re
from fpdf import FPDF
import pandas as pd
import streamlit as st
from validate_docbr import CPF, CNPJ
import firebase_admin
from firebase_admin import db


def gerar_pdf_autorizacao_fpdf(dados):
  """Gera o Título de Permissão com cabeçalho centralizado e tabela à direita."""
  pdf = FPDF(orientation="P", unit="mm", format="A4")
  pdf.add_page()
  pdf.set_margins(20, 20, 20)

  # --- FUNÇÕES DE APOIO ---
  def f(campo, transform=None):
    texto = (
        str(campo) if pd.notna(campo) and str(campo).lower() != "nan" else ""
    )
    if texto.endswith(".0"):
      texto = texto[:-2]
    if transform == "lower":
      return texto.lower()
    if transform == "upper":
      return texto.upper()
    return texto

  def limpar(txt):
    if not txt:
      return ""
    return str(txt).encode("latin-1", "replace").decode("latin-1")

  def formatar_documento(num_doc):
    num_doc = re.sub(r"\D", "", str(num_doc))
    if len(num_doc) == 11:
      return f"{num_doc[:3]}.{num_doc[3:6]}.{num_doc[6:9]}-{num_doc[9:]}"
    elif len(num_doc) == 14:
      return (
          f"{num_doc[:2]}.{num_doc[2:5]}.{num_doc[5:8]}/{num_doc[8:12]}-{num_doc[12:]}"
      )
    return num_doc

  # --- CABEÇALHO CENTRALIZADO ---
  pdf.set_y(12)
  pdf.set_font("Arial", "B", 12)
  pdf.cell(0, 6, limpar(""), ln=True, align="C")
  pdf.cell(0, 6, limpar(""), ln=True, align="C")
  pdf.set_font("Arial", "", 10)
  pdf.cell(0, 5, limpar(""), ln=True, align="C")
  pdf.ln(35)

  # --- TABELA DE IDENTIFICAÇÃO (DIREITA) ---
  hoje = datetime.now()
  meses = [
      "janeiro",
      "fevereiro",
      "março",
      "abril",
      "maio",
      "junho",
      "julho",
      "agosto",
      "setembro",
      "outubro",
      "novembro",
      "dezembro",
  ]
  data_curta = f"{hoje.day} de {meses[hoje.month-1]} de {hoje.year}"

  pdf.set_text_color(0, 0, 0)
  pdf.set_font("Arial", "B", 9)

  largura_tabela = 75
  x_inicial = 115
  pdf.set_x(x_inicial)

  titulo_num = f(dados.get("Titulo_Permissao"))
  livro_num = f(dados.get("Livro_Tombo"))
  folhas_num = f(dados.get("Fls"))

  pdf.cell(
      largura_tabela,
      7,
      limpar(f"TÍTULO DE PERMISSÃO Nº {titulo_num}"),
      border=1,
      ln=True,
      align="C",
  )

  pdf.set_x(x_inicial)
  pdf.cell(40, 7, limpar(f"LIVRO TOMBO Nº {livro_num}"), border=1, align="C")
  pdf.cell(35, 7, limpar(f"FLS. {folhas_num}"), border=1, ln=True, align="C")

  pdf.set_x(x_inicial)
  pdf.cell(
      largura_tabela,
      7,
      limpar(f"TAGUATINGA - TO, {data_curta}"),
      border=1,
      ln=True,
      align="C",
  )

  pdf.ln(10)

  # --- TÍTULO JURÍDICO ---
  pdf.set_font("Arial", "B", 10)
  pdf.set_left_margin(100)

  titulo_texto = (
      "TÍTULO DE PERMISSÃO PARA REGISTRO E TRANSFERÊNCIA DE DOMÍNIO QUE O"
      " MUNICÍPIO DE TAGUATINGA - TO OUTORGA À PESSOA CONTEMPLADA ABAIXO"
      " IDENTIFICADA, CONFORME AUTORIZAÇÃO DO DECRETO N.º 244/2025."
  )

  pdf.multi_cell(0, 5, limpar(titulo_texto), border=0, align="J")
  pdf.set_left_margin(20)
  pdf.ln(8)

  # --- CORPO DO TEXTO JURÍDICO ---
  pdf.set_font("Arial", "", 10)

  chanfro_txt = (
      (
          f", chanfro com {f(dados.get('Chanfro_Com'))}, medindo"
          f" {f(dados.get('Chanfro_M'))} metros"
      )
      if f(dados.get("Chanfro_Com"))
      else ""
  )
  
  doc_limpo = re.sub(r"\D", "", str(dados.get("CPF", "")))
  doc_formatado = formatar_documento(doc_limpo)
  is_cnpj = len(doc_limpo) == 14
  rotulo_doc = "CNPJ/MF nº" if is_cnpj else "CPF nº"

  v_rg = f(dados.get("RG"))
  v_ssp = f(dados.get("SSP"))
  v_uf = f(dados.get("UF_RG"))

  # Se for CNPJ ou não tiver RG preenchido, oculta a menção ao RG no texto
  if not is_cnpj and v_rg:
    rg_completo = f"{v_rg} {v_ssp}/{v_uf}".strip().replace(" /", "/")
    trecho_rg = f"portador(a) da CI/RG nº {rg_completo} e do {rotulo_doc} {doc_formatado}"
  elif is_cnpj:
    trecho_rg = f"inscrita no {rotulo_doc} {doc_formatado}"
  else:
    trecho_rg = f"do {rotulo_doc} {doc_formatado}"

  texto_corpo = (
      "MUNICIPIO DE TAGUATINGA-TO, pessoa jurídica de direito público interno,"
      " inscrita no CNPJ/MF sob a n° 02.306.900/0001-97 com sede administrativa"
      " sito à Avenida Airosa de Sousa Godinho, Quadra 10, Lote 11, s/nº Setor"
      " Bom Jesus Taguatinga TO, neste ato representado pelo Prefeito"
      " Municipal PAULO ROBERTO RIBEIRO, brasileiro, casado, empresário,"
      " portador da CI/RG nº 446.212 SDGPC-GO e do CPF/MF nº 088.124.461-91,"
      " residente e domiciliado em Taguatinga TO, a presente permissão é"
      " realizada com amparo no Processo Administrativo em epígrafe e em"
      " estrita consonância com as disposições do Decreto nº 244 de 10 de"
      " dezembro de 2025, de imóveis urbanos a partir de 80m², após detida"
      " análise dos documentos e provas juntadas pelo o Outorgado, a posse"
      " deste Título concede a plena autorização para a lavratura da"
      " competente Escritura Pública de Compra e Venda perante o Cartório de"
      " Notas e seu posterior e obrigatório registro junto ao Cartório de"
      " Registro de Imóveis. O procedimento de regularização será"
      " integralmente concluído após o recolhimento do Imposto sobre a"
      " Transmissão de Bens Imóveis (ITBI), ônus que será assumido por esta"
      f" Municipalidade, concernente ao LOTE URBANO n.º {f(dados['Lote'])},"
      f" Quadra: {f(dados['Quadra'])}, endereço do lote"
      f" {f(dados['End_Lote'])}, Setor {f(dados['Setor'])}. Dentro dos"
      " seguintes limites e confrontações: frente para a"
      f" {f(dados['Frente_Com'])}, com medida de {f(dados['Frente_M'])} metros;"
      f" fundos com o {f(dados['Fundo_Com'])}, com {f(dados['Fundo_M'])}"
      f" metros; lado direito com o {f(dados['Dir_Com'])}, com"
      f" {f(dados['Dir_M'])} metros e lado esquerdo com o"
      f" {f(dados['Esq_Com'])}, com {f(dados['Esq_M'])} metros{chanfro_txt},"
      f" com área total de {f(dados['Area_Total'])}m²,"
      f" ({f(dados['Area_Extenso'])}), conforme memorial descritivo,"
      f" Taguatinga/TO, ao (à) detentor (a), {f(dados['Nome'], 'upper')},"
      f" brasileiro(a), {f(dados['Estado Civil'], 'lower')},"
      f" {f(dados['Profissao'], 'lower')}, {trecho_rg}, residente na"
      f" {f(dados['End_Residencial'])}, {f(dados['Bairro_Residencial'])}. O"
      " Município de Taguatinga TO, aqui designado OUTORGANTE, é legítimo"
      " titular do domínio do imóvel público municipal, conforme Título"
      " Definitivo de Domínio nº 109/2014, lavrado no livro 85/2014, na folha"
      " 009 e expedido em Palmas TO, no dia 14/05/2014, pelo ITERTINS Instituto"
      " de Terras do Estado do Tocantins, registrado no Cartório de Registro"
      " de Imóveis e Tabelionato 1º de Notas da Comarca de Taguatinga TO, sob"
      " a Matrícula nº 2869, Livro 2-RGR-01 em 23/07/2014, posteriormente"
      f" desmembrado para a {f(dados['Lei_Aplicada'])}, em ato contínuo"
      f" desmembrado referido lote para a MATRÍCULA nº {f(dados['Matricula'])},"
      " recebido pela OUTORGANTE, conforme estabelecido no parágrafo 3º, do"
      " artigo 1º, da Lei Municipal n°438/2014. Certifica e da fé que foram"
      " cumpridas as exigências legais que capacitam e autorizam a"
      " ilustríssima senhora Oficiala de Registro de Imóveis que transfira a"
      " propriedade da matrícula que foi aberta no livro Geral de Reg. de"
      " Imóveis dessa Comarca. Pelo presente, o OUTORGANTE, na qualidade de"
      " legítimo titular do domínio, transfere e cede ao OUTORGADO todo o"
      " domínio, ações, direitos, jus e posse que até então exercia sobre o"
      " aludido imóvel, passando o OUTORGADO a consolidar e exercer o pleno"
      " DIREITO DE PROPRIEDADE sobre o lote em questão. O OUTORGADO declara"
      " aceitar o presente Título Definitivo de Domínio em todos os seus"
      " termos, cláusulas e condições. O presente Título é emitido em estrita"
      " observância ao Decreto nº 244/2025, que autoriza a transferência do"
      " domínio do imóvel, devidamente comprovada a titularidade do"
      f" OUTORGANTE conforme a Matrícula n.º {f(dados['Matricula'])}. O ato"
      " finaliza o Processo Administrativo n.º 01/2024 e habilita o registro"
      " imediato do pleno Direito de Propriedade em nome do OUTORGADO perante"
      " o Cartório de Registro de Imóveis. E por estarem justos, contratados e"
      " de pleno acordo com todas as condições estabelecidas, as partes"
      " firmam o presente Título de Domínio em 02 (duas) vias de igual teor e"
      " forma, que será devidamente assinado por elas e por 02 (duas)"
      " testemunhas."
  )
  pdf.multi_cell(0, 5, limpar(texto_corpo), align="J")
  pdf.ln(10)

  pdf.set_font("Arial", "I", 10)
  data_final = (
      f"Taguatinga-TO, {hoje.day} de {meses[hoje.month-1]} de {hoje.year}."
  )
  pdf.cell(0, 10, limpar(data_final), ln=True, align="R")
  pdf.ln(10)

  # --- ASSINATURAS PRINCIPAIS ---
  pdf.set_font("Arial", "B", 9)
  pdf.cell(0, 5, "__________________________________________", ln=True, align="C")
  pdf.cell(0, 5, limpar("PAULO ROBERTO RIBEIRO"), ln=True, align="C")
  pdf.set_font("Arial", "", 8)
  pdf.cell(0, 4, limpar("Prefeito Municipal"), ln=True, align="C")
  pdf.ln(8)

  pdf.set_font("Arial", "B", 9)
  pdf.cell(0, 5, "__________________________________________", ln=True, align="C")
  pdf.cell(0, 5, limpar("LUAN AIRES RIBEIRO"), ln=True, align="C")
  pdf.set_font("Arial", "", 8)
  pdf.cell(
      0, 4, limpar("Secretário de Regularização Fundiária"), ln=True, align="C"
  )
  pdf.ln(8)

  pdf.set_font("Arial", "B", 9)
  pdf.cell(0, 5, "__________________________________________", ln=True, align="C")
  pdf.cell(0, 5, limpar(f(dados["Nome"], "upper")), ln=True, align="C")
  pdf.set_font("Arial", "", 8)
  pdf.cell(0, 4, limpar("Outorgado Adquirente"), ln=True, align="C")
  pdf.ln(12)

  # --- TESTEMUNHAS ---
  pdf.set_font("Arial", "B", 9)
  pdf.cell(0, 5, "__________________________________________", ln=True, align="L")
  pdf.set_font("Arial", "", 8)
  pdf.cell(0, 4, limpar("Testemunha 01"), ln=True, align="L")
  pdf.cell(0, 4, limpar("CPF:_____._____._____-___"), ln=True, align="L")
  pdf.ln(8)

  pdf.set_font("Arial", "B", 9)
  pdf.cell(0, 5, "__________________________________________", ln=True, align="L")
  pdf.set_font("Arial", "", 8)
  pdf.cell(0, 4, limpar("Testemunha 02"), ln=True, align="L")
  pdf.cell(0, 4, limpar("CPF:_____._____._____-___"), ln=True, align="L")

  retorno_pdf = pdf.output(dest="S")
  if isinstance(retorno_pdf, str):
    return retorno_pdf.encode("latin-1")
  return bytes(retorno_pdf)


def salvar_registro(firebase_key, *args):
  colunas = [
      "Nome",
      "Nacionalidade",
      "Estado Civil",
      "Profissao",
      "RG",
      "SSP",
      "UF_RG",
      "CPF",
      "End_Residencial",
      "Bairro_Residencial",
      "Lote",
      "Quadra",
      "End_Lote",
      "Setor",
      "Frente_Com",
      "Frente_M",
      "Fundo_Com",
      "Fundo_M",
      "Dir_Com",
      "Dir_M",
      "Esq_Com",
      "Esq_M",
      "Area_Total",
      "Area_Extenso",
      "Matricula",
      "Lei_Aplicada",
      "Chanfro_Com",
      "Chanfro_M",
      "Titulo_Permissao",
      "Livro_Tombo",
      "Fls",
  ]

  novo_reg = dict(zip(colunas, args))

  try:
    ref = db.reference("autorizacoes")
    
    # Se temos uma chave de edição válida, atualizamos diretamente o registro existente (evita duplicação)
    if firebase_key:
      ref.child(firebase_key).set(novo_reg)
      st.success("✅ Registro atualizado com sucesso no Firebase!")
    else:
      # Se for novo, verifica duplicidade por CPF/CNPJ + Lote + Quadra antes de inserir
      existentes = ref.get()
      if existentes and isinstance(existentes, dict):
        for k, v in list(existentes.items()):
          if (
              v.get("CPF") == novo_reg["CPF"]
              and v.get("Lote") == novo_reg["Lote"]
              and v.get("Quadra") == novo_reg["Quadra"]
          ):
            db.reference(f"autorizacoes/{k}").delete()

      ref.push(novo_reg)
      st.success("✅ Dados salvos com sucesso no Firebase!")

  except Exception as e:
    st.error(f"Erro ao salvar no Firebase: {e}")
    return

  st.session_state.editar_autorizacao = None
  st.rerun()


def formulario_autorizacao(dados_edicao=None):
  firebase_key_edicao = None
  if dados_edicao is not None:
    firebase_key_edicao = dados_edicao.get("firebase_key")
    st.warning(
        f"📝 Editando: {dados_edicao.get('Nome', '')} (Lote"
        f" {dados_edicao.get('Lote','')}, Q. {dados_edicao.get('Quadra','')})"
    )
    if st.button("❌ Cancelar"):
      st.session_state.editar_autorizacao = None
      st.rerun()

  dados_autocompletar = {}

  try:
    ref = db.reference("autorizacoes")
    dados_fb = ref.get()
  except Exception:
    dados_fb = None

  if dados_fb and dados_edicao is None:
    if isinstance(dados_fb, dict):
      lista_regs = list(dados_fb.values())
    else:
      lista_regs = dados_fb

    df_existente = pd.DataFrame(lista_regs, dtype=str)
    if not df_existente.empty:
      df_unicos = df_existente.drop_duplicates(subset=["CPF", "Nome"])
      lista_pessoas = [
          "-- Selecione para copiar dados (Múltiplos Lotes) --"
      ] + [
          f"{row['Nome']} (Doc: {row['CPF']})"
          for _, row in df_unicos.iterrows()
      ]

      selecionado = st.selectbox(
          "👤 Copiar dados de requerente já cadastrado:", lista_pessoas
      )
      if selecionado != "-- Selecione para copiar dados (Múltiplos Lotes) --":
        nome_selecionado = selecionado.split(" (Doc:")[0]
        match_df = df_unicos[df_unicos["Nome"] == nome_selecionado]
        if not match_df.empty:
          dados_autocompletar = match_df.iloc[0].fillna("").to_dict()

  with st.form("form_autorizacao", clear_on_submit=False):
    if dados_edicao is not None:
      fonte_dados = dados_edicao
    else:
      fonte_dados = dados_autocompletar

    st.subheader("👤 Requerente")
    col1, col2, col3 = st.columns([2, 1, 1])
    nome = col1.text_input("Nome", value=fonte_dados.get("Nome", ""))
    nacionalidade = col2.text_input(
        "Nacionalidade", value=fonte_dados.get("Nacionalidade", "Brasileiro")
    )

    opcoes_civil = [
        "Solteiro(a)",
        "Casado(a)",
        "Divorciado(a)",
        "Viúvo(a)",
        "União Estável",
        "Pessoa Jurídica",
    ]
    civil_salvo = fonte_dados.get("Estado Civil", "Solteiro(a)")
    idx_civil = (
        opcoes_civil.index(civil_salvo) if civil_salvo in opcoes_civil else 0
    )
    estado_civil = col3.selectbox("Estado Civil", opcoes_civil, index=idx_civil)

    c1, c2, c3, c4 = st.columns([1.5, 1, 0.5, 1.5])
    profissao = c1.text_input("Profissão", value=fonte_dados.get("Profissao", ""))
    rg = c2.text_input(
        "RG", value=fonte_dados.get("RG", ""), placeholder="Opcional para CNPJ"
    )
    ssp = c3.text_input("SSP", value=fonte_dados.get("SSP", ""))
    uf_rg = c4.text_input("UF", value=fonte_dados.get("UF_RG", "TO"))

    col_cpf, col_end, col_bairro = st.columns([1.5, 2, 1])
    cpf = col_cpf.text_input(
        "CPF ou CNPJ",
        value=fonte_dados.get("CPF", ""),
        placeholder="000.000.000-00 ou CNPJ",
    )
    endereco_res = col_end.text_input(
        "Endereço", value=fonte_dados.get("End_Residencial", "")
    )
    bairro_res = col_bairro.text_input(
        "Bairro", value=fonte_dados.get("Bairro_Residencial", "")
    )

    st.divider()
    st.subheader("🏘️ Lote")
    l1, l2, l3, l4 = st.columns([1, 1, 2, 1])
    lote_num = l1.text_input("Lote Nº", value=fonte_dados.get("Lote", ""))
    quadra_num = l2.text_input("Quadra", value=fonte_dados.get("Quadra", ""))
    end_lote = l3.text_input(
        "Endereço do Lote", value=fonte_dados.get("End_Lote", "")
    )
    setor = l4.text_input("Setor", value=fonte_dados.get("Setor", ""))

    st.divider()
    st.subheader("📏 Confrontações")
    f1, f2 = st.columns(2)
    finter_c = f1.text_input(
        "Frente com", value=fonte_dados.get("Frente_Com", "")
    )
    finter_m = f2.text_input("Frente (m)", value=fonte_dados.get("Frente_M", ""))
    f3, f4 = st.columns(2)
    fundo_c = f3.text_input(
        "Fundo com", value=fonte_dados.get("Fundo_Com", "")
    )
    fundo_m = f4.text_input("Fundo (m)", value=fonte_dados.get("Fundo_M", ""))
    f5, f6 = st.columns(2)
    dir_c = f5.text_input("Direita com", value=fonte_dados.get("Dir_Com", ""))
    dir_m = f6.text_input("Direita (m)", value=fonte_dados.get("Dir_M", ""))
    f7, f8 = st.columns(2)
    esq_c = f7.text_input("Esquerda com", value=fonte_dados.get("Esq_Com", ""))
    esq_m = f8.text_input("Esquerda (m)", value=fonte_dados.get("Esq_M", ""))

    st.write("**📐 Chanfro (Opcional)**")
    ch1, ch2 = st.columns(2)
    chan_c = ch1.text_input(
        "Chanfro com", value=fonte_dados.get("Chanfro_Com", "")
    )
    chan_m = ch2.text_input("Chanfro (m)", value=fonte_dados.get("Chanfro_M", ""))

    st.write("---")
    area_t = st.text_input("Área Total", value=fonte_dados.get("Area_Total", ""))
    area_e = st.text_area(
        "Área Extenso", value=fonte_dados.get("Area_Extenso", "")
    )

    col_mat, col_lei = st.columns(2)
    matr = col_mat.text_input("Matrícula", value=fonte_dados.get("Matricula", ""))

    opcoes_leis = [
        "MATRÍCULA nº 5.771 - Setor Norte 2° ETAPA",
        "MATRÍCULA nº 6.043 - Setor Buritizinho",
        "MATRÍCULA nº 3.752 - Setor Leste",
        "MATRÍCULA nº 4.244 - Setor Serra Azul",
        "MATRÍCULA nº 4.527 - Setor Bom Jesus",
        "MATRÍCULA nº 3.470 - Setor Vila Santa Maria Leste",
    ]
    lei_atual = fonte_dados.get("Lei_Aplicada", "")
    lei_selecionada = col_lei.selectbox(
        "Legislação Aplicável",
        options=opcoes_leis,
        index=opcoes_leis.index(lei_atual) if lei_atual in opcoes_leis else 0,
    )

    st.subheader("📑 Informações do Título")
    nt1, nt2, nt3 = st.columns([1.5, 1.5, 1])
    titulo_permissao = nt1.text_input(
        "TÍTULO DE PERMISSÃO Nº", value=fonte_dados.get("Titulo_Permissao", "")
    )
    livro_tombo = nt2.text_input(
        "LIVRO TOMBO Nº", value=fonte_dados.get("Livro_Tombo", "")
    )
    fls = nt3.text_input("FLS.", value=fonte_dados.get("Fls", ""))

    if st.form_submit_button("💾 SALVAR"):
      doc_limpo = re.sub(r"\D", "", cpf)
      rg_limpo = re.sub(r"[\s.-]", "", rg)

      validador_cpf = CPF()
      validador_cnpj = CNPJ()

      doc_valido = False
      if len(doc_limpo) == 11:
        doc_valido = validador_cpf.validate(doc_limpo)
      elif len(doc_limpo) == 14:
        doc_valido = validador_cnpj.validate(doc_limpo)

      if not doc_valido:
        st.error(
            "❌ Documento inválido! Certifique-se de digitar um CPF (11 dígitos)"
            " ou um CNPJ (14 dígitos) correto."
        )
      elif rg and not rg_limpo.isdigit():
        st.error("❌ RG INVÁLIDO: Digite apenas números.")
      elif not lote_num or not quadra_num:
        st.error("❌ O preenchimento do Lote e da Quadra é obrigatório.")
      else:
        salvar_registro(
            firebase_key_edicao,
            nome,
            nacionalidade,
            estado_civil,
            profissao,
            rg.strip().upper(),
            ssp,
            uf_rg,
            doc_limpo,
            endereco_res,
            bairro_res,
            lote_num,
            quadra_num,
            end_lote,
            setor,
            finter_c,
            finter_m,
            fundo_c,
            fundo_m,
            dir_c,
            dir_m,
            esq_c,
            esq_m,
            area_t,
            area_e,
            matr,
            lei_selecionada,
            chan_c,
            chan_m,
            titulo_permissao,
            livro_tombo,
            fls,
        )


def lista_e_gestao():
  try:
    ref = db.reference("autorizacoes")
    dados_fb = ref.get()
  except Exception as e:
    st.error(f"Erro ao carregar dados do Firebase: {e}")
    return

  if not dados_fb:
    st.info("Nenhum dado cadastrado.")
    return

  if isinstance(dados_fb, dict):
    lista_regs = [{"firebase_key": k, **v} for k, v in dados_fb.items()]
  else:
    lista_regs = dados_fb

  df = pd.DataFrame(lista_regs, dtype=str)

  busca = st.text_input("🔍 Pesquisar")
  if busca and not df.empty:
    df = df[
        df["Nome"].str.contains(busca, case=False, na=False)
        | df["CPF"].str.contains(busca, na=False)
    ]

  if df.empty:
    st.info("Nenhum registro encontrado com o termo pesquisado.")
    return

  for idx, row in df.iterrows():
    with st.container(border=True):
      c1, c2, c3, c4 = st.columns([2.5, 0.8, 0.8, 1.2])
      c1.write(
          f"👤 **{row.get('Nome', 'N/A')}**  \n📍 Lote {row.get('Lote', 'N/A')} -"
          f" Quadra {row.get('Quadra', 'N/A')} - Setor"
          f" {row.get('Setor', 'N/A')}"
      )

      if c2.button("📝", key=f"e_{row.get('firebase_key', idx)}"):
        st.session_state.editar_autorizacao = row.to_dict()
        st.rerun()

      if c3.button("🗑️", key=f"d_{row.get('firebase_key', idx)}"):
        f_key = row.get("firebase_key")
        if f_key:
          try:
            db.reference(f"autorizacoes/{f_key}").delete()
            st.success("Registro excluído com sucesso!")
            st.rerun()
          except Exception as e:
            st.error(f"Erro ao excluir: {e}")

      pdf_bytes = gerar_pdf_autorizacao_fpdf(row)
      c4.download_button(
          "📄 PDF",
          pdf_bytes,
          f"Titulo_{str(row.get('Nome', 'morador')).replace(' ', '_')}_Lote_{row.get('Lote', '0')}.pdf",
          "application/pdf",
          key=f"p_{row.get('firebase_key', idx)}",
      )


def exibir_pagina():
  st.title("📄 Título de Permissão")
  t1, t2 = st.tabs(["Novo", "Gerenciar"])
  with t1:
    formulario_autorizacao(st.session_state.get("editar_autorizacao"))
  with t2:
    lista_e_gestao()


if __name__ == "__main__":
  exibir_pagina()