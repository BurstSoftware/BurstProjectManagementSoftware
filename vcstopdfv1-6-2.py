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
    """Map filename or extension to Streamlit syntax highlighting language."""
    name_lower = file_name.lower()

    # Special filenames
    special_files = {
        "dockerfile": "dockerfile",
        "docker-compose.yml": "dockerfile",
        "docker-compose.yaml": "dockerfile",
        "makefile": "makefile",
        "gnumakefile": "makefile",
        "cmakelists.txt": "cmake",
    }
    if name_lower in special_files:
        return special_files[name_lower]

    # Get extension
    ext = name_lower.split(".")[-1] if "." in name_lower else ""

    # === EXHAUSTIVE LANGUAGE MAP (with HTMX added) ===
    lang_map = {
        # === Systems & Low-Level ===
        "c": "c", "h": "c",
        "cpp": "cpp", "cc": "cpp", "cxx": "cpp", "hpp": "cpp", "hxx": "cpp",
        "rs": "rust",
        "go": "go",
        "zig": "zig",
        "odin": "odin",
        "v": "v",
        "nim": "nim",
        "crystal": "crystal",
        
        # === Assembly ===
        "asm": "asm", "s": "asm", "S": "asm", "nasm": "nasm",
        
        # === Fortran & Scientific ===
        "f": "fortran", "f90": "fortran", "f95": "fortran", "f03": "fortran",
        "f08": "fortran", "for": "fortran", "f77": "fortran",
        
        # === Functional & Lisp ===
        "lisp": "lisp", "cl": "lisp", "el": "elisp", "scm": "scheme", "rkt": "racket",
        "hs": "haskell", "lhs": "haskell",
        "ml": "ocaml", "mli": "ocaml",
        "fs": "fsharp", "fsx": "fsharp", "fsi": "fsharp",
        "erl": "erlang", "hrl": "erlang",
        "ex": "elixir", "exs": "elixir",
        
        # === Modern & Popular ===
        "py": "python", "pyx": "python", "pyi": "python",
        "js": "javascript", "jsx": "jsx", "mjs": "javascript", "cjs": "javascript",
        "ts": "typescript", "tsx": "tsx",
        "java": "java",
        "kt": "kotlin", "kts": "kotlin",
        "scala": "scala", "sc": "scala",
        "cs": "csharp",
        "rb": "ruby",
        "php": "php",
        "swift": "swift",
        "dart": "dart",
        "lua": "lua",
        "jl": "julia",
        "r": "r", "rmd": "r",
        
        # === Web & Markup (HTMX added here) ===
        "html": "html",
        "htm": "html",
        "htmx": "html",          # ← HTMX support (uses HTML highlighting)
        "css": "css",
        "scss": "scss", "sass": "sass", "less": "less",
        "md": "markdown", "markdown": "markdown",
        "rst": "rst", "adoc": "asciidoc",
        
        # === Data & Config ===
        "json": "json",
        "yaml": "yaml", "yml": "yaml",
        "toml": "toml",
        "xml": "xml",
        "ini": "ini", "cfg": "ini", "conf": "ini",
        "properties": "properties",
        "env": "bash",
        
        # === Database & Query ===
        "sql": "sql",
        "graphql": "graphql", "gql": "graphql",
        
        # === Scripting & Shell ===
        "sh": "bash", "bash": "bash", "zsh": "bash", "fish": "fish",
        "ps1": "powershell", "psm1": "powershell",
        "bat": "batch", "cmd": "batch",
        "pl": "perl", "pm": "perl",
        
        # === Other Notable ===
        "matlab": "matlab", "m": "matlab",
        "prolog": "prolog",
        "sol": "solidity",
        "cu": "cuda", "cuh": "cuda",
        
        # === Build & Tools ===
        "cmake": "cmake",
        "dockerfile": "dockerfile",
        "proto": "protobuf",
        
        # === Others ===
        "txt": "text",
        "log": "text",
        "k": "text",
    }
    
    return lang_map.get(ext, "text")


# Initialize session states
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'file_dict' not in st.session_state:
    st.session_state.file_dict = {}
if 'version_info' not in st.session_state:
    st.session_state.version_info = {}

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

# Supported types (HTMX extension included)
supported_types = list(set([
    'py', 'pyx', 'pyi', 'js', 'jsx', 'mjs', 'cjs', 'ts', 'tsx',
    'java', 'kt', 'kts', 'scala', 'c', 'h', 'cpp', 'cc', 'cxx', 'hpp', 'hxx',
    'rs', 'go', 'zig', 'odin', 'v', 'nim', 'crystal',
    'asm', 's', 'S', 'f', 'f90', 'f95', 'f03', 'f08', 'for', 'f77',
    'lisp', 'cl', 'el', 'scm', 'rkt', 'hs', 'lhs', 'ml', 'mli',
    'fs', 'fsx', 'fsi', 'erl', 'hrl', 'ex', 'exs',
    'rb', 'php', 'swift', 'dart', 'lua', 'jl', 'r', 'rmd',
    'html', 'htm', 'htmx', 'css', 'scss', 'sass', 'less', 'md', 'markdown', 'rst', 'adoc',
    'json', 'yaml', 'yml', 'toml', 'xml', 'ini', 'cfg', 'conf', 'properties',
    'sql', 'graphql', 'gql',
    'sh', 'bash', 'zsh', 'fish', 'ps1', 'psm1', 'bat', 'cmd', 'pl', 'pm',
    'matlab', 'm', 'prolog', 'sol', 'cu', 'cuh',
    'cmake', 'proto', 'dockerfile', 'k', 'txt'
]))

uploaded_files = st.file_uploader(
    "Upload code files — supports 100+ languages including .md, HTMX, Rust, Go, Julia, Zig, etc.",
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

# Display uploaded files
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

        pdf_elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))
        if app_version in st.session_state.version_info:
            interpreter_ver = st.session_state.version_info[app_version]['interpreter_version']
            pdf_elements.append(Paragraph(f"Interpreter Version: {interpreter_ver}", styles['Normal']))
            pdf_elements.append(Spacer(1, 10))

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
