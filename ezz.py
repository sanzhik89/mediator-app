import streamlit as st
from openai import OpenAI
import json
import os



api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key 
)

if "history" not in st.session_state:
    st.session_state.history = []
if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None
if "current_msg" not in st.session_state:
    st.session_state.current_msg = ""

def reset_chat():
    st.session_state.current_analysis = None
    st.session_state.current_msg = ""
    st.session_state.user_input = ""

st.set_page_config(page_title="Conflict Mediator Pro", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    .result-card { background: white; padding: 20px; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 10px; min-height: 110px; }
    .result-label { font-size: 0.75rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
    .progress-bg { background: #f1f5f9; border-radius: 10px; height: 10px; width: 100%; margin: 10px 0; overflow: hidden; }
    .progress-fill { background: #5fb3a1; height: 100%; border-radius: 10px; transition: width 0.8s; }
    .stButton>button { background-color: #5fb3a1 !important; color: white !important; border-radius: 12px !important; border: none !important; font-weight: 600 !important; }
    .sidebar-box { background-color: #eff6ff; padding: 15px; border-radius: 12px; border: 1px solid #dbeafe; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("Mediator AI")
    st.button("➕ Новый чат", on_click=reset_chat, use_container_width=True)
    
    st.divider()
    st.markdown("### 🌐 Внешние каналы")
    st.markdown(f"""
        <div class='sidebar-box'>
            <p style='color: #1e40af; font-size: 0.9rem; margin:0;'>
                Telegram Bot:<br>
                <a href="https://t.me/mediator_ai_bot" target="_blank" style="text-decoration: none; color: #5fb3a1; font-weight: bold;">
                    @mediator_ai_bot
                </a>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 👥 Коллективный разум")
    if st.button("📥 Отправить кейс анонимно", use_container_width=True):
        st.toast("✅ Кейс отправлен")
    
    st.divider()
    st.subheader("📜 История")
    for i, item in enumerate(reversed(st.session_state.history[-10:])):
        if st.button(f"🗨️ {item['title']}", key=f"h_{i}", use_container_width=True):
            st.session_state.current_analysis = item['data']
            st.session_state.current_msg = item['original_text']

st.markdown("<h1 style='text-align: center;'>Превратите конфликт в понимание</h1>", unsafe_allow_html=True)

with st.container():
    u_input = st.text_area("", placeholder="Введите сообщение...", key="user_input", height=130, label_visibility="collapsed")
    _, btn_col = st.columns([4, 1.2])
    with btn_col:
        analyze_btn = st.button("✨ Разобрать", use_container_width=True)

if analyze_btn and u_input:
    try:
        with st.spinner('Анализ...'):
            prompt = f"""
            Ты — эксперт-медиатор. Разбери сообщение: '{u_input}'. 
            Верни JSON на русском. 
            
            SCORE:
            - 1-2: Приветствия, комплименты, вежливость.
            - 3-5: Холодность, претензии.
            - 6-8: Сарказм, обвинения.
            - 9-10: Оскорбления, мат.

            JSON:
            {{
              "patterns": "паттерны",
              "emotion": "эмоция",
              "need": "потребность",
              "score": число,
              "gradus": "Низкий/Средний/Высокий",
              "prognosis": "прогноз",
              "answers": [
                {{"type": "Эмпатичный (Сгладить)", "text": "ответ"}},
                {{"type": "Рациональный (Решить)", "text": "ответ"}},
                {{"type": "Сократовский (Уточнить)", "text": "ответ"}}
              ]
            }}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            data = json.loads(response.choices[0].message.content)
            st.session_state.current_analysis = data
            st.session_state.current_msg = u_input
            st.session_state.history.append({"title": u_input[:20]+"...", "original_text": u_input, "data": data})
            st.rerun()
    except Exception as e:
        st.error(f"Ошибка: {e}")

if st.session_state.current_analysis:
    res = st.session_state.current_analysis
    score = int(res.get("score", 0))
    gradus = res.get("gradus", "Нейтральный")

    _, center, _ = st.columns([1, 8, 1])
    with center:
        c1, c2 = st.columns(2)
        with c1: st.markdown(f"<div class='result-card'><span class='result-label'>💬 СКАЗАНО</span>{st.session_state.current_msg}</div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='result-card'><span class='result-label'>✨ ПАТТЕРНЫ</span>{res.get('patterns')}</div>", unsafe_allow_html=True)
        
        c3, c4 = st.columns(2)
        with c3: st.markdown(f"<div class='result-card'><span class='result-label'>❤️ ЭМОЦИЯ</span>{res.get('emotion')}</div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div class='result-card'><span class='result-label'>🎯 ПОТРЕБНОСТЬ</span>{res.get('need')}</div>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class='result-card'>
                <span class='result-label'>⚠️ ЭСКАЛАЦИЯ <span style='margin-left:auto'>{score}/10 / {gradus}</span></span>
                <div class='progress-bg'><div class='progress-fill' style='width: {score*10}%;'></div></div>
                <small><b>Прогноз:</b> {res.get('prognosis')}</small>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### Варианты трансформации")
        for ans in res.get('answers', []):
            with st.expander(f"💡 {ans.get('type')}"):
                st.write(ans.get('text'))