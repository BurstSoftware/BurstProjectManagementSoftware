import streamlit as st
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

# Function to create download PDF link
def create_download_link_pdf(pdf_data, download_filename):
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{download_filename}">Download PDF</a>'
    return href

def get_file_language(file_name: str) -> str:
    """Determine the language for syntax highlighting based on filename/extension."""
    name_lower = file_name.lower()
    
    # Special filenames (no extension)
    if name_lower in ["dockerfile", "docker-compose.yml", "docker-compose.yaml"]:
        return "dockerfile"
    if name_lower in ["makefile", "gnumakefile"]:
        return "makefile"
    
    # Get extension
    if "." in name_lower:
        ext = name_lower.split(".")[-1]
    else:
        ext = ""
    
    # Language mapping
    lang_map = {
        # Python
        "py": "python",
        "pyx": "python",
        "pyi": "python",
        
        # JavaScript / TypeScript
        "js": "javascript",
        "jsx": "jsx",
        "mjs": "javascript",
        "cjs": "javascript",
        "ts": "typescript",
        "tsx": "tsx",
        
        # JVM languages
        "java": "java",
        "kt": "kotlin",
        "kts": "kotlin",
        "scala": "scala",
        
        # C family
        "c": "c",
        "h": "c",
        "cpp": "cpp",
        "cc": "cpp",
        "cxx": "cpp",
        "hpp": "cpp",
        "hxx": "cpp",
        "cs": "csharp",
        
        # Others
        "go": "go",
        "rs": "rust",
        "rb": "ruby",
        "php": "php",
        "swift": "swift",
        "r": "r",
        "sql": "sql",
        
        # Web
        "html": "html",
        "htm": "html",
        "css": "css",
        "scss": "scss",
        "sass": "sass",
        "less": "less",
        
        # Data / Config
        "json": "json",
        "yaml": "yaml",
        "yml": "yaml",
        "toml": "toml",
        "xml": "xml",
        "ini": "ini",
        "cfg": "ini",
        "conf": "ini",
        
        # Documentation / Markdown
        "md": "markdown",
        "markdown": "markdown",
        
        # Shell / Scripts
        "sh": "bash",
        "bash": "bash",
        "zsh": "bash",
        "ps1": "powershell",
        
        # Plain text
        "txt": "text",
    }
    
    return lang_map.get(ext, "text")

# Initialize session states
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'file_dict' not in st.session_state:
    st.session_state.file_dict = {}
if 'version_info' not in st.session_state:
    st.session_state.version_info = {}

# Main app layout
st.title("Codebase Documentation Generator")

# Version Input Section
st.header("Version Information")
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version:")
with col2:
    interpreter_version = st.text_input("Interpreter Version:", placeholder="e.g., Python 3.12")

if st.button("Save Version Information"):
    if app_version and app_version not in st.session_state.task_list:
        st.session_state.task_list.append(app_version)
        st.session_state.version_info[app_version] = {
            'app_version': app_version,
            'interpreter_version': interpreter_version
        }

# File Upload Section
st.header("Upload Code Files")

# Expanded list of supported file types
supported_types = [
    'py', 'pyx', 'pyi', 'js', 'jsx', 'mjs', 'cjs', 'ts', 'tsx',
    'java', 'kt', 'kts', 'scala', 'c', 'h', 'cpp', 'cc', 'cxx', 'hpp', 'hxx', 'cs',
    'go', 'rs', 'rb', 'php', 'swift', 'r', 'sql',
    'html', 'htm', 'css', 'scss', 'sass', 'less',
    'json', 'yaml', 'yml', 'toml', 'xml', 'ini', 'cfg', 'conf',
    'md', 'markdown',
    'sh', 'bash', 'zsh', 'ps1',
    'txt', 'dockerfile'
]

uploaded_files = st.file_uploader(
    "Upload your code files (supports many languages including .md)",
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
            file_content = "Binary or non-UTF-8 content - cannot display"
        
        st.session_state.file_dict[app_version][file_name] = file_content

# Display uploaded files with better syntax highlighting
st.header("Codebase Preview")
if app_version in st.session_state.file_dict:
    for file_name, file_content in st.session_state.file_dict[app_version].items():
        with st.expander(f"File: {file_name}"):
            language = get_file_language(file_name)
            st.code(file_content, language=language)

# Generate PDF
if st.button("Generate and Download PDF"):
    if app_version and app_version in st.session_state.file_dict:
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
        styles = getSampleStyleSheet()
        pdf_elements = []

        # Add version information
        pdf_elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))
        if app_version in st.session_state.version_info:
            interpreter_ver = st.session_state.version_info[app_version]['interpreter_version']
            pdf_elements.append(Paragraph(f"Interpreter Version: {interpreter_ver}", styles['Normal']))
            pdf_elements.append(Spacer(1, 10))

        # Add uploaded file content
        pdf_elements.append(Paragraph("Codebase Files:", styles['Heading2']))
        for file_name, file_content in st.session_state.file_dict[app_version].items():
            pdf_elements.append(Paragraph(f"File: {file_name}", styles['Heading3']))
            code_paragraph_style = ParagraphStyle(
                name='CodeStyle',
                fontName='Courier',
                fontSize=8,
                leftIndent=10,
                rightIndent=10,
                leading=8,
                wordWrap='CJK'
            )
            code_paragraph = Preformatted(file_content, code_paragraph_style, maxLineLength=65)
            pdf_elements.append(code_paragraph)
            pdf_elements.append(Spacer(1, 10))

        doc.build(pdf_elements)
        pdf_buffer.seek(0)
        pdf_data = pdf_buffer.read()

        st.markdown(create_download_link_pdf(pdf_data, f"codebase_{app_version}.pdf"), unsafe_allow_html=True)
    else:
        st.warning("Please upload files and specify an app version before generating PDF.")

# Display saved versions
st.write("## Saved Versions")
for version in st.session_state.task_list:
    st.write(f"### App Version: {version}")
    if version in st.session_state.version_info:
        st.write(f"**Interpreter Version:** {st.session_state.version_info[version]['interpreter_version']}")
    st.write(f"Number of files: {len(st.session_state.file_dict.get(version, {}))}")
