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

# Initialize session states
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'file_dict' not in st.session_state:
    st.session_state.file_dict = {}
if 'version_info' not in st.session_state:
    st.session_state.version_info = {}

st.title("Markdown Documentation Generator")

# Version Input Section
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

# File Upload Section — ONLY .md files
st.header("Upload Markdown Files")
uploaded_files = st.file_uploader(
    "Upload .md files only",
    accept_multiple_files=True,
    type=['md', 'markdown']
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

# Preview Section (renders Markdown nicely)
st.header("Markdown Preview")
if app_version in st.session_state.file_dict:
    for file_name, content in st.session_state.file_dict[app_version].items():
        with st.expander(f"📄 {file_name}"):
            st.markdown(content)

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

        pdf_elements.append(Paragraph("Markdown Files:", styles['Heading2']))
        for file_name, content in st.session_state.file_dict[app_version].items():
            pdf_elements.append(Paragraph(f"File: {file_name}", styles['Heading3']))
            code_style = ParagraphStyle(
                name='CodeStyle',
                fontName='Courier',
                fontSize=8,
                leftIndent=10,
                rightIndent=10,
                leading=8,
                wordWrap='CJK'
            )
            pdf_elements.append(Preformatted(content, code_style, maxLineLength=65))
            pdf_elements.append(Spacer(1, 10))

        doc.build(pdf_elements)
        pdf_buffer.seek(0)
        pdf_data = pdf_buffer.read()
        st.markdown(create_download_link_pdf(pdf_data, f"docs_{app_version}.pdf"), unsafe_allow_html=True)
    else:
        st.warning("Please add a version and upload .md files first.")

# Saved Versions
st.write("## Saved Versions")
for version in st.session_state.task_list:
    st.write(f"### App Version: {version}")
    if version in st.session_state.version_info:
        st.write(f"**Interpreter Version:** {st.session_state.version_info[version]['interpreter_version']}")
    st.write(f"Number of .md files: {len(st.session_state.file_dict.get(version, {}))}")
