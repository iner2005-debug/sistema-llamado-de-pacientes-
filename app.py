import asyncio
import streamlit as st
import edge_tts

# --- Configuración de página ---
st.set_page_config(page_title="Sistema de Llamado de Pacientes", page_icon="🏥", layout="centered")

# --- Inicialización del Estado de la Sesión ---
if "patient_queue" not in st.session_state:
    st.session_state.patient_queue = []
if "voice_call_count" not in st.session_state:
    st.session_state.voice_call_count = 0
if "patient_call_count" not in st.session_state:
    st.session_state.patient_call_count = 0
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "last_action_msg" not in st.session_state:
    st.session_state.last_action_msg = ""

# --- Función Asíncrona para generar audio con Edge-TTS (Acento Colombiano) ---
async def generate_voice_async(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

def generate_patient_voice(name, office_num, call_number, voice_type="female"):
    """
    Genera audio sintético usando voces neuronales colombianas de Microsoft Edge.
    - Femenina: es-CO-SalmeNeural
    - Masculina: es-CO-GonzaloNeural
    """
    if call_number >= 3:
        text = f"Último llamado. Paciente {name}, por favor acérquese al consultorio número {office_num}."
    else:
        text = f"Paciente {name}, por favor acérquese al consultorio número {office_num}."
    
    # Selección de voz colombiana neuronal
    voice = "es-CO-SalmeNeural" if voice_type == "female" else "es-CO-GonzaloNeural"
    
    # Ejecutar la función asíncrona dentro del flujo síncrono de Streamlit
    return asyncio.run(generate_voice_async(text, voice))

# --- Interfaz de Usuario ---
st.title("🏥 Sistema de Llamado de Pacientes")

# Panel lateral
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
            st.session_state.patient_call_count = 0
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
    
    call_num_display = st.session_state.patient_call_count
    if call_num_display > 0:
        st.caption(f"Veces llamado: **{call_num_display}** | Pacientes restantes en fila: **{len(st.session_state.patient_queue)}**")
    else:
        st.caption(f"Pacientes restantes en fila: **{len(st.session_state.patient_queue)}**")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📢 Llamar Paciente Actual", use_container_width=True):
            st.session_state.patient_call_count += 1
            
            # Alternar entre voz femenina y masculina colombiana
            voice_type = "female" if st.session_state.voice_call_count % 2 == 0 else "male"
            
            st.session_state.audio_bytes = generate_patient_voice(
                current_patient, 
                office_number, 
                st.session_state.patient_call_count,
                voice_type
            )
            
            st.session_state.voice_call_count += 1
            tag = " (ÚLTIMO LLAMADO)" if st.session_state.patient_call_count >= 3 else ""
            st.session_state.last_action_msg = f"Llamando a {current_patient}{tag} - Llamado #{st.session_state.patient_call_count} (Voz: {voice_type})"

    with col2:
        if st.button("➡️ Siguiente Paciente en Fila", type="secondary", use_container_width=True):
            completed_patient = st.session_state.patient_queue.pop(0)
            st.session_state.patient_call_count = 0
            st.session_state.audio_bytes = None
            
            if st.session_state.patient_queue:
                st.session_state.last_action_msg = f"Atendido: {completed_patient}. Siguiente: {st.session_state.patient_queue[0]}"
            else:
                st.session_state.last_action_msg = "🎉 Todos los pacientes han sido llamados."
            st.rerun()

    # Reproducción de audio
    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format="audio/mp3", autoplay=True)

else:
    st.warning("No hay pacientes en la cola. Carga una lista desde el panel lateral para iniciar.")
