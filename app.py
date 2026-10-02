import io
import streamlit as st
from gtts import gTTS

# --- Configuración de la página ---
st.set_page_config(
    page_title="Sistema de Llamado de Pacientes", 
    page_icon="🏥", 
    layout="centered"
)

# --- Inicialización del Estado de la Sesión ---
if "patient_queue" not in st.session_state:
    st.session_state.patient_queue = []
if "patient_call_count" not in st.session_state:
    st.session_state.patient_call_count = 0
if "last_action_msg" not in st.session_state:
    st.session_state.last_action_msg = ""
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

# --- Función para generar audio en Español Colombiano/Latino ---
def generate_patient_voice(text):
    try:
        tts = gTTS(text=text, lang='es', tld='com.co')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        st.error(f"Error generando audio: {e}")
        return None

# --- Interfaz de Usuario ---
st.title("🏥 Sistema de Llamado")

# Panel lateral de configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    office_number = st.text_input("Consultorio Nº:", value="2")
    patient_list_raw = st.text_area(
        "Lista de Pacientes:",
        placeholder="Maria Garcia\nJuan Perez\nAna Lopez",
        height=200
    )
    
    if st.button("📥 Cargar Pacientes e Iniciar", type="primary", use_container_width=True):
        names = [line.strip() for line in patient_list_raw.split('\n') if line.strip()]
        if names:
            st.session_state.patient_queue = names
            st.session_state.patient_call_count = 0
            st.session_state.audio_bytes = None
            st.session_state.last_action_msg = f"✅ Lista cargada ({len(names)} pacientes)."
        else:
            st.session_state.patient_queue = []
            st.session_state.last_action_msg = "⚠️ Por favor, ingresa al menos un paciente."

# Mensajes de notificación
if st.session_state.last_action_msg:
    st.info(st.session_state.last_action_msg)

# Contenido principal
if st.session_state.patient_queue:
    current_patient = st.session_state.patient_queue[0]
    
    st.markdown("### 👤 Paciente en Turno")
    st.markdown(f"# **{current_patient}**")
    
    call_num_display = st.session_state.patient_call_count
    st.caption(f"Veces llamado: **{call_num_display}** | Restantes en fila: **{len(st.session_state.patient_queue)}**")

    # Botón 1: Llamar Paciente
    if st.button("📢 Llamar Paciente Actual", type="primary", use_container_width=True):
        st.session_state.patient_call_count += 1
        
        if st.session_state.patient_call_count >= 3:
            phrase = f"Último llamado. Paciente {current_patient}, por favor acérquese al consultorio número {office_number}."
            tag = " (ÚLTIMO LLAMADO)"
        else:
            phrase = f"Paciente {current_patient}, por favor acérquese al consultorio número {office_number}."
            tag = ""
            
        st.session_state.audio_bytes = generate_patient_voice(phrase)
        st.session_state.last_action_msg = f"Llamando a {current_patient}{tag} - Llamado #{st.session_state.patient_call_count}"

    # Botón 2: Siguiente Paciente
    if st.button("➡️ Siguiente Paciente en Fila", type="secondary", use_container_width=True):
        completed_patient = st.session_state.patient_queue.pop(0)
        st.session_state.patient_call_count = 0
        st.session_state.audio_bytes = None
        
        if st.session_state.patient_queue:
            st.session_state.last_action_msg = f"Atendido: {completed_patient}. Siguiente: {st.session_state.patient_queue[0]}"
        else:
            st.session_state.last_action_msg = "🎉 Todos los pacientes han sido llamados."
        st.rerun()

    # Reproducción de audio estable
    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format="audio/mp3", autoplay=True)

else:
    st.warning("No hay pacientes en la cola. Carga una lista desde el menú lateral para iniciar.")
