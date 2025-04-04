import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime
import traceback
import os
import google.generativeai as genai

LOCAL_ENV = False  # Changed to always False

# Initialize session state
if 'reportlab_instances' not in st.session_state:
    st.session_state.reportlab_instances = []
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = ""
if 'ai_generated_code_list' not in st.session_state:
    st.session_state.ai_generated_code_list = [] # store AI-Generated Code
if 'saved_iterations' not in st.session_state:
    st.session_state.saved_iterations = []

# Main app title
st.title("Development Environment Configurator")

# App configuration inputs
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version", "1.0.0")
    interpreter = st.text_input("Interpreter", "Python 3.9")
with col2:
    ide = st.text_input("IDE/Text Editor", "VS Code")
    framework = st.text_input("Framework", "Streamlit")  # Allow any framework to be entered

# Google AI Studio API Key input
google_api_key = st.text_input("Google AI Studio API Key", type="password")

# ReportLab GUI component
def create_reportlab_gui(index):
    st.subheader(f"Iteration #{index + 1}")  # Changed from ReportLab Instance to Iteration

    # Display hash symbol and input area
    content = st.text_area(
        f"Ideas/Notes (starts with #)",
        value="# ",
        key=f"reportlab_{index}"
    )

    st.info("Please type your ideas/notes.")

    return content

# Add new Iteration instance
if st.button("Add New Iteration"):
    st.session_state.reportlab_instances.append("")

# Display existing Iteration instances
for i in range(len(st.session_state.reportlab_instances)):
    st.session_state.reportlab_instances[i] = create_reportlab_gui(i)

# Generate PDF
def generate_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 50, f"App Version: {app_version}")
    c.drawString(100, height - 70, f"Interpreter: {interpreter}")
    c.drawString(100, height - 90, f"IDE: {ide}")
    c.drawString(100, height - 110, f"Framework: {framework}")

    y_position = height - 150
    for i, content in enumerate(st.session_state.reportlab_instances):
        if y_position < 50:
            c.showPage()
            y_position = height - 50
        c.drawString(100, y_position, f"Iteration #{i + 1}:") # changed here too
        y_position -= 20
        for line in content.split('\n'):
            if y_position < 50:
                c.showPage()
                y_position = height - 50
            c.drawString(120, y_position, line[:80])
            y_position -= 15
        y_position -= 20

    c.save()
    buffer.seek(0)
    return buffer

# Generate codebase for display in the app
def generate_codebase():
    code = ""
    for i, content in enumerate(st.session_state.reportlab_instances):
        # Extract the first line (the app name and version if specified)
        first_line = content.split('\n')[0].strip()
        app_name_version = first_line[1:].strip()  # Remove the initial '#' and leading/trailing spaces

        framework_import = ""
        if framework.lower() == "streamlit":
            framework_import = "import streamlit as st"
        elif framework.lower() == "tkinter":
            framework_import = "import tkinter as tk"
            framework_import += "\nfrom tkinter import ttk" # Optional, but often used
        elif framework.lower() == "pygame":
            framework_import = "import pygame"
        elif framework.lower() == "customtkinter":
            framework_import = "import customtkinter"
        # Add more framework imports here as needed

        code += f"""
# {'#' if app_name_version else ''} {app_name_version if app_name_version else f"Iteration {i+1}"}
# App Configuration (based on user input)
# The configuration below is NOT passed to the AI. It is just for documentation.
VERSION = '{app_version}'
INTERPRETER = '{interpreter}'
IDE = '{ide}'
FRAMEWORK = '{framework}'

{framework_import}

# {app_name_version if app_name_version else "Generated App"}

# Iteration #{i+1}
"""
        for line in content.split('\n')[1:]:
            if line.strip():
                code += f"#st.write('{line.strip()}')\n"  #Commented out for all cases since framework is variable
    return code

# Generate codebase only for the AI.
def generate_codebase_for_ai():
    code = ""
    for i, content in enumerate(st.session_state.reportlab_instances):
        # Extract the first line (the app name and version if specified)
        first_line = content.split('\n')[0].strip()
        app_name_version = first_line[1:].strip()  # Remove the initial '#' and leading/trailing spaces

        framework_import = ""
        if framework.lower() == "streamlit":
            framework_import = "import streamlit as st"
        elif framework.lower() == "tkinter":
            framework_import = "import tkinter as tk"
            framework_import += "\nfrom tkinter import ttk" # Optional, but often used
        elif framework.lower() == "pygame":
            framework_import = "import pygame"
        elif framework.lower() == "customtkinter":
            framework_import = "import customtkinter"
        # Add more framework imports here as needed

        code += f"""
# {'#' if app_name_version else ''} {app_name_version if app_name_version else f"Iteration {i+1}"}

{framework_import}

# {app_name_version if app_name_version else "Generated App"}

# Iteration #{i+1}
"""
        for line in content.split('\n')[1:]:
            if line.strip():
                code += f"#st.write('{line.strip()}')\n" #Commented out for all cases since framework is variable
    return code

def generate_code_with_ai(api_key, codebase, interpreter, framework):
    """
    Generates code using Google AI Studio based on the provided codebase and API key.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"""
        You are a helpful AI assistant that helps to generate python code for applications based on the following codebase,
        and adds implementation details with comments.  The app name and version are defined in the first comment of the codebase.  The code should use {interpreter} and the {framework} framework.  Refer to the feature set with only the term Iteration and the iteration number: (Iteration #1).

        Codebase:
        ```python
        {codebase}
        ```

        Generate the fully implemented code base. Add comments to explain the code.  Make sure the initial comment (app name and version) is preserved. Do not include VERSION, INTERPRETER, IDE, or FRAMEWORK in the code base since the user already specified this in the config. Ensure that the import statement matches the specified framework.
        """

        response = model.generate_content(prompt)

        return response.text
    except Exception as e:
        st.error(f"Error generating code with AI: {str(e)}")
        return None

# Export to PDF button
if st.button("Export to PDF"):
    if st.session_state.reportlab_instances:
        try:
            pdf_buffer = generate_pdf()
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name=f"app_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF generation failed: {str(e)}")
    else:
        st.warning("Please add at least one iteration first")

# Generate and display codebase
if st.button("Generate Codebase"):
    if st.session_state.reportlab_instances:
        try:
            st.session_state.generated_code = generate_codebase()
            st.subheader("Generated Codebase")
            st.code(st.session_state.generated_code, language="python")  # Display the generated code
        except Exception as e:
            st.error(f"Code generation failed: {str(e)}")
            traceback.print_exc()
    else:
        st.warning("Please add at least one iteration first")

# Function to display AI generated code with a delete button
def display_ai_generated_code(code, index):
    col1, col2 = st.columns([0.8, 0.2])  # Adjust column widths as needed
    with col1:
        st.subheader(f"AI Generated Codebase #{index + 1}")
        st.code(code, language="python")
    with col2:
        if st.button("Delete AI Code", key=f"delete_ai_{index}"):
            del st.session_state.ai_generated_code_list[index]

            #Renumber the AI Codebase list
            renumber_ai_codebase_list()

            #st.experimental_rerun() #This will fail if st.experimental_rerun is not allowed
            st.rerun()

#Renumber the AI Codebase list when an item is deleted
def renumber_ai_codebase_list():
    #No need to renumber the list if there are no generated AI Codebase
    if not st.session_state.ai_generated_code_list:
        return

    temp_list = st.session_state.ai_generated_code_list

    st.session_state.ai_generated_code_list = []

    for index, code in enumerate(temp_list):
         st.session_state.ai_generated_code_list.append(code)

# AI Code Generation Button
if st.button("Generate Code with AI"):
    if st.session_state.reportlab_instances and google_api_key:
        try:
            codebase_for_ai = generate_codebase_for_ai()
            ai_generated_code = generate_code_with_ai(google_api_key, codebase_for_ai, interpreter, framework)
            if ai_generated_code:

                #Save the current iteriation
                current_iteration = {
                    "App Version": app_version,
                    "Interpreter": interpreter,
                    "IDE/Text Editor": ide,
                    "Framework": framework,
                    "Iterations": st.session_state.reportlab_instances
                }

                st.session_state.saved_iterations.append(current_iteration)

                #Clear the current itieration for the app
                st.session_state.reportlab_instances = []
                app_version = ""
                interpreter = ""
                ide = ""
                framework = ""

                st.session_state.ai_generated_code_list.append(ai_generated_code) # append to AI code list
                #st.experimental_rerun() #This will fail if st.experimental_rerun is not allowed
                st.rerun()
        except Exception as e:
            st.error(f"AI code generation failed: {str(e)}")
            traceback.print_exc()
    else:
        st.warning("Please generate the initial codebase and/or enter API Key first.")

# Display saved iterations in the sidebar
st.sidebar.header("Saved Iterations")
if st.session_state.saved_iterations:
    for i, iteration in enumerate(st.session_state.saved_iterations):
        with st.sidebar.expander(f"Iteration {i+1}"):
            st.write(f"App Version: {iteration['App Version']}")
            st.write(f"Interpreter: {iteration['Interpreter']}")
            st.write(f"IDE/Text Editor: {iteration['IDE/Text Editor']}")
            st.write(f"Framework: {iteration['Framework']}")
            st.write("Iterations")
            for code in iteration['Iterations']:
                 st.code(code, language="python") # Code
else:
    st.sidebar.write("No saved iterations yet.")

# Display all generated code with delete buttons
if st.session_state.ai_generated_code_list:
    for index, code in enumerate(st.session_state.ai_generated_code_list):
       display_ai_generated_code(code, index)
