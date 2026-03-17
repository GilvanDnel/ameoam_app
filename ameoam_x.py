import streamlit as st
import PyPDF2
import requests
import re
import json
import pandas as pd
import base64
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv
from streamlit_pdf_viewer import pdf_viewer
# Carrega variáveis de ambiente
load_dotenv()

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E ESTILO VISUAL
# ==========================================
st.set_page_config(
    page_title="AMEOAM - Triagem & Orientação",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

def aplicar_estilo_customizado():
    st.markdown("""
        <style>
        /* Ajuste de espaçamentos desnecessários na Sidebar e Topo */
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 2rem;
        }
        
        .block-container {
            padding-top: 2rem;
            padding-bottom: 6rem; /* Espaço base para o computador */
        }

        /* MAGIA DA RESPONSIVIDADE: Aumenta o espaço no final da página só no celular */
        @media (max-width: 800px) {
            .block-container {
                padding-bottom: 12rem !important; /* Compensa a altura extra do texto quebrado */
            }
        }

        /* Título com Gradiente Neon */
        .titulo-gradiente {
            background: linear-gradient(90deg, #8B5CF6, #06B6D4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 0px;
            padding-bottom: 5px;
            line-height: 1.2;
        }
        
        /* Subtítulo mais sofisticado */
        .subtitulo {
            color: #94A3B8;
            font-size: 1.1rem;
            margin-bottom: 25px;
            font-weight: 300;
        }

        /* Botões Arredondados */
        div.stButton > button {
            border-radius: 30px;
            font-weight: bold;
            border: none;
            transition: all 0.3s ease;
            padding: 0.5rem 1rem;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
        }
        
        /* Ajuste sutil nas caixas de texto e upload */
        .stTextArea textarea, .stFileUploader {
            background-color: rgba(30, 41, 59, 0.5) !important;
            border-radius: 10px;
            border: 1px solid #334155;
        }

        /* ==========================================
           MAGIA DA RESPONSIVIDADE E ANIMAÇÃO
           ========================================== */
        
        /* A imagem será abstrata (sem fundo) e vai flutuar */
        .imagem-lateral img {
            border-radius: 0; 
            box-shadow: none; 
            max-width: 85%; 
            display: block;
            margin: 0 auto;
            animation: float 6s ease-in-out infinite; 
        }

        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-15px); }
            100% { transform: translateY(0px); }
        }

        /* Esconde a imagem completamente em celulares (telas menores que 800px) */
        @media (max-width: 800px) {
            [data-testid="column"]:nth-of-type(2) {
                display: none !important;
            }
        }

        /* Footer Customizado */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: rgba(11, 15, 25, 0.95);
            border-top: 1px solid #1E293B;
            color: #64748B;
            text-align: center;
            padding: 15px;
            font-size: 0.85rem;
            z-index: 999;
        }
        .footer a {
            color: #8B5CF6;
            text-decoration: none;
            font-weight: bold;
        }
                

        /* Estilo dos Cards de Ação (YouTube e Avaliação) */
        .card-acao {
            background-color: rgba(30, 41, 59, 0.5);
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            margin-bottom: 15px; /* A MÁGICA DO ESPAÇAMENTO IGUAL AQUI */
        }
        
        /* Efeito ao passar o mouse (Hover) aprimorado */
        .card-acao:hover {
            transform: translateY(-4px); /* Sobe um pouco mais */
            box-shadow: 0 6px 15px rgba(139, 92, 246, 0.4); /* Brilho neon mais forte */
            border-color: #8B5CF6; /* Borda muda para a cor do gradiente */
        }

        .card-acao a {
            color: #E2E8F0;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            display: block;
            width: 100%;
            height: 100%;
        }

        .card-icone {
            font-size: 1.5rem;
            margin-bottom: 5px;
        }
                
        /* ==========================================
           ESTILO DA BARRA LATERAL (SIDEBAR)
           ========================================== */
        
        /* Fundo da barra lateral ligeiramente diferente para dar contraste */
        [data-testid="stSidebar"] {
            background-color: #0B1121;
            border-right: 1px solid #1E293B;
        }

        /* Cards dentro da Sidebar */
        .sidebar-card {
            background-color: rgba(30, 41, 59, 0.4);
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .sidebar-title {
            color: #8B5CF6;
            font-size: 1rem;
            font-weight: bold;
            margin-bottom: 10px;
            border-bottom: 1px solid #334155;
            padding-bottom: 5px;
        }

        /* Status Ergonômico */
        .status-ok { color: #10B981; font-weight: bold; font-size: 0.9rem; }
        .status-warn { color: #F59E0B; font-weight: bold; font-size: 0.9rem; }
        .status-danger { color: #EF4444; font-weight: bold; font-size: 0.9rem; }


        /* ==========================================
           DESTAQUE DOS CAMPOS DE PREENCHIMENTO (INPUTS)
           ========================================== */
        
        .stTextInput div[data-baseweb="input"] {
            background-color: rgba(51, 65, 85, 0.8) !important; /* Cinza azulado mais claro */
            border: 1px solid #64748B !important; /* Borda visível */
            border-radius: 8px !important;
        }
        
        /* Cor do texto digitado */
        .stTextInput input {
            color: #FFFFFF !important; 
        }
        
        /* Efeito de brilho (neon) quando o usuário clica para digitar */
        .stTextInput div[data-baseweb="input"]:focus-within {
            border-color: #8B5CF6 !important;
            box-shadow: 0 0 8px rgba(139, 92, 246, 0.5) !important;
        }        

        </style>
    """, unsafe_allow_html=True)

aplicar_estilo_customizado()

# ==========================================
# CONSTANTES E FUNÇÕES CORE
# ==========================================
MODELOS_GROQ = {
    "Llama 3.3 70B (Recomendado)": "llama-3.3-70b-versatile",
    "Llama 3.1 8B (Rápido)": "llama-3.1-8b-instant",
    "Gemma 2 9B": "gemma2-9b-it",
    "Mixtral 8x7B": "mixtral-8x7b-32768"
}
MODELO_PADRAO = "llama-3.3-70b-versatile"

def extrair_texto_pdf(arquivo_pdf):
    try:
        leitor = PyPDF2.PdfReader(arquivo_pdf)
        if not leitor.pages: return None
        return "".join([pagina.extract_text() or "" for pagina in leitor.pages]).strip() or None
    except:
        return None

def higienizar_texto(texto):
    if not texto: return ""
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL OMITIDO - LGPD]', texto)
    return texto.strip()

def validar_e_listar_modelos(api_key):
    try:
        res = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
        return (True, [m['id'] for m in res.json().get('data', [])]) if res.status_code == 200 else (False, [])
    except:
        return False, []

def mostrar_pdf_na_tela(arquivo_pdf):
    base64_pdf = base64.b64encode(arquivo_pdf.getvalue()).decode('utf-8')
    st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" style="border-radius: 10px; border: 1px solid #334155;"></iframe>', unsafe_allow_html=True)

def analisar_curriculo_ia(texto, api_key, modo, requisitos, modelo_selecionado):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    if modo == "Recrutamento (Match de Vaga)":
        prompt = f"Analise este currículo para a vaga: {requisitos}. CURRÍCULO: {texto[:3000]}. Dê nota 0-10 baseada na compatibilidade técnica. Gere resumo com 3 tópicos. Responda em JSON: {{\"nota\": 8.5, \"resumo\": [\"tópico 1\", \"tópico 2\", \"tópico 3\"]}}"
    else:
        prompt = f"Atue como Orientador analisando: {texto[:3000]}. Avalie clareza, gramática e estrutura (ignore vaga). Dê nota 0-10. Liste 3 melhorias. Responda em JSON: {{\"nota\": 7.0, \"resumo\": [\"melhoria 1\", \"melhoria 2\", \"melhoria 3\"]}}"
    
    modelos = [modelo_selecionado] + [m for m in MODELOS_GROQ.values() if m != modelo_selecionado]
    for modelo in modelos:
        try:
            res = requests.post(url, json={"model": modelo, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}, headers=headers, timeout=30)
            if res.status_code == 200:
                conteudo = res.json()['choices'][0]['message']['content'].strip()
                conteudo = re.sub(r'^```json\n|```$', '', conteudo, flags=re.MULTILINE).strip()
                dados = json.loads(conteudo)
                dados['nota'] = float(dados['nota'])
                return dados
        except:
            continue
    return None

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
def main():
    if 'inicio_sessao' not in st.session_state: st.session_state.inicio_sessao = datetime.now()
    minutos_ativos = int((datetime.now() - st.session_state.inicio_sessao).total_seconds() // 60)
    
    # --- SIDEBAR OTIMIZADA ---
    with st.sidebar:
        st.markdown("## ⚙️ Painel de Controle")
        st.write("") 
        
        # 1. CARD DE AUTENTICAÇÃO (Container Nativo)
        with st.container(border=True):
            st.markdown("#### 🔐 Autenticação (API)")
            
            api_key_input = st.text_input("Chave Groq Cloud", type="password", help="Sua chave de acesso seguro à IA.")
            st.markdown("<div style='margin-top: -10px; margin-bottom: 15px; font-size: 0.8rem;'><a href='https://console.groq.com/keys' target='_blank'>🔗 Obter API Key Gratuita</a></div>", unsafe_allow_html=True)
            
            if api_key_input and st.button("Validar Conexão", use_container_width=True):
                valida, _ = validar_e_listar_modelos(api_key_input)
                if valida:
                    st.session_state.api_key = api_key_input
                    st.session_state.api_key_validada = True
                else:
                    st.error("Chave inválida!")
                    
            if st.session_state.get('api_key_validada', False):
                st.success("✅ Conectado!")
                modelo_escolhido = st.selectbox("🤖 Modelo de IA", options=list(MODELOS_GROQ.keys()), index=0)
                st.session_state.modelo_selecionado = MODELOS_GROQ[modelo_escolhido]

        # 2. CARD DO MONITOR ERGONÔMICO (Container Nativo)
        with st.container(border=True):
            st.markdown("#### ⏳ Monitor Ergonômico")
            st.metric(label="Tempo Contínuo", value=f"{minutos_ativos} min")
            
            if minutos_ativos < 45:
                st.markdown("<span style='color: #10B981; font-weight: bold;'>🟢 Status: Saudável</span>", unsafe_allow_html=True)
                st.caption("Postura e tempo de tela adequados.")
            elif minutos_ativos >= 45 and minutos_ativos < 50:
                st.markdown("<span style='color: #F59E0B; font-weight: bold;'>🟡 Status: Atenção</span>", unsafe_allow_html=True)
                st.warning("Prepare-se para fazer uma pausa em breve.")
            else:
                st.markdown("<span style='color: #EF4444; font-weight: bold;'>🔴 Status: Alerta!</span>", unsafe_allow_html=True)
                st.error("Limite excedido! Faça uma pausa de 10 min, alongue-se e beba água.")
                if st.button("✅ Registrei minha pausa", use_container_width=True):
                    st.session_state.inicio_sessao = datetime.now()
                    st.rerun()

    # --- ÁREA PRINCIPAL EM COLUNAS ---
    # Proporção de 2 para o texto/formulário e 1 para a imagem (dá mais respiro ao app)
    col_esq, col_dir = st.columns([2, 1], gap="large")

    with col_esq:
        st.markdown('<h1 class="titulo-gradiente">AMEOAM</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitulo">RPA e IA Especializada em Triagem e Orientação de Currículos</p>', unsafe_allow_html=True)
        
        modo_operacao = st.radio("Objetivo da análise:", ["Recrutamento (Match de Vaga)", "Orientação (Estrutura e Gramática)"], horizontal=True)
        
        requisitos = ""
        if modo_operacao == "Recrutamento (Match de Vaga)":
            requisitos = st.text_area("Requisitos da Vaga", placeholder="Ex: Python, React, SQL...", height=100)
        else:
            st.info("💡 Foco na qualidade do documento: clareza, gramática e estrutura.")

        arquivos_upados = st.file_uploader("Currículos (PDF)", type=['pdf'], accept_multiple_files=True)
        
        st.write("") 
        botao_analisar = st.button("🚀 INICIAR ANÁLISE", type="primary", use_container_width=True)

    with col_dir:
        st.write("")
        st.write("")
        st.write("")
        
        st.markdown('<div class="imagem-lateral">', unsafe_allow_html=True)
        # O seu vídeo continua aqui normalmente
        st.video("meu_video.mp4", autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("") # Um pequeno espaço entre o vídeo e os cards
        
        # --- PRIMEIRA LINHA DE CARDS ---
        col_card1, col_card2 = st.columns(2)
        
        # --- PRIMEIRA LINHA DE CARDS ---
        col_card1, col_card2 = st.columns(2)
        
        with col_card1:
            st.markdown("""
                <div class="card-acao">
                    <a href="https://youtu.be/2wPQVni6A6s" target="_blank">
                        <div class="card-icone">📺</div>
                        Tutorial no YouTube
                    </a>
                </div>
            """, unsafe_allow_html=True)
            
        with col_card2:
            st.markdown("""
                <div class="card-acao">
                    <a href="https://forms.gle/yXDhJu74r2Cq4zbi9" target="_blank">
                        <div class="card-icone">⭐</div>
                        Avalie a Plataforma
                    </a>
                </div>
            """, unsafe_allow_html=True)

        # APAGUE O st.write("") QUE ESTAVA AQUI NO MEIO!

        # --- SEGUNDA LINHA DE CARDS ---
        col_card3, col_card4 = st.columns(2)
        
        with col_card3:
            st.markdown("""
                <div class="card-acao">
                    <a href="https://wa.me/message/FRVFVIUBESLVD1" target="_blank">
                        <div class="card-icone">💬</div>
                        Suporte Técnico
                    </a>
                </div>
            """, unsafe_allow_html=True)
            
        with col_card4:
            st.markdown("""
                <div class="card-acao">
                    <a href="https://youtu.be/7c5yfAdmIEQ?si=Rg73Pock1NGQ_b1i" target="_blank">
                        <div class="card-icone">💡</div>
                        Dicas de Carreira
                    </a>
                </div>
            """, unsafe_allow_html=True)

    # --- PROCESSAMENTO ---
    if botao_analisar:
        if not st.session_state.get('api_key_validada', False): return st.error("❌ Valide sua API key na barra lateral.")
        if modo_operacao == "Recrutamento (Match de Vaga)" and not requisitos.strip(): return st.error("❌ Insira os requisitos da vaga.")
        if not arquivos_upados: return st.error("❌ Faça o upload de um currículo.")
            
        st.markdown("---")
        resultados = []
        barra_progresso = st.progress(0)
        
        for idx, arquivo in enumerate(arquivos_upados):
            texto = extrair_texto_pdf(arquivo)
            if texto:
                res_ia = analisar_curriculo_ia(higienizar_texto(texto), st.session_state.api_key, modo_operacao, requisitos, st.session_state.get('modelo_selecionado', MODELO_PADRAO))
                if res_ia:
                    resultados.append({"Arquivo": arquivo.name, "Nota": res_ia.get("nota", 0), "Resumo": "\n".join([f"• {t}" for t in res_ia.get("resumo", [""])]), "Obj": arquivo})
            barra_progresso.progress((idx + 1) / len(arquivos_upados))
        
        if resultados:
            df = pd.DataFrame(resultados).sort_values(by="Nota", ascending=False).reset_index(drop=True)
            st.markdown("## 📊 Dashboard de Resultados")
            
            fig = px.bar(df, x="Arquivo", y="Nota", color="Nota", color_continuous_scale="Viridis", text_auto='.1f')
            fig.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            for index, row in df.iterrows():
                with st.expander(f"📍 {index + 1}º Lugar - {row['Arquivo']} - Nota: {row['Nota']:.1f}"):
                    c1, c2 = st.columns(2)
                    with c1: st.markdown(f"#### Parecer da IA:\n{row['Resumo']}")
                    with c2: mostrar_pdf_na_tela(row['Obj'])

    # --- FOOTER ---
    ano_atual = datetime.now().year
    st.markdown(f"""
        <div class="footer">
            Desenvolvido por alunos do Centro Universitário ESBAM | &copy; {ano_atual} <br>
            <span style="font-size: 0.75rem;"> Automação para Mitigação de Estress Ocupacional no Amazonas <strong>AMEOAM</strong></span>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
