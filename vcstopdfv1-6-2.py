import streamlit as st
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_download_link_pdf(pdf_data, download_filename):
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{download_filename}">Download PDF</a>'
    return href

def get_file_language(file_name: str) -> str:
    """Simple language detection for syntax highlighting."""
    name_lower = file_name.lower()
    
    # Special files
    if "dockerfile" in name_lower:
        return "dockerfile"
    if "makefile" in name_lower:
        return "makefile"
    
    # Extension
    ext = name_lower.split(".")[-1] if "." in name_lower else ""
    
    lang_map = {
        # Core languages
        "py": "python", "js": "javascript", "jsx": "jsx", "ts": "typescript", "tsx": "tsx",
        "java": "java", "cpp": "cpp", "c": "c", "cs": "csharp",
        "go": "go", "rs": "rust", "rb": "ruby", "php": "php",
        "swift": "swift", "kt": "kotlin", "dart": "dart",
        "lua": "lua", "jl": "julia", "r": "r",
        "html": "html", "htm": "html", "htmx": "html",  # HTMX
        "css": "css", "md": "markdown", "markdown": "markdown",
        "json": "json", "yaml": "yaml", "yml": "yaml",
        "sql": "sql", "sh": "bash", "txt": "text",
    }
    return lang_map.get(ext, "text")


# Session state
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'file_dict' not in st.session_state:
    st.session_state.file_dict = {}
if 'version_info' not in st.session_state:
    st.session_state.version_info = {}

st.title("Codebase Documentation Generator")

# Version Input
st.header("Version Information")
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version:")
with col2:
    interpreter_version = st.text_input("Interpreter Version:", placeholder="e.g. Python 3.12")

if st.button("Save Version Information"):
    if app_version and app_version not in st.session_state.task_list:
        st.session_state.task_list.append(app_version)
        st.session_state.version_info[app_version] = {
            'app_version': app_version,
            'interpreter_version': interpreter_version
        }

# File Upload
st.header("Upload Code Files")
supported_types = ['py','js','jsx','ts','tsx','java','cpp','c','cs','go','rs','rb','php',
                   'swift','kt','dart','lua','jl','r','html','htm','htmx','css','md',
                   'markdown','json','yaml','yml','sql','sh','txt']

uploaded_files = st.file_uploader(
    "Upload files (.md, .py, .js, .html, .htmx, etc.)",
    accept_multiple_files=True,
    type=supported_types
)

if uploaded_files and app_version:
    if app_version not in st.session_state.file_dict:
        st.session_state.file_dict[app_version] = {}
    
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        try:
            file_content = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
            file_content = "Binary or non-UTF-8 content"
        
        st.session_state.file_dict[app_version][file_name] = file_content

# Preview
st.header("Codebase Preview")
if app_version in st.session_state.file_dict:
    for file_name, content in st.session_state.file_dict[app_version].items():
        with st.expander(f"📄 {file_name}"):
            lang = get_file_language(file_name)
            st.code(content, language=lang)

# PDF Generation
if st.button("Generate and Download PDF"):
    if app_version and app_version in st.session_state.file_dict:
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))
        if app_version in st.session_state.version_info:
            ver = st.session_state.version_info[app_version]['interpreter_version']
            elements.append(Paragraph(f"Interpreter: {ver}", styles['Normal']))
            elements.append(Spacer(1, 12))

        elements.append(Paragraph("Codebase Files:", styles['Heading2']))
        for name, content in st.session_state.file_dict[app_version].items():
            elements.append(Paragraph(f"File: {name}", styles['Heading3']))
            style = ParagraphStyle('Code', fontName='Courier', fontSize=8, leftIndent=10,
                                   rightIndent=10, leading=8, wordWrap='CJK')
            elements.append(Preformatted(content, style, maxLineLength=65))
            elements.append(Spacer(1, 12))

        doc.build(elements)
        pdf_buffer.seek(0)
        st.markdown(create_download_link_pdf(pdf_buffer.read(), f"codebase_{app_version}.pdf"),
                    unsafe_allow_html=True)
    else:
        st.warning("Please add a version and upload files first.")

# Saved Versions
st.write("## Saved Versions")
for v in st.session_state.task_list:
    st.write(f"### {v}")
    if v in st.session_state.version_info:
        st.write(f"Interpreter: {st.session_state.version_info[v]['interpreter_version']}")
    st.write(f"Files: {len(st.session_state.file_dict.get(v, {}))}")
