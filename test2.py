import streamlit as st
import PyPDF2
import requests
import re
import json
import pandas as pd
import plotly.express as px
import base64
from datetime import datetime
from streamlit_pdf_viewer import pdf_viewer

# ==========================================
# CONFIGURAÇÃO DE DESIGN SISTÊMICO (UI/UX)
# ==========================================
st.set_page_config(
    page_title="AMEOAM",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

def aplicar_identidade_visual():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background-color: #0F172A;
            color: #F8FAFC;
        }

        .brand-title {
            background: linear-gradient(135deg, #8B5CF6 0%, #06B6D4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3.2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            letter-spacing: -1.5px;
        }
        
        .brand-subtitle {
            color: #94A3B8;
            font-size: 1.1rem;
            font-weight: 400;
            margin-bottom: 2rem;
        }

        .sidebar-nav-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 10px 14px;
            text-align: left;
            transition: all 0.2s ease-in-out;
            text-decoration: none !important;
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
            width: 100%;
        }
        .sidebar-nav-card:hover {
            border-color: #8B5CF6;
            background: rgba(51, 65, 85, 0.6);
            transform: translateX(4px);
        }
        .sidebar-nav-card:hover .fa-youtube { color: #FF0000; }
        .sidebar-nav-card:hover .fa-whatsapp { color: #25D366; }
        
        .sidebar-nav-card span { 
            font-size: 1.1rem; 
            display: flex;
            align-items: center;
            justify-content: center;
            width: 24px;
        }
        .sidebar-nav-card label { 
            color: #F1F5F9; 
            font-weight: 500; 
            cursor: pointer; 
            font-size: 0.8rem; 
            margin: 0;
            line-height: 1;
        }

        .sidebar-video-box {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #1E293B;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            line-height: 0;
        }

        div.stButton > button {
            background: #8B5CF6 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 2rem !important;
            font-weight: 700 !important;
            transition: all 0.2s !important;
        }
        div.stButton > button:hover {
            background: #7C3AED !important;
            box-shadow: 0 0 15px rgba(139, 92, 246, 0.4) !important;
        }

        .footer-fixed {
            position: fixed;
            bottom: 0; left: 0; width: 100%;
            background: rgba(15, 23, 42, 0.9);
            backdrop-filter: blur(8px);
            padding: 15px;
            text-align: center;
            border-top: 1px solid #1E293B;
            color: #64748B;
            font-size: 0.75rem;
            z-index: 99;
        }

        section[data-testid="stSidebar"] .stMarkdown h3 {
            margin-bottom: 0.5rem;
        }

        @media (max-width: 800px) {
            .block-container { padding-bottom: 15rem; }
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# FUNÇÕES DE PROCESSAMENTO E UTILITÁRIOS
# ==========================================
def renderizar_video_como_gif(caminho_video):
    try:
        with open(caminho_video, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            video_html = f"""
                <div class="sidebar-video-box">
                    <video width="100%" autoplay loop muted playsinline>
                        <source src="data:video/mp4;base64,{b64}" type="video/mp4">
                    </video>
                </div>
            """
            return video_html
    except:
        return "⚠️ Vídeo não encontrado"

def extrair_texto_pdf(arquivo_pdf):
    try:
        leitor = PyPDF2.PdfReader(arquivo_pdf)
        return "".join([p.extract_text() or "" for p in leitor.pages]).strip()
    except: return None

def analisar_curriculo_ia(texto, api_key, modo, requisitos, modelo):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    if modo == "Recrutamento (Match)":
        prompt = (
            f"Você é um Headhunter Técnico de elite. Sua tarefa é dar uma nota de 0 a 10 ao currículo abaixo "
            f"baseado estritamente nos requisitos: {requisitos}. \n\n"
            f"CURRÍCULO: {texto[:4000]}\n\n"
            "INSTRUÇÕES CRÍTICAS:\n"
            "1. Analise cada tecnologia/habilidade pedida.\n"
            "2. Se o candidato não menciona uma tecnologia pedida, a nota DEVE cair drasticamente.\n"
            "3. Se o currículo for genérico ou sem experiência na área, a nota DEVE ser abaixo de 4.\n"
            "4. Não use notas padrão (como 8.5) a menos que o currículo seja realmente excepcional.\n"
            "5. Calcule a nota com uma casa decimal.\n\n"
            "Responda EXCLUSIVAMENTE em JSON: {\"nota\": <valor>, \"resumo\": [\"Ponto 1\", \"Ponto 2\", \"Ponto 3\"]}"
        )
    else:
        # PROMPT DE ORIENTAÇÃO PROFISSIONAL (ALTO RIGOR)
        prompt = (
            "Você é um Arquiteto de Carreiras Sênior e Especialista em ATS (Applicant Tracking Systems). "
            "Sua missão é avaliar a ESTRUTURA PROFISSIONAL e a eficácia de comunicação do currículo abaixo.\n\n"
            f"TEXTO DO CURRÍCULO: {texto[:4000]}\n\n"
            "CRITÉRIOS DE AVALIAÇÃO (SEJA RIGOROSO):\n"
            "1. COMPATIBILIDADE ATS: Verifique se as seções estão bem definidas e se há palavras-chave técnicas relevantes.\n"
            "2. FOCO EM RESULTADOS: O candidato usou números ou KPIs? (Ex: 'Aumentei vendas em 20%' vs 'Trabalhei com vendas'). "
            "Se não houver dados quantitativos, penalize a nota drasticamente.\n"
            "3. VOCABULÁRIO TÉCNICO: Avalie o uso de verbos de ação e terminologia moderna da área de atuação.\n"
            "4. SÍNTESE EXECUTIVA: O resumo profissional é estratégico ou apenas uma lista de adjetivos clichês?\n\n"
            "NOTAS:\n"
            "9-10: Currículo de nível Executivo/Senior, impecável e focado em impacto.\n"
            "7-8: Bom currículo, mas precisa de ajustes em palavras-chave ou formatação.\n"
            "4-6: Currículo 'descritivo' demais, sem foco em resultados ou mal estruturado.\n"
            "0-3: Texto amador, erros graves de estrutura ou falta de informações básicas.\n\n"
            "Responda EXCLUSIVAMENTE em JSON: "
            "{\"nota\": <valor_decimal>, \"resumo\": [\"Feedback crítico 1\", \"Feedback crítico 2\", \"Feedback crítico 3\"]}"
        )
    
    try:
        res = requests.post(url, json={
            "model": modelo, 
            "messages": [{"role": "user", "content": prompt}], 
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }, headers=headers, timeout=45)
        
        if res.status_code == 200:
            conteudo = res.json()['choices'][0]['message']['content']
            match = re.search(r'\{.*\}', conteudo, re.DOTALL)
            if match:
                dados = json.loads(match.group())
                dados['nota'] = float(dados['nota'])
                return dados
    except Exception as e:
        print(f"Erro na IA: {e}")
        return None
    return None

# ==========================================
# INTERFACE DO USUÁRIO
# ==========================================
def main():
    aplicar_identidade_visual()
    
    if 'start' not in st.session_state: st.session_state.start = datetime.now()
    minutos = int((datetime.now() - st.session_state.start).total_seconds() // 60)

    # SIDEBAR
    with st.sidebar:
        st.markdown("### Painel de Controle")
        
        with st.container(border=True):

            video_html = renderizar_video_como_gif("meu_video.mp4")
            st.markdown(video_html, unsafe_allow_html=True)
            st.markdown("**🔐 Autenticação**")
            api_key_input = st.text_input("Groq Cloud Key", type="password", label_visibility="collapsed", placeholder="Digite sua API Key aqui")
            if api_key_input: 
                st.session_state.key = api_key_input
            
            modelo_input = st.selectbox("Modelo de IA", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
            st.session_state.mod = modelo_input


            st.markdown("**Informações**")
            st.markdown("""
               
                <a href="https://console.groq.com/keys" target="_blank" class="sidebar-nav-card">
                    <span><i class="fa-solid fa-key"></i></span>
                    <label>Adquir API KEY</label>
                </a>
                
                <a href="https://youtu.be/fvnLsbQLdy4" target="_blank" class="sidebar-nav-card">
                    <span><i class="fa-brands fa-youtube"></i></span>
                    <label>Tutorial YouTube</label>
                </a>
                <a href="https://forms.gle/yXDhJu74r2Cq4zbi9" target="_blank" class="sidebar-nav-card">
                    <span><i class="fa-solid fa-square-poll-vertical"></i></span>
                    <label>Avaliar Plataforma</label>
                </a>
                <a href="https://wa.me/message/FRVFVIUBESLVD1" target="_blank" class="sidebar-nav-card">
                    <span><i class="fa-brands fa-whatsapp"></i></span>
                    <label>Suporte Técnico</label>
                </a>
                <a href="https://youtu.be/7c5yfAdmIEQ" target="_blank" class="sidebar-nav-card">
                    <span><i class="fa-solid fa-lightbulb"></i></span>
                    <label>Dicas de Carreira</label>
                </a>
            """, unsafe_allow_html=True)

        st.write("")
        st.markdown("**🧘 Monitor Ergonômico**")
        with st.container(border=True):
            st.metric("Sessão Ativa", f"{minutos} min")
            if minutos < 45: st.success("🟢 Status: Saudável")
            else: st.error("🔴 Hora de uma pausa!")

    st.markdown('<h1 class="brand-title">AMEOAM</h1>', unsafe_allow_html=True)
    st.markdown('<p class="brand-subtitle">Análise Técnica e Orientação Estrutural de Currículos</p>', unsafe_allow_html=True)
    
    with st.container(border=True):
        modo = st.radio("Objetivo:", ["Recrutamento (Match)", "Orientação Técnico-Gramatical"], horizontal=True)
        vaga = ""
        if modo == "Recrutamento (Match)":
            vaga = st.text_area("Requisitos da Vaga", placeholder="Ex: Mínimo 2 anos de Python, experiência com RPA e SQL...", height=100)
        else:
            st.info("🎯 **Modo de Orientação:** A IA analisará a qualidade estrutural, impacto de resultados e compatibilidade com filtros ATS.")
        
        arquivos = st.file_uploader("Upload de Currículos (PDF)", type=['pdf'], accept_multiple_files=True)
        
        st.write("")
        btn = st.button("✨ INICIAR ANÁLISE PROFISSIONAL", use_container_width=True)

    if btn:
        # Ajuste aqui para usar a chave correta da sessão
        if not st.session_state.get('key'): 
            st.error("Insira sua chave API na barra lateral.")
        elif not arquivos: 
            st.warning("Suba os currículos primeiro.")
        else:
            progresso = st.progress(0)
            resultados = []
            
            for i, arq in enumerate(arquivos):
                with st.status(f"Analisando: {arq.name}..."):
                    texto = extrair_texto_pdf(arq)
                    if texto:
                        # Corrigindo os nomes das variáveis passadas para a função
                        analise = analisar_curriculo_ia(
                            texto, 
                            st.session_state.key, 
                            modo, 
                            vaga, 
                            st.session_state.mod
                        )
                        if analise:
                            resultados.append({
                                "Candidato": arq.name, 
                                "Nota": analise['nota'], 
                                "Resumo": analise['resumo'], 
                                "Arquivo_Obj": arq
                            })
                progresso.progress((i + 1) / len(arquivos))

            if resultados:
                df = pd.DataFrame(resultados).sort_values(by="Nota", ascending=False).reset_index(drop=True)
                
                st.markdown("---")
                st.markdown("## 📊 Ranking de Qualificação")
                
                fig = px.bar(
                    df, x="Candidato", y="Nota", color="Nota", 
                    template="plotly_dark", height=400,
                    labels={"Nota": "Score Técnico", "Candidato": "Candidatos"},
                    color_continuous_scale="Viridis",
                    text_auto='.1f'
                )
                fig.update_layout(yaxis_range=[0,10])
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 🏆 Tabela de Classificação")
                st.dataframe(df[["Candidato", "Nota"]], use_container_width=True)

                st.markdown("### 🔍 Feedback Especializado")
                for index, row in df.iterrows():
                    with st.expander(f"📍 {index + 1}º Lugar - {row['Candidato']} (Nota: {row['Nota']:.1f})"):
                        ca, cb = st.columns([1, 1.5])
                        with ca:
                            st.markdown("#### Veredito do Especialista")
                            for item in row['Resumo']: st.write(f"• {item}")
                            st.download_button(f"📥 Baixar PDF", row['Arquivo_Obj'].getvalue(), file_name=row['Candidato'], key=f"dl_{index}")
                        with cb:
                            pdf_viewer(input=row['Arquivo_Obj'].getvalue(), height=500)
            else:
                st.error("Erro no processamento. Verifique sua chave API.")

    st.markdown(f"""
        <div class="footer-fixed">
            Desenvolvido por alunos da UNIESBAM | &copy; {datetime.now().year} <br>
            <strong>AMEOAM:</strong> Automação e Mitigação de Estresse Ocupacional no Amazonas
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
