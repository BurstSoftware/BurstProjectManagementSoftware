import streamlit as st
from io import BytesIO
import base64
from streamlit_ace import st_ace
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Function to create download PDF link
def create_download_link_pdf(pdf_data, download_filename):
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{download_filename}">Download PDF</a>'
    return href

# Initialize session states
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'text_dict' not in st.session_state:
    st.session_state.text_dict = {}
if 'code_dict' not in st.session_state:
    st.session_state.code_dict = {}
if 'interpreter_dict' not in st.session_state:
    st.session_state.interpreter_dict = {}
if 'terminal_dict' not in st.session_state:
    st.session_state.terminal_dict = {}
if 'requirements_dict' not in st.session_state:
    st.session_state.requirements_dict = {}
if 'code_sections' not in st.session_state:
    st.session_state.code_sections = 1

st.title("Testing Documentation App")

# ====================== VERSION INFORMATION ======================
st.header("Version Information")
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version:", key="app_version_input")
with col2:
    interpreter_version = st.text_input("Interpreter Version:", 
                                      placeholder="e.g., Python 3.9.0", 
                                      key="interpreter_version_input")

if st.button("Save Version Information"):
    if app_version and app_version not in st.session_state.task_list:
        st.session_state.task_list.append(app_version)
        st.session_state.interpreter_dict[app_version] = interpreter_version
        st.session_state.app_version_input = ""
        st.session_state.interpreter_version_input = ""
        st.rerun()

# ====================== REQUIREMENTS ======================
st.header("Project Requirements (requirements.txt)")

selected_version = st.selectbox(
    "Select App Version for editing", 
    options=st.session_state.task_list + ["New Version"] if st.session_state.task_list else ["New Version"],
    key="req_version_select"
)

current_version = app_version if selected_version == "New Version" else selected_version

if current_version:
    if current_version in st.session_state.requirements_dict and st.session_state.requirements_dict[current_version].strip():
        with st.expander("Current saved requirements.txt", expanded=False):
            st.code(st.session_state.requirements_dict[current_version], language="text")

    requirements_text = st.text_area(
        "Enter or update requirements.txt content:",
        height=150,
        placeholder="numpy==1.24.0\npandas>=2.0.0\nstreamlit==1.28.0\n...",
        key="requirements_input"
    )

    if st.button("Save Requirements"):
        if current_version:
            st.session_state.requirements_dict[current_version] = requirements_text
            st.session_state.requirements_input = ""
            st.success(f"Requirements saved for {current_version}")
            st.rerun()

# ====================== REGRESSION NOTES ======================
st.header("Testing Notes")
regression_notes = st.text_area("Enter Regression Testing Notes:", key="regression_notes_input")

if st.button("Save Regression Testing Notes"):
    if current_version:
        if current_version not in st.session_state.text_dict:
            st.session_state.text_dict[current_version] = []
        st.session_state.text_dict[current_version].append(f"Regression Notes: {regression_notes}")
        st.session_state.regression_notes_input = ""
        st.success("Regression notes saved!")
        st.rerun()

# ====================== TERMINAL OUTPUT ======================
st.header("Terminal Output")
terminal_output = st.text_area(
    "Enter Terminal Output:",
    height=200,
    placeholder="Paste any relevant terminal output, error messages, or command results here",
    key="terminal_input"
)

if st.button("Save Terminal Output"):
    if current_version:
        if current_version not in st.session_state.terminal_dict:
            st.session_state.terminal_dict[current_version] = []
        st.session_state.terminal_dict[current_version].append(terminal_output)
        st.session_state.terminal_input = ""
        st.success("Terminal output saved!")
        st.rerun()

# ====================== CODE SECTIONS ======================
st.header("Code Input Sections")

if st.button("Add Another Code Section"):
    st.session_state.code_sections += 1
    st.rerun()

for i in range(st.session_state.code_sections):
    st.subheader(f"Code Section {i+1}")
    code = st_ace(
        language="python",
        theme="monokai",
        key=f"ace-editor-{i}",
        placeholder="Enter your code here..."
    )
    
    if st.button(f"Save Code Section {i+1}", key=f"save_code_{i}"):
        if current_version:
            if current_version not in st.session_state.code_dict:
                st.session_state.code_dict[current_version] = []
            st.session_state.code_dict[current_version].append(code)
            st.success(f"Code Section {i+1} saved!")
            if i + 1 == st.session_state.code_sections:
                st.session_state.code_sections += 1
            st.rerun()

# ====================== SAVED ITEMS DISPLAY ======================
st.write("## Saved Items")
for ver in st.session_state.task_list:
    st.write(f"### App Version: {ver}")
    if ver in st.session_state.interpreter_dict:
        st.write(f"**Interpreter Version:** {st.session_state.interpreter_dict[ver]}")
    
    if ver in st.session_state.requirements_dict:
        reqs = st.session_state.requirements_dict[ver]
        if reqs and reqs.strip():
            st.write("#### Requirements:")
            st.code(reqs, language="text")
    
    if ver in st.session_state.text_dict:
        st.write("#### Notes:")
        for text in st.session_state.text_dict[ver]:
            st.write(f"- {text}")
    
    if ver in st.session_state.terminal_dict:
        st.write("#### Terminal Outputs:")
        for idx, out in enumerate(st.session_state.terminal_dict[ver]):
            with st.expander(f"Terminal Output {idx+1}"):
                st.code(out, language="bash")
    
    if ver in st.session_state.code_dict:
        st.write("#### Code Sections:")
        for idx, code_snippet in enumerate(st.session_state.code_dict[ver]):
            st.write(f"Code Section {idx+1}:")
            st.code(code_snippet, language="python")

# ====================== PDF GENERATION ======================
if st.button("Generate PDF"):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
    styles = getSampleStyleSheet()
    elements = []

    for ver in st.session_state.task_list:
        elements.append(Paragraph(f"App Version: {ver}", styles['Heading1']))
        if ver in st.session_state.interpreter_dict:
            elements.append(Paragraph(f"Interpreter Version: {st.session_state.interpreter_dict[ver]}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Requirements
        if ver in st.session_state.requirements_dict:
            reqs = st.session_state.requirements_dict[ver]
            if reqs.strip():
                elements.append(Paragraph("Requirements (requirements.txt):", styles['Heading2']))
                style = ParagraphStyle('CodeStyle', parent=styles['Normal'], fontName='Courier', fontSize=9, leading=10)
                elements.append(Preformatted(reqs, style))
                elements.append(Spacer(1, 12))

        # Notes
        if ver in st.session_state.text_dict:
            elements.append(Paragraph("Notes:", styles['Heading2']))
            for t in st.session_state.text_dict[ver]:
                elements.append(Paragraph(f"• {t}", styles['Normal']))
            elements.append(Spacer(1, 12))

        # Terminal
        if ver in st.session_state.terminal_dict:
            elements.append(Paragraph("Terminal Outputs:", styles['Heading2']))
            for i, out in enumerate(st.session_state.terminal_dict[ver]):
                elements.append(Paragraph(f"Terminal Output {i+1}:", styles['Heading3']))
                style = ParagraphStyle('TermStyle', parent=styles['Normal'], fontName='Courier', fontSize=9, leading=10)
                elements.append(Preformatted(out, style))
                elements.append(Spacer(1, 12))

        # Code
        if ver in st.session_state.code_dict:
            elements.append(Paragraph("Code Sections:", styles['Heading2']))
            for i, c in enumerate(st.session_state.code_dict[ver]):
                elements.append(Paragraph(f"Code Section {i+1}:", styles['Heading3']))
                style = ParagraphStyle('CodeStyle', parent=styles['Normal'], fontName='Courier', fontSize=9, leading=10)
                elements.append(Preformatted(c, style))
                elements.append(Spacer(1, 12))

    doc.build(elements)
    pdf_buffer.seek(0)
    st.markdown(create_download_link_pdf(pdf_buffer.read(), "testing_documentation.pdf"), unsafe_allow_html=True)
