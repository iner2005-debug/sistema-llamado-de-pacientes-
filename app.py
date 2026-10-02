import streamlit as st
import streamlit.components.v1 as components

# --- Configuración de página ---
st.set_page_config(
    page_title="Sistema de Llamado de Pacientes", 
    page_icon="🏥", 
    layout="centered"
)

# --- Inicialización del Estado de la Sesión ---
if "patient_queue" not in st.session_state:
    st.session_state.patient_queue = []
if "voice_call_count" not in st.session_state:
    st.session_state.voice_call_count = 0
if "patient_call_count" not in st.session_state:
    st.session_state.patient_call_count = 0
if "last_action_msg" not in st.session_state:
    st.session_state.last_action_msg = ""
if "speak_trigger" not in st.session_state:
    st.session_state.speak_trigger = None

# --- Función para reproducir voz en Español Latino / Colombiano usando Web Speech API ---
def play_web_speech(text, lang="es-CO"):
    """
    Genera un componente HTML/JS que ejecuta la síntesis de voz nativa 
    del navegador configurada en español de Colombia ('es-CO') o Latinoamérica ('es-419').
    """
    js_code = f"""
    <script>
        function speak() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel(); // Cancelar audios anteriores
                var msg = new SpeechSynthesisUtterance("{text}");
                msg.lang = '{lang}';
                msg.rate = 0.95; // Velocidad de lectura
                msg.pitch = 1.0;
                
                // Buscar voz colombiana o latina si está disponible en el dispositivo
                var voices = window.speechSynthesis.getVoices();
                var selectedVoice = voices.find(function(voice) {{
                    return voice.lang === 'es-CO' || voice.lang === 'es-419' || voice.lang.includes('es');
                }});
                if (selectedVoice) {{
                    msg.voice = selectedVoice;
                }}
                
                window.speechSynthesis.speak(msg);
            }} else {{
                alert('Tu navegador no soporta síntesis de voz.');
            }}
        }}
        // Ejecutar inmediatamente
        setTimeout(speak, 200);
    </script>
    """
    components.html(js_code, height=0, width=0)

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
            st.session_state.voice_call_count = 0
            st.session_state.patient_call_count = 0
            st.session_state.speak_trigger = None
            st.session_state.last_action_msg = f"✅ Lista cargada ({len(names)} pacientes)."
        else:
            st.session_state.patient_queue = []
            st.session_state.last_action_msg = "⚠️ Por favor, ingresa al menos un paciente."

# Mensaje de estado
if st.session_state.last_action_msg:
    st.info(st.session_state.last_action_msg)

# Contenido principal
if st.session_state.patient_queue:
    current_patient = st.session_state.patient_queue[0]
    
    st.markdown("### 👤 Paciente en Turno")
    st.markdown(f"# **{current_patient}**")
    
    call_num_display = st.session_state.patient_call_count
    st.caption(f"Veces llamado: **{call_num_display}** | Pacientes restantes en fila: **{len(st.session_state.patient_queue)}**")

    # Botones principales
    if st.button("📢 Llamar Paciente Actual", type="primary", use_container_width=True):
        st.session_state.patient_call_count += 1
        
        if st.session_state.patient_call_count >= 3:
            text_to_say = f"Último llamado. Paciente {current_patient}, por favor acérquese al consultorio número {office_number}."
            tag = " (ÚLTIMO LLAMADO)"
        else:
            text_to_say = f"Paciente {current_patient}, por favor acérquese al consultorio número {office_number}."
            tag = ""
            
        st.session_state.speak_trigger = text_to_say
        st.session_state.last_action_msg = f"Llamando a {current_patient}{tag} - Llamado #{st.session_state.patient_call_count}"

    if st.button("➡️ Siguiente Paciente en Fila", type="secondary", use_container_width=True):
        completed_patient = st.session_state.patient_queue.pop(0)
        st.session_state.patient_call_count = 0
        st.session_state.speak_trigger = None
        
        if st.session_state.patient_queue:
            st.session_state.last_action_msg = f"Atendido: {completed_patient}. Siguiente: {st.session_state.patient_queue[0]}"
        else:
            st.session_state.last_action_msg = "🎉 Todos los pacientes han sido llamados."
        st.rerun()

    # Reproducción de voz nativa del dispositivo/navegador
    if st.session_state.speak_trigger:
        play_web_speech(st.session_state.speak_trigger, lang="es-CO")

else:
    st.warning("No hay pacientes en la cola. Carga una lista desde el menú lateral para iniciar.")
