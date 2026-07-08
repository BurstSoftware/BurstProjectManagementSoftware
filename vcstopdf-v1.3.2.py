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
if 'saved_code_keys' not in st.session_state:
    st.session_state.saved_code_keys = set()

# Initialize input keys to prevent StreamlitAPIException
for key in ["app_version_input", "interpreter_version_input", "requirements_input", 
            "regression_notes_input", "terminal_input"]:
    if key not in st.session_state:
        st.session_state[key] = ""

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
        # Clear inputs
        st.session_state.app_version_input = ""
        st.session_state.interpreter_version_input = ""
        st.rerun()

# ====================== REQUIREMENTS ======================
st.header("Project Requirements (requirements.txt)")

selected_version = st.selectbox(
    "Select App Version", 
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
            # Auto-add next section after saving the last one
            if i + 1 == st.session_state.code_sections:
                st.session_state.code_sections += 1
            st.rerun()

# ====================== SAVED ITEMS ======================
st.write("## Saved Items")
for app_version in st.session_state.task_list:
    st.write(f"### App Version: {app_version}")
    
    if app_version in st.session_state.interpreter_dict:
        st.write(f"**Interpreter Version:** {st.session_state.interpreter_dict[app_version]}")
    
    if app_version in st.session_state.requirements_dict:
        reqs = st.session_state.requirements_dict[app_version]
        if reqs.strip():
            st.write("#### Requirements (requirements.txt):")
            st.code(reqs, language="text")
    
    if app_version in st.session_state.text_dict:
        st.write("#### Notes:")
        for text in st.session_state.text_dict[app_version]:
            st.write(f"- {text}")
    
    if app_version in st.session_state.terminal_dict:
        st.write("#### Terminal Outputs:")
        for i, output in enumerate(st.session_state.terminal_dict[app_version]):
            with st.expander(f"Terminal Output {i+1}"):
                st.code(output, language="bash")
    
    if app_version in st.session_state.code_dict:
        st.write("#### Code Sections:")
        for i, code in enumerate(st.session_state.code_dict[app_version]):
            st.write(f"Code Section {i+1}:")
            st.code(code, language="python")

# ====================== GENERATE PDF ======================
if st.button("Generate PDF"):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
    styles = getSampleStyleSheet()
    pdf_elements = []
    
    for app_version in st.session_state.task_list:
        pdf_elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))
        
        if app_version in st.session_state.interpreter_dict:
            pdf_elements.append(Paragraph(
                f"Interpreter Version: {st.session_state.interpreter_dict[app_version]}",
                styles['Normal']
            ))
        pdf_elements.append(Spacer(1, 10))
        
        # Requirements
        if app_version in st.session_state.requirements_dict:
            reqs_content = st.session_state.requirements_dict[app_version]
            if reqs_content.strip():
                pdf_elements.append(Paragraph("Requirements (requirements.txt):", styles['Heading2']))
                style = ParagraphStyle('ReqStyle', parent=styles['Normal'], fontName='Courier', fontSize=8, leading=8)
                pdf_elements.append(Preformatted(reqs_content, style, maxLineLength=65))
                pdf_elements.append(Spacer(1, 10))
        
        # Notes, Terminal, Code sections... (same as before)
        # ... (full PDF logic kept from previous version)
        if app_version in st.session_state.text_dict:
            pdf_elements.append(Paragraph("Notes:", styles['Heading2']))
            for text in st.session_state.text_dict[app_version]:
                pdf_elements.append(Paragraph(f"- {text}", styles['Normal']))
            pdf_elements.append(Spacer(1, 10))
        
        if app_version in st.session_state.terminal_dict:
            pdf_elements.append(Paragraph("Terminal Outputs:", styles['Heading2']))
            for i, output in enumerate(st.session_state.terminal_dict[app_version]):
                pdf_elements.append(Paragraph(f"Terminal Output {i+1}:", styles['Heading3']))
                style = ParagraphStyle('TermStyle', parent=styles['Normal'], fontName='Courier', fontSize=8, leading=8)
                pdf_elements.append(Preformatted(output, style, maxLineLength=65))
                pdf_elements.append(Spacer(1, 10))
        
        if app_version in st.session_state.code_dict:
            pdf_elements.append(Paragraph("Code Sections:", styles['Heading2']))
            for i, code in enumerate(st.session_state.code_dict[app_version]):
                pdf_elements.append(Paragraph(f"Code Section {i+1}:", styles['Heading3']))
                style = ParagraphStyle('CodeStyle', parent=styles['Normal'], fontName='Courier', fontSize=8, leading=8)
                pdf_elements.append(Preformatted(code, style, maxLineLength=65))
                pdf_elements.append(Spacer(1, 10))
    
    doc.build(pdf_elements)
    pdf_buffer.seek(0)
    pdf_data = pdf_buffer.read()
    st.markdown(create_download_link_pdf(pdf_data, "documentation.pdf"), unsafe_allow_html=True)
