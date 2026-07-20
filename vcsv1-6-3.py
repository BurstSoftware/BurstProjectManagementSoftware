import streamlit as st
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_download_link_pdf(pdf_data: bytes, download_filename: str) -> str:
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{download_filename}">📥 Download PDF</a>'
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
    
    # Exhaustive language map
    lang_map = {
        # Systems & Low-Level
        "c": "c", "h": "c", "cpp": "cpp", "cc": "cpp", "cxx": "cpp", 
        "hpp": "cpp", "hxx": "cpp", "rs": "rust", "go": "go", "zig": "zig",
        "odin": "odin", "v": "v", "nim": "nim", "crystal": "crystal",
        # ... (your full map remains unchanged - it's excellent)
        "py": "python", "js": "javascript", "ts": "typescript", "html": "html",
        "htmx": "html", "md": "markdown", "json": "json", "yaml": "yaml",
        "sql": "sql", "sh": "bash", "txt": "text",
        # Add any missing ones if needed
    }
    return lang_map.get(ext, "text")


# ====================== SESSION STATE ======================
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'file_dict' not in st.session_state:
    st.session_state.file_dict = {}
if 'version_info' not in st.session_state:
    st.session_state.version_info = {}

st.title("📄 Codebase Documentation Generator")

# ====================== VERSION INPUT ======================
st.header("Version Information")
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version", placeholder="v1.2.3", key="app_ver")
with col2:
    interpreter_version = st.text_input(
        "Interpreter Version", 
        placeholder="Python 3.14.6",
        value="Python 3.14.6"  # default for your request
    )

if st.button("💾 Save Version Information", type="primary"):
    if app_version.strip():
        if app_version not in st.session_state.task_list:
            st.session_state.task_list.append(app_version)
            st.session_state.version_info[app_version] = {
                'app_version': app_version,
                'interpreter_version': interpreter_version
            }
            st.success(f"Version {app_version} saved!")
        else:
            st.info("Version already exists.")
    else:
        st.warning("Please enter an app version.")

# ====================== FILE UPLOAD ======================
st.header("Upload Code Files")
supported_types = [ ... ]  # your list is fine - keep it

uploaded_files = st.file_uploader(
    "Upload code files (100+ languages supported including HTMX, Rust, Zig, etc.)",
    accept_multiple_files=True,
    type=supported_types
)

if uploaded_files and app_version.strip():
    if app_version not in st.session_state.file_dict:
        st.session_state.file_dict[app_version] = {}
    
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        if file_name not in st.session_state.file_dict[app_version]:
            try:
                file_content = uploaded_file.read().decode('utf-8')
            except UnicodeDecodeError:
                file_content = "⚠️ Binary or non-UTF-8 file - cannot display content"
            except Exception as e:
                file_content = f"Error reading file: {e}"
            
            st.session_state.file_dict[app_version][file_name] = file_content
            st.toast(f"✅ Added {file_name}", icon="📄")

# ====================== PREVIEW ======================
st.header("Codebase Preview")
if app_version and app_version in st.session_state.file_dict:
    st.info(f"Showing files for version: **{app_version}**")
    for file_name, file_content in st.session_state.file_dict[app_version].items():
        with st.expander(f"📄 {file_name}"):
            language = get_file_language(file_name)
            st.code(file_content[:10000] + ("..." if len(file_content) > 10000 else ""), 
                   language=language, line_numbers=True)
else:
    st.info("No files uploaded for the current version yet.")

# ====================== PDF GENERATION ======================
if st.button("🚀 Generate and Download PDF", type="primary"):
    if app_version and app_version in st.session_state.file_dict and st.session_state.file_dict[app_version]:
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer, 
            pagesize=letter, 
            leftMargin=36, 
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        styles = getSampleStyleSheet()
        pdf_elements = []

        pdf_elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))
        
        if app_version in st.session_state.version_info:
            interp = st.session_state.version_info[app_version]['interpreter_version']
            pdf_elements.append(Paragraph(f"Interpreter Version: {interp}", styles['Normal']))
            pdf_elements.append(Spacer(1, 12))

        pdf_elements.append(Paragraph("Codebase Files:", styles['Heading2']))

        for file_name, file_content in st.session_state.file_dict[app_version].items():
            pdf_elements.append(Paragraph(f"File: {file_name}", styles['Heading3']))
            
            code_style = ParagraphStyle(
                'CodeStyle',
                parent=styles['Normal'],
                fontName='Courier',
                fontSize=8,
                leftIndent=10,
                rightIndent=10,
                leading=8,
                wordWrap='CJK'
            )
            # Truncate very long files for PDF
            display_content = file_content[:15000] + ("\n... [truncated]" if len(file_content) > 15000 else "")
            pdf_elements.append(Preformatted(display_content, code_style, maxLineLength=80))
            pdf_elements.append(Spacer(1, 12))

        doc.build(pdf_elements)
        pdf_buffer.seek(0)
        pdf_data = pdf_buffer.read()

        st.success("✅ PDF generated successfully!")
        st.markdown(create_download_link_pdf(pdf_data, f"codebase_{app_version}.pdf"), unsafe_allow_html=True)
    else:
        st.error("Please specify a version and upload at least one file.")

# ====================== SAVED VERSIONS ======================
st.divider()
st.subheader("Saved Versions")
if st.session_state.task_list:
    for version in st.session_state.task_list:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**{version}**")
        with col2:
            files_count = len(st.session_state.file_dict.get(version, {}))
            st.write(f"Files: **{files_count}**")
        with col3:
            if st.button("🗑️", key=f"del_{version}"):
                # Simple delete logic (you can expand this)
                st.session_state.task_list.remove(version)
                st.session_state.file_dict.pop(version, None)
                st.session_state.version_info.pop(version, None)
                st.rerun()
else:
    st.info("No versions saved yet.")
