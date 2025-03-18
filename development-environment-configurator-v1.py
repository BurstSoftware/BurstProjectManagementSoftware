import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import speech_recognition as sr
import sounddevice as sd
import numpy as np
from datetime import datetime
import traceback

# Check if running locally (for voice input support)
try:
    import sounddevice
    LOCAL_ENV = True
except ImportError:
    LOCAL_ENV = False

# Initialize session state
if 'reportlab_instances' not in st.session_state:
    st.session_state.reportlab_instances = []
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = ""

# Main app title
st.title("Development Environment Configurator")

# App configuration inputs
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version", "1.0.0")
    interpreter = st.text_input("Interpreter", "Python 3.9")
with col2:
    ide = st.text_input("IDE/Text Editor", "VS Code")
    framework = st.text_input("Framework", "Streamlit")

# Google AI Studio API Key input
google_api_key = st.text_input("Google AI Studio API Key", type="password")

# Voice to text function (local only)
def voice_to_text():
    if not LOCAL_ENV:
        return "Voice input is only available in local environments."
    
    try:
        # Record audio using sounddevice
        st.info("Recording... Speak now! (5 seconds)")
        duration = 5  # seconds
        fs = 44100  # Sample rate
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  # Wait for recording to finish
        
        # Convert to WAV-like format for speech_recognition
        audio_data = np.frombuffer(recording.tobytes(), dtype=np.int16)
        
        # Use speech_recognition to process audio
        r = sr.Recognizer()
        audio = sr.AudioData(audio_data.tobytes(), fs, 2)  # 2 bytes per sample
        text = r.recognize_google(audio)
        return text
    except Exception as e:
        return f"Voice recognition failed: {str(e)}"

# ReportLab GUI component
def create_reportlab_gui(index):
    st.subheader(f"ReportLab Instance #{index + 1}")
    
    # Display hash symbol and input area
    content = st.text_area(
        f"Ideas/Notes (starts with #)", 
        value="# ",
        key=f"reportlab_{index}"
    )
    
    # Voice input (local) or file upload (cloud fallback)
    if LOCAL_ENV:
        if st.button("Voice Input", key=f"voice_{index}"):
            voice_text = voice_to_text()
            if not voice_text.startswith("Voice recognition failed"):
                content = f"# {voice_text}"
                st.session_state[f"reportlab_{index}"] = content
            else:
                st.error(voice_text)
    else:
        st.info("Voice input unavailable in cloud. Upload an audio file instead.")
        audio_file = st.file_uploader(f"Upload WAV file for Instance #{index + 1}", type=["wav"], key=f"audio_{index}")
        if audio_file:
            try:
                r = sr.Recognizer()
                with sr.AudioFile(audio_file) as source:
                    audio = r.record(source)
                    voice_text = r.recognize_google(audio)
                    content = f"# {voice_text}"
                    st.session_state[f"reportlab_{index}"] = content
                    st.success("Audio processed successfully")
            except Exception as e:
                st.error(f"Audio processing failed: {str(e)}")
    
    return content

# Add new ReportLab instance
if st.button("Add New ReportLab Instance"):
    st.session_state.reportlab_instances.append("")

# Display existing ReportLab instances
for i in range(len(st.session_state.reportlab_instances)):
    st.session_state.reportlab_instances[i] = create_reportlab_gui(i)

# Generate PDF
def generate_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    c.drawString(100, height - 50, f"App Version: {app_version}")
    c.drawString(100, height - 70, f"Interpreter: {interpreter}")
    c.drawString(100, height - 90, f"IDE: {ide}")
    c.drawString(100, height - 110, f"Framework: {framework}")
    
    y_position = height - 150
    for i, content in enumerate(st.session_state.reportlab_instances):
        if y_position < 50:
            c.showPage()
            y_position = height - 50
        c.drawString(100, y_position, f"Instance #{i + 1}:")
        y_position -= 20
        for line in content.split('\n'):
            if y_position < 50:
                c.showPage()
                y_position = height - 50
            c.drawString(120, y_position, line[:80])
            y_position -= 15
        y_position -= 20
    
    c.save()
    buffer.seek(0)
    return buffer

# Generate codebase
def generate_codebase():
    code = f"""# Generated App Codebase - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
import streamlit as st

# App Configuration
VERSION = '{app_version}'
INTERPRETER = '{interpreter}'
IDE = '{ide}'
FRAMEWORK = '{framework}'

st.title('Generated App')

# Features from ReportLab instances
"""
    for i, content in enumerate(st.session_state.reportlab_instances):
        code += f"\n# Features from Instance #{i + 1}\n"
        for line in content.split('\n')[1:]:
            if line.strip():
                code += f"st.write('{line.strip()}')\n"
    return code

# Export to PDF button
if st.button("Export to PDF"):
    if st.session_state.reportlab_instances:
        try:
            pdf_buffer = generate_pdf()
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name=f"app_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF generation failed: {str(e)}")
    else:
        st.warning("Please add at least one ReportLab instance first")

# Generate and display codebase
if st.button("Generate Codebase"):
    if st.session_state.reportlab_instances:
        try:
            st.session_state.generated_code = generate_codebase()
            st.subheader("Generated Codebase")
            st.code(st.session_state.generated_code, language="python")
            st.session_state.reportlab_instances.append(f"# Generated Codebase\n{st.session_state.generated_code}")
            st.success("Codebase added as new ReportLab instance")
        except Exception as e:
            st.error(f"Code generation failed: {str(e)}")
    else:
        st.warning("Please add at least one ReportLab instance first")

# Instructions
st.sidebar.header("Instructions")
st.sidebar.write("""
1. Enter app configuration details
2. Input Google AI Studio API Key (optional)
3. Add ReportLab instances using the button
4. Type ideas or use voice input (local) / upload WAV (cloud)
5. Export to PDF when ready
6. Generate codebase from your ideas
""")
