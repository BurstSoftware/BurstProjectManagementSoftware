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

# Main app title
st.title("Development Environment Configurator")

# App configuration inputs
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version", "1.0.0")
    interpreter = st.text_input("Interpreter", "Python 3.9")
with col2:
    ide = st.text_input("IDE/Text Editor", "VS Code")
    framework = st.text_input("Framework", "Streamlit")

# Google AI Studio API Key input
google_api_key = st.text_input("Google AI Studio API Key", type="password")

# ReportLab GUI component
def create_reportlab_gui(index):
    st.subheader(f"ReportLab Instance #{index + 1}")

    # Display hash symbol and input area
    content = st.text_area(
        f"Ideas/Notes (starts with #)",
        value="# ",
        key=f"reportlab_{index}"
    )

    st.info("Please type your ideas/notes.")

    return content

# Add new ReportLab instance
if st.button("Add New ReportLab Instance"):
    st.session_state.reportlab_instances.append("")

# Display existing ReportLab instances
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
        c.drawString(100, y_position, f"Instance #{i + 1}:")
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

# Generate codebase
def generate_codebase():
    code = ""
    for i, content in enumerate(st.session_state.reportlab_instances):
        # Extract the first line (the app name and version if specified)
        first_line = content.split('\n')[0].strip()
        app_name_version = first_line[1:].strip()  # Remove the initial '#' and leading/trailing spaces

        code += f"""
# {'#' if app_name_version else ''} {app_name_version if app_name_version else f"ReportLab Instance {i+1}"}
import streamlit as st

# App Configuration (based on user input)
VERSION = '{app_version}'
INTERPRETER = '{interpreter}'
IDE = '{ide}'
FRAMEWORK = '{framework}'

st.title('{app_name_version if app_name_version else "Generated App"}')

# Features from ReportLab instance #{i+1}
"""
        for line in content.split('\n')[1:]:
            if line.strip():
                code += f"st.write('{line.strip()}')\n"
    return code

def generate_code_with_ai(api_key, codebase):
    """
    Generates code using Google AI Studio based on the provided codebase and API key.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"""
        You are a helpful AI assistant that helps to generate python code for streamlit applications based on the following codebase,
        and adds implementation details with comments.  The app name and version are defined in the first comment of the codebase. Use the specified python version and framework.

        Codebase:
        ```python
        {codebase}
        ```

        Generate the fully implemented code base. Use streamlit to show the results and UI.
        Add comments to explain the code.  Make sure the initial comment (app name and version) is preserved.
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
        st.warning("Please add at least one ReportLab instance first")

# Generate and display codebase
if st.button("Generate Codebase"):
    if st.session_state.reportlab_instances:
        try:
            st.session_state.generated_code = generate_codebase()
            st.subheader("Generated Codebase")
            st.code(st.session_state.generated_code, language="python")
        except Exception as e:
            st.error(f"Code generation failed: {str(e)}")
            traceback.print_exc()
    else:
        st.warning("Please add at least one ReportLab instance first")

# AI Code Generation Button
if st.button("Generate Code with AI"):
    if st.session_state.generated_code and google_api_key:
        try:
            ai_generated_code = generate_code_with_ai(google_api_key, st.session_state.generated_code)
            if ai_generated_code:
                st.subheader("AI Generated Codebase")
                st.code(ai_generated_code, language="python")

                # Add AI-generated code as a new ReportLab instance
                st.session_state.reportlab_instances.append(f"# AI Generated Codebase\n{ai_generated_code}")
                st.success("AI-generated codebase added as a new ReportLab instance.")
        except Exception as e:
            st.error(f"AI code generation failed: {str(e)}")
            traceback.print_exc()
    elif not st.session_state.generated_code:
        st.warning("Please generate the initial codebase first.")
    elif not google_api_key:
        st.warning("Please enter your Google AI Studio API Key.")

# Instructions
st.sidebar.header("Instructions")
st.sidebar.write("""
1. Enter app configuration details
2. Input Google AI Studio API Key (optional)
3. Add ReportLab instances using the button
4. In each instance, the *first* line (starting with #) will be used as the application name and version.  If no first line is provided, it will default to ReportLab Instance #.
5. Type ideas (following the first line).
6. Generate the initial codebase.
7. Click "Generate Code with AI" to enhance the codebase using Google AI Studio.
8. Export to PDF when ready
""")
