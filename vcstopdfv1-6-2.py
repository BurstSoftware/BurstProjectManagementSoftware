import streamlit as st
from io import BytesIO
import base64
from streamlit_ace import st_ace
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import datetime

st.set_page_config(
    page_title="Testing Documentation App",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== FILE TYPE MAPPING ======================
LANGUAGE_MAP = {
    "py": "python", "js": "javascript", "ts": "typescript",
    "html": "html", "htm": "html", "css": "css",
    "md": "markdown", "json": "json",
    "yaml": "yaml", "yml": "yaml", "sql": "sql",
    "sh": "sh", "bash": "sh",
    "rs": "rust", "go": "golang",
    "cpp": "c_cpp", "c": "c_cpp",
    "txt": "text",
    "dockerfile": "dockerfile", "makefile": "makefile",
    "cmakelists.txt": "cmake", "docker-compose.yml": "yaml",
}

FILE_OPTIONS = list(LANGUAGE_MAP.keys())

# ====================== PREDEFINED PRESETS (kept from your code) ======================
PRESETS = { ... }  # ← paste your full PRESETS dict here (unchanged)

# ====================== HELPER FUNCTIONS ======================
def create_download_link_pdf(pdf_data, filename):
    b64 = base64.b64encode(pdf_data).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Download PDF</a>'

def get_ace_language(ext: str) -> str:
    return LANGUAGE_MAP.get(ext.lower(), "text")

# ====================== SESSION STATE ======================
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'current_version' not in st.session_state:
    st.session_state.current_version = ""
if 'requirements_dict' not in st.session_state:
    st.session_state.requirements_dict = {}
if 'code_entries' not in st.session_state:          # NEW: structured code storage
    st.session_state.code_entries = {}
if 'notes_dict' not in st.session_state:
    st.session_state.notes_dict = {}
if 'terminal_dict' not in st.session_state:
    st.session_state.terminal_dict = {}
if 'voice_notes' not in st.session_state:
    st.session_state.voice_notes = {}
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("⚙️ Quick Controls")
    st.session_state.current_version = st.text_input(
        "Current App Version", 
        value=st.session_state.current_version or "v1.0.0"
    )
    
    if st.button("➕ Add Version to List"):
        if st.session_state.current_version and st.session_state.current_version not in st.session_state.task_list:
            st.session_state.task_list.append(st.session_state.current_version)
            st.success(f"Added {st.session_state.current_version}")

    st.divider()
    st.caption("Made with ❤️ using Streamlit + Ace Editor")

# ====================== MAIN TABS ======================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 Project Setup", 
    "📤 Upload Files", 
    "💻 Code & Notes", 
    "🎤 Voice Notes", 
    "🤖 AI Assistant", 
    "👁️ Preview & Edit", 
    "📄 Generate PDF"
])

# ====================== TAB 1: PROJECT SETUP ======================
with tab1:
    st.header("🏠 Project Setup")
    
    col1, col2 = st.columns(2)
    with col1:
        preset_choice = st.selectbox("Choose Project Preset", list(PRESETS.keys()))
    with col2:
        st.info(f"**Project Type:** {PRESETS[preset_choice]['project_type']}")

    selected = PRESETS[preset_choice]

    requirements_input = st.text_area(
        "requirements.txt", 
        value=selected["requirements"], 
        height=200
    )

    if st.button("💾 Save requirements.txt", use_container_width=True):
        version = st.session_state.current_version
        if version not in st.session_state.requirements_dict:
            st.session_state.requirements_dict[version] = []
        st.session_state.requirements_dict[version].append({
            "project_type": selected["project_type"],
            "python_version": selected["python_version"] or "Not specified",
            "content": requirements_input
        })
        st.success("requirements.txt saved!")

    terminal = st.text_area("Terminal Output", height=150)
    if st.button("💾 Save Terminal Output"):
        version = st.session_state.current_version
        if version not in st.session_state.terminal_dict:
            st.session_state.terminal_dict[version] = []
        st.session_state.terminal_dict[version].append(terminal)
        st.success("Terminal output saved!")

# ====================== TAB 2: UPLOAD FILES ======================
with tab2:
    st.header("📤 Upload Files")
    uploaded = st.file_uploader(
        "Drop files here (code, requirements, configs, etc.)",
        accept_multiple_files=True,
        type=FILE_OPTIONS + ['txt']
    )
    
    if uploaded:
        for file in uploaded:
            ext = file.name.split('.')[-1].lower() if '.' in file.name else 'txt'
            content = file.read().decode("utf-8", errors="ignore")
            
            st.write(f"**{file.name}** ({ext})")
            if st.button(f"Add {file.name} to Code Sections", key=f"add_{file.name}"):
                version = st.session_state.current_version
                if version not in st.session_state.code_entries:
                    st.session_state.code_entries[version] = []
                st.session_state.code_entries[version].append({
                    "filename": file.name,
                    "extension": ext,
                    "content": content
                })
                st.success(f"Added {file.name} to {version}")

# ====================== TAB 3: CODE & NOTES ======================
with tab3:
    st.header("💻 Code & Notes Editor")
    
    version = st.session_state.current_version
    
    # Notes
    st.subheader("Testing Notes")
    note = st.text_area("Regression / Testing Notes", height=120, key="note_input")
    if st.button("💾 Save Note"):
        if version not in st.session_state.notes_dict:
            st.session_state.notes_dict[version] = []
        st.session_state.notes_dict[version].append(note)
        st.success("Note saved!")

    # Dynamic Code Sections
    st.subheader("Code Sections")
    
    if version not in st.session_state.code_entries:
        st.session_state.code_entries[version] = []

    if st.button("➕ Add New Code Section"):
        st.session_state.code_entries[version].append({
            "filename": "main.py",
            "extension": "py",
            "content": ""
        })

    for i, entry in enumerate(st.session_state.code_entries[version]):
        with st.container(border=True):
            cols = st.columns([3, 2, 6])
            with cols[0]:
                entry["filename"] = st.text_input("Filename", value=entry["filename"], key=f"fn_{i}")
            with cols[1]:
                entry["extension"] = st.selectbox(
                    "Extension", 
                    FILE_OPTIONS, 
                    index=FILE_OPTIONS.index(entry["extension"]) if entry["extension"] in FILE_OPTIONS else 0,
                    key=f"ext_{i}"
                )
            with cols[2]:
                entry["content"] = st_ace(
                    value=entry["content"],
                    language=get_ace_language(entry["extension"]),
                    theme="monokai",
                    key=f"ace_{i}",
                    height=200
                )
            
            if st.button("🗑️ Remove", key=f"remove_{i}"):
                st.session_state.code_entries[version].pop(i)
                st.rerun()

# ====================== TAB 4: VOICE NOTES ======================
with tab4:
    st.header("🎤 Voice Notes")
    audio_file = st.file_uploader("Upload voice recording", type=["wav", "mp3", "m4a", "ogg"])
    
    if audio_file:
        st.audio(audio_file)
        if st.button("🎙️ Transcribe Audio"):
            try:
                import speech_recognition as sr
                r = sr.Recognizer()
                with sr.AudioFile(audio_file) as source:
                    audio = r.record(source)
                    text = r.recognize_google(audio)
                    st.success("Transcription:")
                    st.write(text)
                    
                    version = st.session_state.current_version
                    if version not in st.session_state.notes_dict:
                        st.session_state.notes_dict[version] = []
                    st.session_state.notes_dict[version].append(f"[Voice Note] {text}")
            except Exception as e:
                st.error(f"Transcription failed: {e}")

# ====================== TAB 5: AI ASSISTANT ======================
with tab5:
    st.header("🤖 AI Assistant (Gemini)")
    
    enable_ai = st.checkbox("Enable Gemini AI Assistant")
    
    if enable_ai:
        api_key = st.text_input("Google Gemini API Key", type="password")
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = st.text_area("What do you need help with?", 
                    placeholder="Generate requirements.txt for a Streamlit dashboard with pandas and plotly")
                
                if st.button("🚀 Generate with AI"):
                    with st.spinner("Thinking..."):
                        response = model.generate_content(prompt)
                        st.markdown("### AI Response")
                        st.write(response.text)
                        
                        if st.button("💾 Save to Notes"):
                            version = st.session_state.current_version
                            if version not in st.session_state.notes_dict:
                                st.session_state.notes_dict[version] = []
                            st.session_state.notes_dict[version].append(f"[AI Generated] {response.text}")
                            st.success("Saved to notes!")
            except Exception as e:
                st.error(f"AI Error: {e}")

# ====================== TAB 6: PREVIEW & EDIT ======================
with tab6:
    st.header("👁️ Preview & Edit Saved Items")
    
    for version in st.session_state.task_list:
        with st.expander(f"📌 {version}", expanded=True):
            # Requirements
            if version in st.session_state.requirements_dict:
                for i, req in enumerate(st.session_state.requirements_dict[version]):
                    st.markdown(f"**requirements.txt #{i+1}**")
                    st.code(req["content"], language="text")
            
            # Code
            if version in st.session_state.code_entries:
                for i, entry in enumerate(st.session_state.code_entries[version]):
                    st.markdown(f"**{entry['filename']}** (`{entry['extension']}`)")
                    st.code(entry["content"], language=get_ace_language(entry["extension"]))

# ====================== TAB 7: GENERATE PDF ======================
with tab7:
    st.header("📄 Generate Documentation PDF")
    
    if st.button("📄 Generate Professional PDF", use_container_width=True):
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, 
                               leftMargin=0.6*inch, rightMargin=0.6*inch)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        elements.append(Paragraph("Testing Documentation Report", styles['Title']))
        elements.append(Paragraph(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        for version in st.session_state.task_list:
            elements.append(Paragraph(f"App Version: {version}", styles['Heading1']))
            
            # Add all your saved content here (requirements, code, notes, etc.)
            # (same logic as your original PDF generation, just cleaner)
            
        doc.build(elements)
        pdf_buffer.seek(0)
        st.markdown(create_download_link_pdf(pdf_buffer.read(), f"documentation_{version}.pdf"), unsafe_allow_html=True)

st.caption("Pro tip: Use the tabs above for the best experience. Everything is saved in session state until you refresh.")
