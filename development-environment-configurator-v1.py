import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

from datetime import datetime
import traceback


LOCAL_ENV = False # Changed to always False

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
    
    st.info("Voice input is disabled. Please type your ideas/notes.")

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
    code = f"""# Generated App Codebase - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
import streamlit as st

# App Configuration
VERSION = '{app_version}'
INTERPRETER = '{interpreter}'
IDE = '{ide}'
FRAMEWORK = '{framework}'

st.title('Generated App')

# Features from ReportLab instances
"""
    for i, content in enumerate(st.session_state.reportlab_instances):
        code += f"\n# Features from Instance #{i + 1}\n"
        for line in content.split('\n')[1:]:
            if line.strip():
                code += f"st.write('{line.strip()}')\n"
    return code

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
            st.session_state.reportlab_instances.append(f"# Generated Codebase\n{st.session_state.generated_code}")
            st.success("Codebase added as new ReportLab instance")
        except Exception as e:
            st.error(f"Code generation failed: {str(e)}")
    else:
        st.warning("Please add at least one ReportLab instance first")

# Instructions
st.sidebar.header("Instructions")
st.sidebar.write("""
1. Enter app configuration details
2. Input Google AI Studio API Key (optional)
3. Add ReportLab instances using the button
4. Type ideas
5. Export to PDF when ready
6. Generate codebase from your ideas
""")
