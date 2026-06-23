import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import tempfile
import os
from groq import Groq
from dotenv import load_dotenv

# =====================================================
# LOAD ENV
# =====================================================

load_dotenv()

client = Groq(
    api_key=os.getenv("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")
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Industrial maintanence knowledge Bot",
    page_icon="🤖",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #0f172a;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

.stChatMessage {
    border-radius: 15px;
    padding: 12px;
    margin-bottom: 10px;
    border: 1px solid #1e293b;
}

h1, h2, h3, h4, h5, h6, p, span, label {
    color: white !important;
}

.stButton button {
    width: 100%;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE
# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =====================================================
# LANGUAGE MAP
# =====================================================

LANGUAGE_CODES = {
    "English": "en-IN",
    "Tamil": "ta-IN",
    "Hindi": "hi-IN",
    "Telugu": "te-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN"
}

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("⚙️ Settings")

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    domain = st.selectbox(
        "📚 Assistant Mode",
        [
            "General AI Assistant",
            "Industrial Maintenance",
            "Mechanical Engineering",
            "Electrical Maintenance",
            "Predictive Maintenance",
            "Preventive Maintenance",
            "Automation",
            "PLC Programming",
            "Industrial AI",
            "Programming",
            "Education",
            "Science",
            "Technology",
            "Business"
        ]
    )

    language = st.selectbox(
        "🌐 Language",
        list(LANGUAGE_CODES.keys())
    )

    model_name = st.selectbox(
    "🤖 AI Model",
    [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "gemma2-9b-it"
    ]
)

    st.markdown("---")

    st.info("""
Recommended Models:

✅ llama3-8b-8192 → Fast + best overall

✅ gemma2-9b-it → Lightweight + smart

✅ mixtral-8x7b-32768 → Advanced reasoning
""")

# =====================================================
# HEADER
# =====================================================

st.title("🤖 AI Knowledge Assistant")

st.caption(
    f"Mode: {domain} | Language: {language} | Model: {model_name}"
)

# =====================================================
# SYSTEM PROMPT
# =====================================================

def system_prompt():

    return f"""
You are a powerful multilingual AI assistant.

Rules:
- ALWAYS answer in {language}
- Be professional and accurate
- Answer ALL types of questions
- Give detailed explanations
- Maintain conversation context
- If topic relates to {domain}, provide expert-level answers
- Explain clearly and naturally
- Be friendly and helpful
"""

# =====================================================
# BUILD PROMPT
# =====================================================

def build_prompt(user_question):

    history = ""

    for msg in st.session_state.messages[-10:]:

        role = msg["role"]

        if role == "user":
            history += f"User: {msg['content']}\n"
        else:
            history += f"Assistant: {msg['content']}\n"

    final_prompt = f"""
{system_prompt()}

Conversation History:
{history}

User:
{user_question}

Assistant:
"""

    return final_prompt

# =====================================================
# ASK AI
# =====================================================

def ask_llm(question):

    try:

        prompt = build_prompt(question)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=700
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"❌ Error:\n\n{str(e)}"

# =====================================================
# DISPLAY CHAT HISTORY
# =====================================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =====================================================
# VOICE INPUT
# =====================================================

st.markdown("## 🎤 Voice Assistant")

audio_bytes = audio_recorder(
    text="🎙️ Click to Record",
    recording_color="#ff0000",
    neutral_color="#10b981",
    icon_name="microphone",
    icon_size="2x"
)

if audio_bytes:

    st.audio(audio_bytes, format="audio/wav")

    if st.button("🧠 Analyze Voice"):

        try:

            recognizer = sr.Recognizer()

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".wav"
            ) as tmp:

                tmp.write(audio_bytes)
                temp_audio_path = tmp.name

            with sr.AudioFile(temp_audio_path) as source:

                audio_data = recognizer.record(source)

            spoken_text = recognizer.recognize_google(
                audio_data,
                language=LANGUAGE_CODES[language]
            )

            os.remove(temp_audio_path)

            st.success(f"🎤 You said: {spoken_text}")

            st.session_state.messages.append({
                "role": "user",
                "content": spoken_text
            })

            with st.chat_message("user"):
                st.markdown(spoken_text)

            with st.spinner("🤖 Thinking..."):

                response = ask_llm(spoken_text)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            with st.chat_message("assistant"):
                st.markdown(response)

        except sr.UnknownValueError:

            st.error("❌ Could not understand audio.")

        except sr.RequestError:

            st.error("❌ Speech Recognition service unavailable.")

        except Exception as e:

            st.error(f"❌ Voice Error:\n\n{str(e)}")

# =====================================================
# TEXT INPUT
# =====================================================

user_input = st.chat_input("Ask anything...")

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("🤖 Thinking..."):

        response = ask_llm(user_input)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.markdown(response)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption("🚀 Powered by Streamlit + Groq + Speech Recognition")