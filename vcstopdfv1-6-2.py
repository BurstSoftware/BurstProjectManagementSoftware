import streamlit as st
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import google.generativeai as genai
from streamlit_option_menu import option_menu
from streamlit_ace import st_ace
from streamlit_extras.card import card
import speech_recognition as sr
import requests  # already in requirements

# ====================== HELPER FUNCTIONS ======================
def create_download_link_pdf(pdf_data, download_filename):
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{download_filename}">📥 Download PDF</a>'
    return href

def get_file_language(file_name: str) -> str:
    name_lower = file_name.lower()
    special_files = {
        "dockerfile": "dockerfile", "makefile": "makefile",
        "cmakelists.txt": "cmake", "docker-compose.yml": "yaml",
    }
    if name_lower in special_files:
        return special_files[name_lower]
    ext = name_lower.split(".")[-1] if "." in name_lower else ""
    lang_map = {
        "py": "python", "js": "javascript", "ts": "typescript", "html": "html",
        "htmx": "html", "css": "css", "md": "markdown", "json": "json",
        "yaml": "yaml", "yml": "yaml", "sql": "sql", "sh": "bash",
        "rs": "rust", "go": "go", "cpp": "c_cpp", "c": "c",
        # add more as needed
    }
    return lang_map.get(ext, "text")

def get_gemini_response(api_key: str, prompt: str, code_context: str = "") -> str:
    """Generate content using Gemini (google-generativeai 0.3.2)"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')  # works well with 0.3.2
        full_prompt = f"{prompt}\n\nCode Context:\n{code_context}" if code_context else prompt
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error with Gemini: {str(e)}"

def transcribe_speech():
    """Voice input using speechrecognition"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now (max 10 seconds)")
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Speech service error: {e}"
        except Exception as e:
            return f"Microphone error: {e}"

# ====================== SESSION STATE ======================
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'file_dict' not in st.session_state:
    st.session_state.file_dict = {}
if 'version_info' not in st.session_state:
    st.session_state.version_info = {}
if 'ai_notes' not in st.session_state:
    st.session_state.ai_notes = {}

st.set_page_config(page_title="Codebase Documentation Generator", layout="wide")

# ====================== SIDEBAR NAVIGATION ======================
with st.sidebar:
    selected = option_menu(
        "Main Menu",
        ["🏠 Home", "📤 Upload Files", "👁️ Preview & Edit", "🤖 AI Assistant", "🎤 Voice Notes", "📄 Generate PDF"],
        icons=["house", "cloud-upload", "eye", "robot", "mic", "file-pdf"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical"
    )

st.title("📄 Codebase Documentation Generator")

# ====================== HOME / VERSION ======================
if selected == "🏠 Home":
    st.header("Version Information")
    col1, col2 = st.columns(2)
    with col1:
        app_version = st.text_input("App Version", placeholder="v1.0.0")
    with col2:
        interpreter_version = st.text_input("Interpreter Version", value="Python 3.14.6")

    if st.button("💾 Save Version", type="primary"):
        if app_version and app_version not in st.session_state.task_list:
            st.session_state.task_list.append(app_version)
            st.session_state.version_info[app_version] = {
                'app_version': app_version,
                'interpreter_version': interpreter_version
            }
            st.success(f"Version {app_version} saved!")
        elif app_version:
            st.info("Version already exists.")

    st.divider()
    st.subheader("Saved Versions")
    for version in st.session_state.task_list:
        with st.expander(f"Version: {version}"):
            info = st.session_state.version_info.get(version, {})
            st.write(f"**Interpreter:** {info.get('interpreter_version', 'N/A')}")
            st.write(f"**Files:** {len(st.session_state.file_dict.get(version, {}))}")

# ====================== UPLOAD ======================
elif selected == "📤 Upload Files":
    st.header("Upload Code Files")
    supported_types = ['py','js','ts','html','css','md','json','yaml','yml','sql','sh','rs','go','cpp','c','txt']

    uploaded_files = st.file_uploader(
        "Upload multiple code files",
        accept_multiple_files=True,
        type=supported_types
    )

    app_version = st.selectbox("Select Version for these files", 
                               options=st.session_state.task_list or ["New Version"])

    if uploaded_files and app_version:
        if app_version not in st.session_state.file_dict:
            st.session_state.file_dict[app_version] = {}
        for file in uploaded_files:
            content = file.read().decode('utf-8', errors='ignore')
            st.session_state.file_dict[app_version][file.name] = content
        st.success(f"Uploaded {len(uploaded_files)} file(s) to version {app_version}")

# ====================== PREVIEW & EDIT (with st_ace) ======================
elif selected == "👁️ Preview & Edit":
    st.header("Code Preview & Editor")
    if st.session_state.file_dict:
        version = st.selectbox("Select Version", list(st.session_state.file_dict.keys()))
        if version:
            file_names = list(st.session_state.file_dict[version].keys())
            selected_file = st.selectbox("Select File", file_names)
            if selected_file:
                content = st.session_state.file_dict[version][selected_file]
                language = get_file_language(selected_file)

                st.write(f"**Editing:** {selected_file}")
                edited_content = st_ace(
                    value=content,
                    language=language,
                    theme="monokai",
                    key=f"ace_{version}_{selected_file}",
                    height=500,
                    show_gutter=True,
                    show_print_margin=False
                )

                if st.button("💾 Save Changes"):
                    st.session_state.file_dict[version][selected_file] = edited_content
                    st.success("Changes saved!")
    else:
        st.info("Upload files first in the Upload section.")

# ====================== AI ASSISTANT (Gemini) ======================
elif selected == "🤖 AI Assistant":
    st.header("🤖 AI-Powered Documentation Assistant")
    
    api_key = st.text_input("Enter your Gemini API Key", type="password", 
                            help="Get free key at https://aistudio.google.com/app/apikey")

    if not api_key:
        st.warning("Please enter your Gemini API key to use AI features.")
    else:
        version = st.selectbox("Select Version", list(st.session_state.file_dict.keys()) if st.session_state.file_dict else [])
        
        if version:
            file_options = ["All Files"] + list(st.session_state.file_dict[version].keys())
            target = st.selectbox("Target", file_options)

            prompt = st.text_area("What would you like Gemini to do?", 
                                  value="Generate a clear technical summary and documentation for this code.")

            if st.button("🚀 Generate with Gemini", type="primary"):
                code_context = ""
                if target == "All Files":
                    for fname, fcontent in st.session_state.file_dict[version].items():
                        code_context += f"\n\n=== {fname} ===\n{fcontent[:3000]}"
                else:
                    code_context = st.session_state.file_dict[version][target]

                with st.spinner("Gemini is thinking..."):
                    result = get_gemini_response(api_key, prompt, code_context)

                st.subheader("Gemini Response")
                st.markdown(result)

                # Save as note
                if st.button("💾 Save as AI Note"):
                    note_key = f"{version}_{target}"
                    st.session_state.ai_notes[note_key] = result
                    st.success("Note saved!")

# ====================== VOICE NOTES ======================
elif selected == "🎤 Voice Notes":
    st.header("🎤 Voice Notes (Speech-to-Text)")
    st.info("Works best when running locally with microphone access.")

    if st.button("🎙️ Start Recording"):
        transcribed = transcribe_speech()
        st.text_area("Transcribed Text", transcribed, height=150)

        version = st.selectbox("Save to Version", st.session_state.task_list)
        if st.button("Save Voice Note"):
            if version not in st.session_state.ai_notes:
                st.session_state.ai_notes[version] = ""
            st.session_state.ai_notes[version] += f"\n[Voice Note] {transcribed}\n"
            st.success("Voice note saved!")

    if st.session_state.ai_notes:
        st.subheader("Saved Notes")
        for key, note in st.session_state.ai_notes.items():
            with st.expander(key):
                st.write(note)

# ====================== PDF GENERATION ======================
elif selected == "📄 Generate PDF":
    st.header("Generate Documentation PDF")
    
    if st.session_state.file_dict:
        version = st.selectbox("Version for PDF", list(st.session_state.file_dict.keys()))
        
        include_ai = st.checkbox("Include AI-generated notes/summaries (if available)")

        if st.button("📄 Generate PDF", type="primary"):
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, 
                                    leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph(f"Codebase Documentation - {version}", styles['Heading1']))
            if version in st.session_state.version_info:
                elements.append(Paragraph(
                    f"Interpreter: {st.session_state.version_info[version]['interpreter_version']}", 
                    styles['Normal']))
            elements.append(Spacer(1, 20))

            for fname, fcontent in st.session_state.file_dict[version].items():
                elements.append(Paragraph(f"File: {fname}", styles['Heading2']))
                code_style = ParagraphStyle('Code', fontName='Courier', fontSize=7, leading=9)
                elements.append(Preformatted(fcontent[:12000], code_style))
                elements.append(Spacer(1, 15))

            # Add AI notes if requested
            if include_ai and version in st.session_state.ai_notes:
                elements.append(Paragraph("AI-Generated Notes", styles['Heading1']))
                elements.append(Preformatted(st.session_state.ai_notes[version][:8000], code_style))

            doc.build(elements)
            pdf_buffer.seek(0)
            st.markdown(create_download_link_pdf(pdf_buffer.read(), f"codebase_{version}.pdf"), unsafe_allow_html=True)
    else:
        st.warning("Upload files first.")

st.caption("Built with Streamlit 1.32.0 + your specified packages | Python 3.14.6 compatible")
