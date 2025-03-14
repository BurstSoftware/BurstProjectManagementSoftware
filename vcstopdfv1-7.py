import streamlit as st
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import requests
#from streamlit_extras.app_logo import add_logo # Removed
from streamlit_extras.colored_header import colored_header
from streamlit_extras.buy_me_a_coffee import button
from streamlit_option_menu import option_menu
from streamlit_ace import st_ace
import time

# Function to create download PDF link
def create_download_link_pdf(pdf_data, download_filename):
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{download_filename}">Download PDF</a>'
    return href

# Initialize session states (only if not already initialized)
def initialize_session_state():
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
        st.session_state.file_dict = {}
    if 'ai_output_dict' not in st.session_state:
        st.session_state.ai_output_dict = {}

initialize_session_state()
# Streamlit app configurations
st.set_page_config(page_title="CodeDocGen AI", page_icon=":scroll:", layout="wide")

# --- CUSTOM CSS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style/style.css")

# --- LOAD ASSETS ---
#add_logo("images/Seal_of_MIT.svg.png", height=150) # Removed

# Sidebar for navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Project Setup", "Code Analysis", "PDF Generation", "About"],
        icons=['gear', 'code', 'file-pdf', 'info-circle'],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"},
            "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "green"},
        }
    )

# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

button(username="cesarhfernandez")

# --- PROJECT SETUP PAGE ---
if selected == "Project Setup":
    colored_header(
        label="Project Configuration",
        description="Define project details and upload code files.",
        color_name="green-70",
    )

    # API Key Input (Moved to top for prominence)
    gemini_api_key = st.text_input("Enter your Gemini API Key:", type="password")

    col1, col2 = st.columns(2)  # Create two columns for side-by-side input
    with col1:
        app_version = st.text_input("App Version:")
    with col2:
        interpreter_version = st.text_input("Interpreter Version:", placeholder="e.g., Python 3.9.0")

    if st.button("Save Version Information", key="save_version"):
        if app_version and app_version not in st.session_state.task_list:
            st.session_state.task_list.append(app_version)
            st.session_state.interpreter_dict[app_version] = interpreter_version

    if app_version:
        st.subheader("Testing Notes")
        regression_notes = st.text_area("Enter Regression Testing Notes:")
        if st.button("Save Regression Testing Notes", key="save_notes"):
            if app_version not in st.session_state.text_dict:
                st.session_state.text_dict[app_version] = []
            st.session_state.text_dict[app_version].append(f"Regression Notes: {regression_notes}")

        st.subheader("Terminal Output")
        terminal_output = st.text_area(
            "Enter Terminal Output:",
            height=200,
            help="Paste any relevant terminal output, error messages, or command results here"
        )
        if st.button("Save Terminal Output", key="save_terminal"):
            if app_version not in st.session_state.terminal_dict:
                st.session_state.terminal_dict[app_version] = []
            st.session_state.terminal_dict[app_version].append(terminal_output)

        st.subheader("File Upload")
        uploaded_files = st.file_uploader("Upload your project files", accept_multiple_files=True)

        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_content = uploaded_file.read().decode()

            if app_version not in st.session_state.file_dict:
                st.session_state.file_dict[app_version] = {}

            st.session_state.file_dict[app_version][file_name] = file_content

# --- CODE ANALYSIS PAGE ---
elif selected == "Code Analysis":
    colored_header(
        label="AI-Powered Code Analysis",
        description="Analyze your code with Gemini AI and view the suggested improvements.",
        color_name="blue-70",
    )

    if st.session_state.task_list:
        app_version = st.selectbox("Select App Version for Analysis:", st.session_state.task_list)

        if app_version and app_version in st.session_state.file_dict:
            gemini_api_key = st.text_input("Gemini API Key:", type="password")
            ai_prompt = st.text_area("Enter Prompt for Gemini AI (e.g., 'Optimize this code for performance'):", height=100)

            if st.button("Run AI Code Analysis"):
                if gemini_api_key:
                    st.session_state.ai_output_dict[app_version] = {}
                    with st.spinner("Analyzing code with AI..."):
                        for file_name, file_content in st.session_state.file_dict[app_version].items():
                            prompt = f"Given the following code:\n\n{file_content}\n\n{ai_prompt}"
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
                            data = {
                                "contents": [{
                                    "parts": [{"text": prompt}]
                                }]
                            }
                            try:
                                response = requests.post(url, json=data)
                                response.raise_for_status()
                                ai_response = response.json()
                                generated_text = ai_response["candidates"][0]["content"]["parts"][0]["text"]
                                st.session_state.ai_output_dict[app_version][file_name] = generated_text
                            except requests.exceptions.RequestException as e:
                                st.error(f"Error calling Gemini API: {e}")
                                st.session_state.ai_output_dict[app_version][file_name] = "Error: Could not connect to the API."
                            except (KeyError, IndexError) as e:
                                st.error(f"Error parsing Gemini API response: {e}. Full response: {response.text}")
                                st.session_state.ai_output_dict[app_version][file_name] = "Error: Could not parse the API response."
                    st.success("Code analysis complete!")

            st.subheader("AI Code Suggestions")
            if app_version in st.session_state.ai_output_dict:
                for file_name, ai_output in st.session_state.ai_output_dict[app_version].items():
                    with st.expander(f"AI Suggestion for {file_name}"):
                        st.code(ai_output, language="python")  # Detect language dynamically if possible
        else:
            st.warning("No files uploaded for the selected App Version. Please upload files in the Project Setup page.")
    else:
        st.info("Please set up your project details and upload files in the 'Project Setup' page first.")

# --- PDF GENERATION PAGE ---
elif selected == "PDF Generation":
    colored_header(
        label="Generate Documentation PDF",
        description="Generate a comprehensive PDF report of your project, including code analysis results.",
        color_name="orange-70",
    )

    if st.button("Generate PDF"):
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
        styles = getSampleStyleSheet()
        pdf_elements = []

        with st.spinner("Generating PDF..."):  # Show spinner while generating PDF
            for app_version in st.session_state.task_list:
                pdf_elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))

                if app_version in st.session_state.interpreter_dict:
                    pdf_elements.append(Paragraph(f"Interpreter Version: {st.session_state.interpreter_dict[app_version]}", styles['Normal']))
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
                        code_paragraph_style = ParagraphStyle(name='TerminalStyle', fontName='Courier', fontSize=8, leftIndent=10, rightIndent=10, leading=8, wordWrap='CJK')
                        terminal_paragraph = Preformatted(output, code_paragraph_style, maxLineLength=65)
                        pdf_elements.append(terminal_paragraph)
                        pdf_elements.append(Spacer(1, 10))

                if app_version in st.session_state.file_dict:
                    pdf_elements.append(Paragraph("Uploaded Files:", styles['Heading2']))
                    for file_name, file_content in st.session_state.file_dict[app_version].items():
                        pdf_elements.append(Paragraph(f"File: {file_name}", styles['Heading3']))
                        code_paragraph_style = ParagraphStyle(name='CodeStyle', fontName='Courier', fontSize=8, leftIndent=10, rightIndent=10, leading=8, wordWrap='CJK')
                        code_paragraph = Preformatted(file_content, code_paragraph_style, maxLineLength=65)
                        pdf_elements.append(code_paragraph)
                        pdf_elements.append(Spacer(1, 10))

                if app_version in st.session_state.ai_output_dict:
                    pdf_elements.append(Paragraph("AI Code Suggestions:", styles['Heading2']))
                    for file_name, ai_output in st.session_state.ai_output_dict[app_version].items():
                        pdf_elements.append(Paragraph(f"AI Suggestion for {file_name}:", styles['Heading3']))
                        code_paragraph_style = ParagraphStyle(name='CodeStyle', fontName='Courier', fontSize=8, leftIndent=10, rightIndent=10, leading=8, wordWrap='CJK')
                        code_paragraph = Preformatted(ai_output, code_paragraph_style, maxLineLength=65)
                        pdf_elements.append(code_paragraph)
                        pdf_elements.append(Spacer(1, 10))

            doc.build(pdf_elements)
            pdf_buffer.seek(0)
            pdf_data = pdf_buffer.read()

        st.markdown(create_download_link_pdf(pdf_data, "documentation.pdf"), unsafe_allow_html=True)
        st.success("PDF generated successfully!")

# --- ABOUT PAGE ---
elif selected == "About":
    colored_header(
        label="About CodeDocGen AI",
        description="Learn more about this tool and its capabilities.",
        color_name="gray-70",
    )

    st.markdown(
        """
        ## CodeDocGen AI: Your AI-Powered Documentation Assistant

        This application leverages the power of AI to streamline the documentation process for your software projects.  It allows you to:

        - Easily configure project settings and upload code files.
        - Analyze your code using the Gemini AI model to identify potential improvements.
        - Generate a comprehensive PDF report that includes your code, AI analysis results, and other project details.

        ### Key Features:

        - **AI-Powered Code Analysis:**  Utilizes the Gemini AI model to provide intelligent code suggestions and identify potential issues.
        - **Comprehensive Documentation:**  Generates a detailed PDF report that includes your code, AI analysis results, testing notes, and terminal outputs.
        - **User-Friendly Interface:**  A clean and intuitive interface makes it easy to configure your project and generate documentation.
        - **Streamlined Workflow:**  Simplifies the documentation process, saving you time and effort.

        ### How to Use:

        1. **Project Setup:**  Enter your project details (App Version, Interpreter Version) and upload your code files in the "Project Setup" section.
        2. **Code Analysis:**  Navigate to the "Code Analysis" section, select your app version, enter your Gemini API key, and provide a prompt for the AI to analyze your code.
        3. **PDF Generation:**  Go to the "PDF Generation" section and click the "Generate PDF" button to create your documentation report.

        ### Credits:

        - Built with Streamlit: https://streamlit.io/
        - Uses the Gemini AI API from Google AI Studio: https://makersuite.google.com/app/apikey
        - Icons from Font Awesome: https://fontawesome.com/
        - Additional styling and components from Streamlit Extras.

        ### Contact:

        - If you have any questions or feedback, please contact [Your Name/Organization] at [Your Email Address].

        Enjoy using CodeDocGen AI!
        """
    )
