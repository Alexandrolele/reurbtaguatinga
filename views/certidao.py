from datetime import datetime
import io
import re
import pandas as pd
import streamlit as st
from firebase_admin import db

# Importações do ReportLab para construir os PDFs
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

# --- FUNÇÃO DE AUXÍLIO PARA FORMATAR CPF ---
def formatar_cpf_display(valor):
    if not valor or str(valor).lower() in ['nan', 'none', 'n/a']: 
        return "N/A"
    
    val_str = str(valor).split('.')[0]
    cpf_limpo = re.sub(r'\D', '', val_str)
    
    if 0 < len(cpf_limpo) < 11:
        cpf_limpo = cpf_limpo.zfill(11)
        
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[0:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:11]}"
        
    return str(valor).strip()

# --- FUNÇÃO DE AUXÍLIO PARA TRATAR TEXTO E ENCODING ---
def limpar_texto(txt):
    if txt is None or str(txt).lower() in ['nan', 'none', 'n/a']: 
        return ""
    return str(txt).strip()

# --- FUNÇÃO GERADORA DE PDF ---
def construir_pdf_certidao(dados_projeto, moradores_df, data_emissao, morador_unico_row=None):
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=50, leftMargin=50, 
        topMargin=140, bottomMargin=25
    )
    
    styles = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle(
        'TituloOficial', 
        parent=styles['Normal'], 
        fontSize=14, 
        leading=18, 
        alignment=TA_CENTER, 
        fontName='Helvetica-Bold'
    )
    
    estilo_corpo = ParagraphStyle(
        'CorpoTexto', 
        parent=styles['Normal'], 
        fontSize=11, 
        leading=15, 
        alignment=TA_JUSTIFY, 
        fontName='Helvetica'
    )
    
    estilo_assinatura = ParagraphStyle(
        'AssinaturaBloco', 
        parent=styles['Normal'], 
        fontSize=10, 
        leading=13, 
        alignment=TA_CENTER, 
        fontName='Helvetica'
    )

    story = []
    
    if morador_unico_row is not None:
        lista_moradores = [morador_unico_row]
    else:
        df_trabalho = moradores_df.copy()
        # Normaliza colunas para minúsculo para evitar erros
        df_trabalho.columns = [str(c).lower() for c in df_trabalho.columns]
        df_trabalho['quadra_int'] = pd.to_numeric(df_trabalho.get('quadra', 0), errors='coerce')
        df_trabalho['lote_int'] = pd.to_numeric(df_trabalho.get('lote', 0), errors='coerce')
        df_ordenado = df_trabalho.sort_values(by=['quadra_int', 'lote_int', 'quadra', 'lote'])
        lista_moradores = [row for _, row in df_ordenado.iterrows()]

    total_registros = len(lista_moradores)
    nome_nucleo = limpar_texto(dados_projeto.get('nome', '')).upper()
    modalidade_projeto = limpar_texto(dados_projeto.get('modalidade', 'Reurb-S (Social)'))
    local_projeto = limpar_texto(dados_projeto.get('local', 'Taguatinga-TO'))
    
    meses = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
        'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
        'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
        'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    }

    for idx, row in enumerate(lista_moradores):
        # Trata se o row é Series do pandas ou dicionário comum
        def get_val(r, chave):
            if hasattr(r, 'get'):
                val = r.get(chave) or r.get(chave.lower()) or r.get(chave.capitalize())
                return val if val is not None else 'N/A'
            return 'N/A'

        story.append(Paragraph("<b>CERTIDÃO DE REGULARIZAÇÃO FUNDIÁRIA INDIVIDUAL</b>", estilo_titulo))
        story.append(Paragraph(f"<b>INTEGRANTE DA CRF NÚCLEO: {nome_nucleo}</b>", estilo_titulo))
        story.append(Spacer(1, 20)) 
        
        m_nome = limpar_texto(get_val(row, 'nome'))
        m_cpf = formatar_cpf_display(get_val(row, 'cpf'))
        m_rg = limpar_texto(get_val(row, 'rg'))
        m_ssp = limpar_texto(get_val(row, 'ssp'))
        m_est_civil = limpar_texto(get_val(row, 'estado_civil') or get_val(row, 'estado civil'))
        m_profissao = limpar_texto(get_val(row, 'profissao'))
        m_endereco = limpar_texto(get_val(row, 'endereco'))
        m_bairro = limpar_texto(get_val(row, 'bairro'))
        m_quadra = limpar_texto(get_val(row, 'quadra'))
        m_lote = limpar_texto(get_val(row, 'lote'))
        m_matricula = limpar_texto(get_val(row, 'matricula'))

        rg_completo = f"{m_rg} {m_ssp}".strip() if m_ssp else m_rg

        texto_formal = f"""
        O <b>MUNICÍPIO DE TAGUATINGA</b>, Estado do Tocantins, por meio de seu Departamento de Regularização Fundiária, no uso de suas atribuições legais e em conformidade com a Lei Federal nº 13.465/2017, <b>CERTIFICA</b> para os devidos fins de direito e registro cartorário que o imóvel abaixo caracterizado foi devidamente regularizado, integrando o projeto de Regularização Fundiária Urbana (REURB), na modalidade <b>{modalidade_projeto}</b>.
        <br/><br/>
        <b> 1 - QUALIFICAÇÃO DO(A) BENEFICIÁRIO(A) TITULAR:</b><br/>
        • <b>Nome Completo:</b> {m_nome}<br/>
        • <b>Inscrição no CPF/MF:</b> {m_cpf} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Cédula de Identidade (RG):</b> {rg_completo}<br/>
        • <b>Estado Civil:</b> {m_est_civil} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Profissão:</b> {m_profissao}<br/>
        • <b>Endereço:</b> {m_endereco}, Bairro: {m_bairro}, Taguatinga-TO.<br/><br/>
        <b> 2 - CARACTERÍSTICAS E LOCALIZAÇÃO DO IMÓVEL:</b><br/>
        • <b>Núcleo Urbano:</b> {nome_nucleo}<br/>
        • <b>Localização/Setor:</b> {local_projeto}<br/>
        • <b>Quadra:</b> {m_quadra} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Lote:</b> {m_lote}<br/>
        • <b>Matrícula Imobiliária Correspondente:</b> {m_matricula}<br/>
        """
        story.append(Paragraph(texto_formal, estilo_corpo))
        story.append(Spacer(1, 8)) 
        
        data_formatada = data_emissao.strftime('%d de %B de %Y')
        for eng, pt in meses.items():
            data_formatada = data_formatada.replace(eng, pt)
            
        texto_encerramento = f"""
        Por ser a expressão da verdade, firmo a presente certidão para que surta seus efeitos jurídicos e legais junto ao Cartório de Registro de Imóveis competente.
        <br/><br/>
        Taguatinga - TO, {data_formatada}.
        """ 
        story.append(Paragraph(texto_encerramento, estilo_corpo))
        story.append(Spacer(1, 35))
        
        # Bloco de Assinaturas
        p_prefeito = Paragraph("""
            __________________________________________________________<br/>
            <b>Paulo Roberto Ribeiro</b><br/>
            Prefeito Municipal de Taguatinga - TO
        """, estilo_assinatura)
        
        p_viceprefeita = Paragraph("""
            __________________________________________________________<br/>
            <b>Izabella Antunes de França</b><br/>
            Vice-Prefeita Municipal de Taguatinga - TO
        """, estilo_assinatura)

        p_secretario = Paragraph("""
            __________________________________________________________<br/>
            <b>Luan Aires Ribeiro</b><br/>
            Secretário Municipal de Regularização Fundiária
        """, estilo_assinatura)
        
        tabela_assinaturas = Table([
            [p_prefeito],
            [Spacer(1, 15)], 
            [p_viceprefeita],
            [Spacer(1, 15)],
            [p_secretario]
        ], colWidths=[512])
        
        tabela_assinaturas.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        
        story.append(tabela_assinaturas)
        
        if idx < total_registros - 1:
            story.append(PageBreak())
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# --- FUNÇÃO PRINCIPAL DE RENDERIZAÇÃO DA PÁGINA STREAMLIT ---
def renderizar_relatorios():
    st.title("📜 Central de Certidões REURB")
    st.caption("Emissão de documentos em lote para entrega oficial ou busca direcionada de segunda via.")
    st.write("<br>", unsafe_allow_html=True)

    try:
        ref_projetos = db.reference("REURB_V1/projetos")
        dados_projetos_fb = ref_projetos.get()
    except Exception as e:
        st.error(f"Erro ao carregar projetos do Firebase: {e}")
        return

    if not dados_projetos_fb:
        st.info("🏛️ Nenhum núcleo ou projeto urbanístico foi cadastrado no sistema ainda.")
        return

    nomes_projetos = {}
    if isinstance(dados_projetos_fb, dict):
        for proj_id, d in dados_projetos_fb.items():
            if isinstance(d, dict) and 'nome' in d:
                nomes_projetos[d['nome']] = (d, proj_id)

    if not nomes_projetos:
        st.info("🏛️ Nenhum núcleo ou projeto urbanístico válido foi encontrado no Firebase.")
        return

    aba_completa, aba_individual = st.tabs([
        "📦 Certidão Coletiva (Entrega Oficial)", 
        "👤 Certidão Individual (Segunda Via)"
    ])

    # 1. ABA: CERTIDÃO COLETIVA DO SETOR
    with aba_completa:
        st.subheader("Emissão Completa do Setor")
        st.markdown("""
        Esta opção é ideal para a **fase de entrega dos títulos**. Ela gera um único arquivo PDF 
        consolidado contendo a certidão de todos os moradores cadastrados no setor, aplicando automaticamente 
        **uma quebra de página para cada lote/matrícula**. O espaçamento foi configurado para **papel timbrado**.
        """)
        
        with st.container(border=True):
            projeto_sel_c = st.selectbox(
                "Selecione o Núcleo Urbano para processamento coletivo:", 
                options=list(nomes_projetos.keys()),
                key="sb_proj_coletivo"
            )
            
            data_emissao_c = st.date_input(
                "Data oficial de emissão do documento:", 
                value=datetime.today().date(),
                format="DD/MM/YYYY",
                key="dt_coletivo"
            )
            
            st.write("<br>", unsafe_allow_html=True)
            
            dados_p, proj_id = nomes_projetos[projeto_sel_c]
            
            try:
                ref_prop = db.reference(f"REURB_V1/proprietarios/{proj_id}")
                dados_prop_fb = ref_prop.get()
            except Exception:
                dados_prop_fb = None
            
            df_cadastrados = pd.DataFrame()
            if dados_prop_fb:
                if isinstance(dados_prop_fb, dict):
                    lista_regs = list(dados_prop_fb.values())
                else:
                    lista_regs = dados_prop_fb
                df_cadastrados = pd.DataFrame(lista_regs)
            
            if not df_cadastrados.empty:
                qtd_moradores = len(df_cadastrados)
                
                st.info(f"📊 O núcleo **{projeto_sel_c}** possui atualmente **{qtd_moradores}** lotes/ocupantes cadastrados.")
                
                if st.button("🚀 Processar e Compilar Certidão Coletiva", type="primary", key="btn_gerar_coletivo"):
                    with st.spinner("Estruturando páginas para papel timbrado..."):
                        try:
                            pdf_data = construir_pdf_certidao(dados_p, df_cadastrados, data_emissao_c, morador_unico_row=None)
                            
                            st.success(f"✅ Sucesso! Arquivo pronto com {qtd_moradores} páginas exclusivas.")
                            st.download_button(
                                label="⬇️ Baixar Arquivo de Impressão Coletiva",
                                data=pdf_data,
                                file_name=f"Certidao_COLETIVA_{projeto_sel_c.replace(' ', '_').upper()}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Erro crítico ao gerar o PDF Coletivo: {e}")
            else:
                st.warning("⚠️ Não existem ocupantes ou lotes cadastrados na planilha deste núcleo para gerar o documento.")

    # 2. ABA: CERTIDÃO INDIVIDUAL
    with aba_individual:
        st.subheader("Busca de Ocupante e Emissão de Segunda Via")
        st.markdown("""
        Utilize esta ferramenta para o **atendimento de balcão**. Se um morador precisar de uma segunda via 
        ou via avulsa da certidão dele, digite o nome, CPF ou Lote para imprimir **apenas a folha dele** imediatamente.
        """)
        
        projeto_sel_i = st.selectbox(
            "Selecione o Núcleo Urbano para busca:", 
            options=list(nomes_projetos.keys()),
            key="sb_proj_individual"
        )
        
        dados_p, proj_id = nomes_projetos[projeto_sel_i]
        
        try:
            ref_prop = db.reference(f"REURB_V1/proprietarios/{proj_id}")
            dados_prop_fb = ref_prop.get()
        except Exception:
            dados_prop_fb = None
        
        df_cadastrados = pd.DataFrame()
        if dados_prop_fb:
            if isinstance(dados_prop_fb, dict):
                lista_regs = list(dados_prop_fb.values())
            else:
                lista_regs = dados_prop_fb
            df_cadastrados = pd.DataFrame(lista_regs).fillna("")
        
        if not df_cadastrados.empty:
            busca = st.text_input("🔍 Digite o Nome, CPF ou Número do Lote para filtrar:", placeholder="Ex: João da Silva / 000.000... / Lote 02")
            
            # Normaliza colunas do dataframe para busca flexível
            df_busca = df_cadastrados.copy()
            df_busca.columns = [str(c).lower() for c in df_busca.columns]
            
            if busca:
                col_nome = 'nome' if 'nome' in df_busca.columns else df_busca.columns[0]
                col_cpf = 'cpf' if 'cpf' in df_busca.columns else col_nome
                col_lote = 'lote' if 'lote' in df_busca.columns else col_nome
                
                mask = (
                    df_busca[col_nome].astype(str).str.contains(busca, case=False, na=False) |
                    df_busca[col_cpf].astype(str).str.contains(busca, na=False) |
                    df_busca[col_lote].astype(str).str.contains(busca, na=False)
                )
                df_filtrado = df_cadastrados[mask]
            else:
                df_filtrado = df_cadastrados

            st.write("---")
            
            if not df_filtrado.empty:
                st.caption(f"Exibindo {len(df_filtrado)} registro(s) localizado(s):")
                
                max_exibicao = 20
                if len(df_filtrado) > max_exibicao:
                    st.warning(f"Exibindo os primeiros {max_exibicao} resultados. Refine sua busca para encontrar outros registros.")
                    df_exibir = df_filtrado.head(max_exibicao)
                else:
                    df_exibir = df_filtrado

                for idx, row in df_exibir.iterrows():
                    def r_get(k):
                        return row.get(k) or row.get(k.lower()) or row.get(k.capitalize()) or ""

                    m_nome = r_get('nome')
                    m_cpf = formatar_cpf_display(r_get('cpf'))
                    m_rg = r_get('rg')
                    m_ssp = r_get('ssp')
                    m_quadra = r_get('quadra')
                    m_lote = r_get('lote')
                    m_matricula = r_get('matricula')

                    with st.container(border=True):
                        col_dados, col_botao = st.columns([3.5, 1.5])
                        
                        with col_dados:
                            st.markdown(f"👤 **{m_nome}**")
                            st.markdown(f"💳 **CPF:** {m_cpf} &nbsp;|&nbsp; 📝 **RG:** {m_rg} {m_ssp}")
                            st.caption(f"📍 Quadra: {m_quadra} &nbsp;•&nbsp; Lote: {m_lote} &nbsp;•&nbsp; Matrícula: {m_matricula}")
                        
                        with col_botao:
                            data_emissao_i = st.date_input(
                                "Emissão da 2ª Via:", 
                                value=datetime.today().date(),
                                format="DD/MM/YYYY",
                                key=f"dt_ind_{idx}"
                            )
                            
                            try:
                                pdf_individual_data = construir_pdf_certidao(dados_p, None, data_emissao_i, morador_unico_row=row)
                                
                                st.download_button(
                                    label="🖨️ Baixar 2ª Via",
                                    data=pdf_individual_data,
                                    file_name=f"Segunda_Via_Certidao_Lote_{m_lote}_{str(m_nome).replace(' ', '_').upper()}.pdf",
                                    mime="application/pdf",
                                    key=f"dl_ind_{idx}",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Erro ao gerar PDF: {e}")
            else:
                st.warning("❌ Nenhum morador ou lote foi localizado com o termo digitado.")
        else:
            st.error("⚠️ Este núcleo urbano ainda não possui nenhuma planilha de moradores cadastrada no Firebase.")