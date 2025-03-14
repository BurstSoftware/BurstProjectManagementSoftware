import streamlit as st
from io import BytesIO
import base64
from streamlit_ace import st_ace
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import requests  # For making API requests


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
if 'file_dict' not in st.session_state:
    st.session_state.file_dict = {} #store the content of each uploaded file
if 'ai_output_dict' not in st.session_state:
    st.session_state.ai_output_dict = {} #store the AI output for each file

# Main app layout
st.title("Enhanced Testing Documentation App")

# Gemini API Key Input
gemini_api_key = st.text_input("Enter your Gemini API Key:", type="password")

# Version Input Section
st.header("Version Information")
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version:")
with col2:
    interpreter_version = st.text_input("Interpreter Version:", placeholder="e.g., Python 3.9.0")

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

    # File Upload Section
    st.header("File Upload")
    uploaded_files = st.file_uploader("Upload your project files", accept_multiple_files=True)

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        file_content = uploaded_file.read().decode()

        if app_version not in st.session_state.file_dict:
            st.session_state.file_dict[app_version] = {}

        st.session_state.file_dict[app_version][file_name] = file_content

    # Google AI Studio Integration
    st.header("AI Code Modification")
    ai_prompt = st.text_area("Enter Prompt for Gemini AI (e.g., 'Optimize this code for performance'):", height=100)

    if st.button("Run AI Code Analysis"):
        if gemini_api_key:
            if app_version in st.session_state.file_dict:
                st.session_state.ai_output_dict[app_version] = {}  # Init AI output for this version
                for file_name, file_content in st.session_state.file_dict[app_version].items():
                    prompt = f"Given the following code:\n\n{file_content}\n\n{ai_prompt}"

                    # Call Gemini API
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"  # Or whichever model you want to use

                    data = {
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }]
                    }
                    try:
                        response = requests.post(url, json=data)
                        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                        ai_response = response.json()

                        # Extract the generated text from the API response
                        generated_text = ai_response["candidates"][0]["content"]["parts"][0]["text"]
                        st.session_state.ai_output_dict[app_version][file_name] = generated_text
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error calling Gemini API: {e}")
                        st.session_state.ai_output_dict[app_version][file_name] = "Error: Could not connect to the API."
                    except (KeyError, IndexError) as e:
                        st.error(f"Error parsing Gemini API response: {e}. Full response: {response.text}")
                        st.session_state.ai_output_dict[app_version][file_name] = "Error: Could not parse the API response."


    # Display AI Code Suggestions
    st.header("AI Code Suggestions")
    if app_version in st.session_state.ai_output_dict:
        for file_name, ai_output in st.session_state.ai_output_dict[app_version].items():
            st.subheader(f"AI Suggestion for {file_name}")
            st.code(ai_output, language="python") # or whatever language the file is


# Display saved items
st.write("## Saved Items")
for app_version in st.session_state.task_list:
    st.write(f"### App Version: {app_version}")

    # Display interpreter version
    if app_version in st.session_state.interpreter_dict:
        st.write(f"**Interpreter Version:** {st.session_state.interpreter_dict[app_version]}")

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

    # Display uploaded files
    if app_version in st.session_state.file_dict:
        st.write("#### Uploaded Files:")
        for file_name, file_content in st.session_state.file_dict[app_version].items():
            with st.expander(f"File: {file_name}"):
                st.code(file_content, language="python") # or detect language

    # Display AI Output for each file
    if app_version in st.session_state.ai_output_dict:
        st.write("#### AI Code Suggestions:")
        for file_name, ai_output in st.session_state.ai_output_dict[app_version].items():
            with st.expander(f"AI Suggestion for {file_name}"):
                st.code(ai_output, language="python") # or detect language


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

        # Add uploaded file content
        if app_version in st.session_state.file_dict:
            pdf_elements.append(Paragraph("Uploaded Files:", styles['Heading2']))
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

        # Add AI generated output
        if app_version in st.session_state.ai_output_dict:
            pdf_elements.append(Paragraph("AI Code Suggestions:", styles['Heading2']))
            for file_name, ai_output in st.session_state.ai_output_dict[app_version].items():
                pdf_elements.append(Paragraph(f"AI Suggestion for {file_name}:", styles['Heading3']))
                code_paragraph_style = ParagraphStyle(
                    name='CodeStyle',
                    fontName='Courier',
                    fontSize=8,
                    leftIndent=10,
                    rightIndent=10,
                    leading=8,
                    wordWrap='CJK'
                )
                code_paragraph = Preformatted(ai_output, code_paragraph_style, maxLineLength=65)
                pdf_elements.append(code_paragraph)
                pdf_elements.append(Spacer(1, 10))

    # Build the PDF document
    doc.build(pdf_elements)

    # Output the PDF content
    pdf_buffer.seek(0)
    pdf_data = pdf_buffer.read()

    # Create download link
    st.markdown(create_download_link_pdf(pdf_data, "documentation.pdf"), unsafe_allow_html=True)
