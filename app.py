import io
import streamlit as st
from gtts import gTTS

# --- Configuración de página ---
st.set_page_config(page_title="Sistema de Llamado de Pacientes", page_icon="🏥", layout="centered")

# --- Inicialización del Estado de la Sesión ---
if "patient_queue" not in st.session_state:
    st.session_state.patient_queue = []
if "voice_call_count" not in st.session_state:
    st.session_state.voice_call_count = 0
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "last_action_msg" not in st.session_state:
    st.session_state.last_action_msg = ""

# --- Función para generar audio TTS ---
def generate_patient_voice(name, office_num, voice_type="female"):
    text = f"Paciente {name}, por favor acérquese al consultorio número {office_num}."
    tld = 'com.mx' if voice_type == "male" else 'es'
    tts = gTTS(text, lang='es', tld=tld)
    
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

# --- Interfaz de Usuario ---
st.title("🏥 Sistema de Llamado de Pacientes")

# Panel lateral de configuración / carga
with st.sidebar:
    st.header("⚙️ Configuración")
    office_number = st.text_input("Consultorio Nº:", value="2")
    patient_list_raw = st.text_area(
        "Lista de Pacientes:",
        placeholder="Maria Garcia\nJuan Perez\nAna Lopez",
        height=200
    )
    
    if st.button("📥 Cargar Pacientes e Iniciar", type="primary"):
        names = [line.strip() for line in patient_list_raw.split('\n') if line.strip()]
        if names:
            st.session_state.patient_queue = names
            st.session_state.voice_call_count = 0
            st.session_state.audio_bytes = None
            st.session_state.last_action_msg = f"✅ Lista cargada ({len(names)} pacientes)."
        else:
            st.session_state.patient_queue = []
            st.session_state.last_action_msg = "⚠️ Por favor, ingresa al menos un paciente."

# Panel Principal
if st.session_state.last_action_msg:
    st.info(st.session_state.last_action_msg)

if st.session_state.patient_queue:
    current_patient = st.session_state.patient_queue[0]
    
    st.markdown("### 👤 Paciente en Turno")
    st.markdown(f"## **{current_patient}**")
    st.caption(f"Quedan **{len(st.session_state.patient_queue)}** paciente(s) en la fila.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📢 Llamar Paciente Actual", use_container_width=True):
            voice_type = "female" if st.session_state.voice_call_count % 2 == 0 else "male"
            st.session_state.audio_bytes = generate_patient_voice(current_patient, office_number, voice_type)
            st.session_state.voice_call_count += 1
            st.session_state.last_action_msg = f"Llamando a {current_patient} ({voice_type}, consultorio {office_number})"

    with col2:
        if st.button("➡️ Siguiente Paciente en Fila", type="secondary", use_container_width=True):
            completed_patient = st.session_state.patient_queue.pop(0)
            st.session_state.voice_call_count = 0
            st.session_state.audio_bytes = None
            
            if st.session_state.patient_queue:
                st.session_state.last_action_msg = f"Atendido: {completed_patient}. Siguiente: {st.session_state.patient_queue[0]}"
            else:
                st.session_state.last_action_msg = "🎉 Todos los pacientes han sido llamados."
            st.rerun()

    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format="audio/mp3", autoplay=True)

else:
    st.warning("No hay pacientes en la cola. Carga una lista desde el panel lateral para iniciar.")
