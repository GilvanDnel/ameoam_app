import streamlit as st
import PyPDF2
import requests
import re
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_pdf_viewer import pdf_viewer

# ==========================================
# CONFIGURAÇÃO DE DESIGN SISTÊMICO (UI/UX)
# ==========================================
st.set_page_config(
    page_title="AMEOAM | Triagem Inteligente",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

def aplicar_identidade_visual():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
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

        .nav-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1.2rem;
            text-align: center;
            transition: all 0.2s ease-in-out;
            text-decoration: none !important;
            display: flex;
            flex-direction: column;
            gap: 8px;
            height: 110px;
            justify-content: center;
        }
        .nav-card:hover {
            border-color: #8B5CF6;
            background: rgba(51, 65, 85, 0.5);
            transform: translateY(-2px);
        }
        .nav-card span { font-size: 1.5rem; }
        .nav-card label { color: #F1F5F9; font-weight: 600; cursor: pointer; font-size: 0.85rem; }

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

        .media-container video, .media-container img {
            border-radius: 20px;
            border: 1px solid #1E293B;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
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

        @media (max-width: 800px) {
            .media-container { display: none !important; }
            .block-container { padding-bottom: 15rem; }
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# FUNÇÕES DE PROCESSAMENTO (REFATORADAS)
# ==========================================
def extrair_texto_pdf(arquivo_pdf):
    try:
        leitor = PyPDF2.PdfReader(arquivo_pdf)
        return "".join([p.extract_text() or "" for p in leitor.pages]).strip()
    except: return None

def analisar_curriculo_ia(texto, api_key, modo, requisitos, modelo):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # PROMPT DE ALTA PRECISÃO (Sem exemplos numéricos para evitar vício)
    if modo == "Recrutamento (Match)":
        prompt = (
            f"Você é um Headhunter Técnico de elite. Sua tarefa é dar uma nota de 0 a 10 ao currículo abaixo "
            f"baseado estritamente nos requisitos: {requisitos}. \n\n"
            f"CURRÍCULO: {texto[:4000]}\n\n"
            "INSTRUÇÕES CRÍTICAS:\n"
            "1. Analise cada tecnologia/habilidade pedida.\n"
            "2. Se o candidato não menciona uma tecnologia pedida, a nota DEVE cair drasticamente.\n"
            "3. Se o currículo for genérico ou sem experiência na área, a nota DEVE ser abaixo de 4.\n"
            "4. Não use notas padrão (como 8.0 ou 8.5) a menos que o currículo seja realmente excepcional.\n"
            "5. Calcule a nota com uma casa decimal (ex: 3.2, 5.7, 9.1).\n\n"
            "Responda EXCLUSIVAMENTE em JSON: {\"nota\": <valor_numérico>, \"resumo\": [\"Ponto Crítico 1\", \"Ponto Crítico 2\", \"Ponto Crítico 3\"]}"
        )
    else:
        prompt = (
            f"Analise a estrutura e gramática deste currículo para fins de orientação.\n\n"
            f"TEXTO: {texto[:4000]}\n\n"
            "Atribua nota de 0 a 10 baseada na qualidade da redação e organização. "
            "Responda em JSON: {\"nota\": <valor_numérico>, \"resumo\": [\"Dica 1\", \"Dica 2\", \"Dica 3\"]}"
        )
    
    try:
        res = requests.post(url, json={
            "model": modelo, 
            "messages": [{"role": "user", "content": prompt}], 
            "temperature": 0.0, # Temperatura 0 para ser determinístico e analítico
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
        st.markdown("### ⚙️ Painel")
        with st.container(border=True):
            api_key = st.text_input("Groq Cloud Key", type="password")
            if api_key: st.session_state.key = api_key
            
            modelo = st.selectbox("Modelo", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
            st.session_state.mod = modelo

        st.markdown("### 🧘 Ergonomia")
        with st.container(border=True):
            st.metric("Sessão Ativa", f"{minutos} min")
            if minutos < 45: st.success("🟢 Status: Saudável")
            else: st.error("🔴 Faça uma pausa!")

    col_main, col_widgets = st.columns([2, 1], gap="large")

    with col_main:
        st.markdown('<h1 class="brand-title">AMEOAM</h1>', unsafe_allow_html=True)
        st.markdown('<p class="brand-subtitle">Análise Técnica e Rankeamento com Inteligência Artificial</p>', unsafe_allow_html=True)
        
        with st.container(border=True):
            modo = st.radio("Objetivo:", ["Recrutamento (Match)", "Orientação Técnico-Gramatical"], horizontal=True)
            vaga = st.text_area("Requisitos da Vaga (Seja específico)", placeholder="Ex: Mínimo 2 anos de Python, experiência com RPA e SQL...", height=100)
            arquivos = st.file_uploader("Currículos (PDF)", type=['pdf'], accept_multiple_files=True)
            
            st.write("")
            btn = st.button("✨ INICIAR TRIAGEM TÉCNICA", use_container_width=True)

    with col_widgets:
        st.write("")
        st.markdown('<div class="media-container">', unsafe_allow_html=True)
        st.video("meu_video.mp4", autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<a href="https://youtu.be/2wPQVni6A6s" target="_blank" class="nav-card"><span>📺</span><label>Tutorial</label></a>', unsafe_allow_html=True)
            st.markdown('<a href="https://wa.me/message/FRVFVIUBESLVD1" target="_blank" class="nav-card"><span>💬</span><label>Suporte</label></a>', unsafe_allow_html=True)
        with c2:
            st.markdown('<a href="https://forms.gle/yXDhJu74r2Cq4zbi9" target="_blank" class="nav-card"><span>⭐</span><label>Avaliar</label></a>', unsafe_allow_html=True)
            st.markdown('<a href="https://youtu.be/7c5yfAdmIEQ" target="_blank" class="nav-card"><span>💡</span><label>Dicas</label></a>', unsafe_allow_html=True)

    if btn:
        if not st.session_state.get('key'): st.error("Insira sua chave API na barra lateral.")
        elif not arquivos: st.warning("Suba os ficheiros primeiro.")
        else:
            progresso = st.progress(0)
            resultados = []
            
            for i, arq in enumerate(arquivos):
                with st.status(f"Escaneando: {arq.name}..."):
                    texto = extrair_texto_pdf(arq)
                    if texto:
                        analise = analisar_curriculo_ia(texto, st.session_state.key, modo, vaga, st.session_state.mod)
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
                fig.update_layout(yaxis_range=[0,10]) # Fixar escala para ver a diferença real
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 🏆 Tabela de Classificação")
                st.dataframe(df[["Candidato", "Nota"]], use_container_width=True)

                st.markdown("### 🔍 Análise Detalhada")
                for index, row in df.iterrows():
                    with st.expander(f"📍 {index + 1}º Lugar - {row['Candidato']} (Nota: {row['Nota']:.1f})"):
                        ca, cb = st.columns([1, 1.5])
                        with ca:
                            st.markdown("#### Veredito da IA")
                            for item in row['Resumo']: st.write(f"• {item}")
                            st.download_button(f"📥 Baixar PDF", row['Arquivo_Obj'].getvalue(), file_name=row['Candidato'], key=f"dl_{index}")
                        with cb:
                            pdf_viewer(input=row['Arquivo_Obj'].getvalue(), height=500)
            else:
                st.error("A IA não conseguiu processar os currículos. Tente novamente.")

    st.markdown(f"""
        <div class="footer-fixed">
            Desenvolvido por alunos ESBAM | &copy; {datetime.now().year} <br>
            <strong>AMEOAM:</strong> Automação e Mitigação de Estresse Ocupacional no Amazonas
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
