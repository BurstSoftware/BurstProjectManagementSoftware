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

st.title("Testing Documentation App")

# Version Input Section
st.header("Version Information")
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version:", key="app_version_input")
with col2:
    interpreter_version = st.text_input("Interpreter Version:", placeholder="e.g., Python 3.9.0", key="interpreter_version_input")

if st.button("Save Version Information"):
    if app_version and app_version not in st.session_state.task_list:
        st.session_state.task_list.append(app_version)
        st.session_state.interpreter_dict[app_version] = interpreter_version
        # Clear inputs after save
        st.session_state.app_version_input = ""
        st.session_state.interpreter_version_input = ""
        st.rerun()

# Project Requirements Section
st.header("Project Requirements (requirements.txt)")
if 'current_app_version' not in st.session_state:
    st.session_state.current_app_version = None

selected_version = st.selectbox("Select App Version for Requirements", 
                               options=st.session_state.task_list + ["New Version"] if st.session_state.task_list else ["New Version"],
                               key="req_version_select")

if selected_version == "New Version":
    current_version = app_version if app_version else "Unnamed"
else:
    current_version = selected_version

if current_version:
    st.session_state.current_app_version = current_version
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
            # Clear input after save
            st.session_state.requirements_input = ""
            st.success(f"Requirements saved for {current_version}")
            st.rerun()

# Testing Notes
st.header("Testing Notes")
regression_notes = st.text_area("Enter Regression Testing Notes:", key="regression_notes_input")

if st.button("Save Regression Testing Notes"):
    if current_version:
        if current_version not in st.session_state.text_dict:
            st.session_state.text_dict[current_version] = []
        st.session_state.text_dict[current_version].append(f"Regression Notes: {regression_notes}")
        # Clear input
        st.session_state.regression_notes_input = ""
        st.success("Regression notes saved!")
        st.rerun()

# Terminal Output Section
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
        # Clear input
        st.session_state.terminal_input = ""
        st.success("Terminal output saved!")
        st.rerun()

# Multiple code editors
st.header("Code Input Sections")

if st.button("Add Another Code Section"):
    st.session_state.code_sections += 1
    st.rerun()

for i in range(st.session_state.code_sections):
    st.subheader(f"Code Section {i+1}")
    code_key = f"ace-editor-{i}"
    code = st_ace(
        language="python",
        theme="monokai",
        key=code_key,
        placeholder="Enter your code here..."
    )
    
    if st.button(f"Save Code Section {i+1}", key=f"save_code_{i}"):
        if current_version:
            if current_version not in st.session_state.code_dict:
                st.session_state.code_dict[current_version] = []
            st.session_state.code_dict[current_version].append(code)
            # Clear the editor by forcing rerun (Streamlit ACE handles via key)
            st.success(f"Code Section {i+1} saved!")
            # Optionally increment sections
            if i + 1 == st.session_state.code_sections:
                st.session_state.code_sections += 1
            st.rerun()

# Display saved items
st.write("## Saved Items")
for app_version in st.session_state.task_list:
    st.write(f"### App Version: {app_version}")
    # Display interpreter version
    if app_version in st.session_state.interpreter_dict:
        st.write(f"**Interpreter Version:** {st.session_state.interpreter_dict[app_version]}")
    
    # Display requirements
    if app_version in st.session_state.requirements_dict:
        reqs_content = st.session_state.requirements_dict[app_version]
        if reqs_content and reqs_content.strip():
            st.write("#### Requirements (requirements.txt):")
            st.code(reqs_content, language="text")
    
    # Display text inputs
    if app_version in st.session_state.text_dict:
        st.write("#### Notes:")
        for text in st.session_state.text_dict[app_version]:
            st.write(f"- {text}")
    
    # Display terminal outputs
    if app_version in st.session_state.terminal_dict:
        st.write("#### Terminal Outputs:")
        for i, output in enumerate(st.session_state.terminal_dict[app_version]):
            with st.expander(f"Terminal Output {i+1}"):
                st.code(output, language="bash")
    
    # Display code sections
    if app_version in st.session_state.code_dict:
        st.write("#### Code Sections:")
        for i, code in enumerate(st.session_state.code_dict[app_version]):
            st.write(f"Code Section {i+1}:")
            st.code(code, language="python")

# Generate PDF
if st.button("Generate PDF"):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
    styles = getSampleStyleSheet()
    pdf_elements = []
    
    for app_version in st.session_state.task_list:
        pdf_elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))
        
        # Add interpreter version
        if app_version in st.session_state.interpreter_dict:
            pdf_elements.append(Paragraph(
                f"Interpreter Version: {st.session_state.interpreter_dict[app_version]}",
                styles['Normal']
            ))
        pdf_elements.append(Spacer(1, 10))
        
        # Add requirements content
        if app_version in st.session_state.requirements_dict:
            reqs_content = st.session_state.requirements_dict[app_version]
            if reqs_content and reqs_content.strip():
                pdf_elements.append(Paragraph("Requirements (requirements.txt):", styles['Heading2']))
                code_paragraph_style = ParagraphStyle(
                    name='RequirementsStyle',
                    fontName='Courier',
                    fontSize=8,
                    leftIndent=10,
                    rightIndent=10,
                    leading=8,
                    wordWrap='CJK'
                )
                req_paragraph = Preformatted(reqs_content, code_paragraph_style, maxLineLength=65)
                pdf_elements.append(req_paragraph)
                pdf_elements.append(Spacer(1, 10))
        
        # Add text content
        if app_version in st.session_state.text_dict:
            pdf_elements.append(Paragraph("Notes:", styles['Heading2']))
            for text in st.session_state.text_dict[app_version]:
                pdf_elements.append(Paragraph(f"- {text}", styles['Normal']))
            pdf_elements.append(Spacer(1, 10))
        
        # Add terminal output content
        if app_version in st.session_state.terminal_dict:
            pdf_elements.append(Paragraph("Terminal Outputs:", styles['Heading2']))
            for i, output in enumerate(st.session_state.terminal_dict[app_version]):
                pdf_elements.append(Paragraph(f"Terminal Output {i+1}:", styles['Heading3']))
                code_paragraph_style = ParagraphStyle(
                    name='TerminalStyle',
                    fontName='Courier',
                    fontSize=8,
                    leftIndent=10,
                    rightIndent=10,
                    leading=8,
                    wordWrap='CJK'
                )
                terminal_paragraph = Preformatted(output, code_paragraph_style, maxLineLength=65)
                pdf_elements.append(terminal_paragraph)
                pdf_elements.append(Spacer(1, 10))
        
        # Add code content
        if app_version in st.session_state.code_dict:
            pdf_elements.append(Paragraph("Code Sections:", styles['Heading2']))
            for i, code in enumerate(st.session_state.code_dict[app_version]):
                pdf_elements.append(Paragraph(f"Code Section {i+1}:", styles['Heading3']))
                code_paragraph_style = ParagraphStyle(
                    name='CodeStyle',
                    fontName='Courier',
                    fontSize=8,
                    leftIndent=10,
                    rightIndent=10,
                    leading=8,
                    wordWrap='CJK'
                )
                code_paragraph = Preformatted(code, code_paragraph_style, maxLineLength=65)
                pdf_elements.append(code_paragraph)
                pdf_elements.append(Spacer(1, 10))
    
    # Build the PDF document
    doc.build(pdf_elements)
    pdf_buffer.seek(0)
    pdf_data = pdf_buffer.read()
    st.markdown(create_download_link_pdf(pdf_data, "documentation.pdf"), unsafe_allow_html=True)
