import streamlit as st
from io import BytesIO
import base64
from streamlit_ace import st_ace
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import google.generativeai as genai
import json

# Function to create download PDF link
def create_download_link_pdf(pdf_data, download_filename):
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{download_filename}">Download PDF</a>'
    return href

# Function to get saved items as context
def get_saved_items_context():
    context = {}
    for app_version in st.session_state.task_list:
        version_data = {}
        if app_version in st.session_state.interpreter_dict:
            version_data["interpreter_version"] = st.session_state.interpreter_dict[app_version]
        if app_version in st.session_state.text_dict:
            version_data["notes"] = st.session_state.text_dict[app_version]
        if app_version in st.session_state.terminal_dict:
            version_data["terminal_outputs"] = st.session_state.terminal_dict[app_version]
        if app_version in st.session_state.code_dict:
            version_data["code_sections"] = st.session_state.code_dict[app_version]
        context[app_version] = version_data
    return json.dumps(context, indent=2)

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
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""
if 'gemini_response' not in st.session_state:
    st.session_state.gemini_response = ""

# Main app layout
st.title("Testing Documentation App")

# Sidebar for Gemini AI Configuration
with st.sidebar:
    st.header("Gemini AI Configuration")
    gemini_api_key = st.text_input("Enter Gemini AI API Key:", type="password", key="gemini_key")
    if st.button("Save API Key"):
        st.session_state.gemini_api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        st.success("API Key saved successfully!")
    
    if st.session_state.gemini_api_key:
        st.subheader("Gemini AI Query")
        gemini_query = st.text_area("Enter your query:", key="gemini_query")
        include_context = st.checkbox("Include Saved Items as context")
        
        if st.button("Submit to Gemini AI"):
            try:
                model = genai.GenerativeModel('gemini-pro')
                query_content = gemini_query
                if include_context:
                    context = get_saved_items_context()
                    query_content = f"Context:\n{context}\n\nQuery:\n{gemini_query}"
                response = model.generate_content(query_content)
                st.session_state.gemini_response = response.text
                st.write("Gemini AI Response:")
                st.write(st.session_state.gemini_response)
            except Exception as e:
                st.error(f"Error calling Gemini AI: {str(e)}")

# Version Input Section
st.header("Version Information")
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version:")
with col2:
    interpreter_version = st.text_input("Interpreter Version:", placeholder="e.g., Python 3.10.11")

if st.button("Save Version Information"):
    if app_version and app_version not in st.session_state.task_list:
        st.session_state.task_list.append(app_version)
        st.session_state.interpreter_dict[app_version] = interpreter_version

if app_version:
    # Default inputs
    st.header("Testing Notes")
    regression_notes = st.text_area("Enter Regression Testing Notes:")
    if st.button("Save Regression Testing Notes"):
        if app_version not in st.session_state.text_dict:
            st.session_state.text_dict[app_version] = []
        st.session_state.text_dict[app_version].append(f"Regression Notes: {regression_notes}")

    # Terminal Output Section
    st.header("Terminal Output")
    terminal_output = st.text_area(
        "Enter Terminal Output:",
        height=200,
        help="Paste any relevant terminal output, error messages, or command results here"
    )
    if st.button("Save Terminal Output"):
        if app_version not in st.session_state.terminal_dict:
            st.session_state.terminal_dict[app_version] = []
        st.session_state.terminal_dict[app_version].append(terminal_output)

    # Multiple code editors
    st.header("Code Input Sections")
    if 'code_sections' not in st.session_state:
        st.session_state.code_sections = 1

    if st.button("Add Another Code Section"):
        st.session_state.code_sections += 1

    for i in range(st.session_state.code_sections):
        st.subheader(f"Code Section {i+1}")
        code = st_ace(
            language="python",
            theme="monokai",
            key=f"ace-editor-{i}",
            placeholder="Enter your code here..."
        )
        if st.button(f"Save Code Section {i+1}"):
            if app_version not in st.session_state.code_dict:
                st.session_state.code_dict[app_version] = []
            st.session_state.code_dict[app_version].append(code)

# Display saved items
st.write("## Saved Items")
for app_version in st.session_state.task_list:
    st.write(f"### App Version: {app_version}")
    
    if app_version in st.session_state.interpreter_dict:
        st.write(f"**Interpreter Version:** {st.session_state.interpreter_dict[app_version]}")

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

# Generate PDF
if st.button("Generate PDF"):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
    styles = getSampleStyleSheet()
    pdf_elements = []

    # Add Gemini AI Section to PDF
    if st.session_state.gemini_api_key:
        pdf_elements.append(Paragraph("Gemini AI Configuration", styles['Heading1']))
        pdf_elements.append(Paragraph("API Key: [REDACTED]", styles['Normal']))
        if st.session_state.gemini_response:
            pdf_elements.append(Paragraph("Gemini AI Response:", styles['Heading2']))
            response_style = ParagraphStyle(
                name='GeminiStyle',
                fontName='Courier',
                fontSize=8,
                leftIndent=10,
                rightIndent=10,
                leading=8,
                wordWrap='CJK'
            )
            pdf_elements.append(Preformatted(st.session_state.gemini_response, response_style, maxLineLength=65))
        pdf_elements.append(Spacer(1, 20))

    # Existing PDF generation logic
    for app_version in st.session_state.task_list:
        pdf_elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))
        
        if app_version in st.session_state.interpreter_dict:
            pdf_elements.append(Paragraph(
                f"Interpreter Version: {st.session_state.interpreter_dict[app_version]}",
                styles['Normal']
            ))
            pdf_elements.append(Spacer(1, 10))

        if app_version in st.session_state.text_dict:
            pdf_elements.append(Paragraph("Notes:", styles['Heading2']))
            for text in st.session_state.text_dict[app_version]:
                pdf_elements.append(Paragraph(f"- {text}", styles['Normal']))
            pdf_elements.append(Spacer(1, 10))

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

    doc.build(pdf_elements)
    pdf_buffer.seek(0)
    pdf_data = pdf_buffer.read()
    st.markdown(create_download_link_pdf(pdf_data, "documentation.pdf"), unsafe_allow_html=True)
