import streamlit as st
from io import BytesIO
import base64
from streamlit_ace import st_ace
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ====================== PREDEFINED PRESETS ======================
PRESETS = {
    "Custom (Paste your own)": {
        "project_type": "Custom Project",
        "python_version": "",
        "requirements": ""
    },
    "Testing Documentation App (Python 3.10.20)": {
        "project_type": "Testing Documentation App",
        "python_version": "Python 3.10.20",
        "requirements": """streamlit==1.32.0
streamlit-ace==0.1.1
reportlab==4.3.1
google-generativeai==0.3.2
streamlit-extras==0.3.5
streamlit-option-menu==0.3.6
speechrecognition==3.10.0
requests>=2.31.0"""
    },
    "Open Job Postings (Python 3.14.6)": {
        "project_type": "Open Job Postings",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0
pandas>=2.2.0
plotly>=6.0.0
openai>=1.35.0"""
    },
    "Business Reality Assessment Dashboard (Python 3.14.6)": {
    "project_type": "Open Job Postings",
    "python_version": "Python 3.14.6",
    "requirements": """streamlit>=1.38.0
pandas>=2.2.0"""
}, 
    "Python Code Snippets (Python 3.10.20)": {
        "project_type": "Python Code Snippets",
        "python_version": "Python 3.10.20",
        "requirements": """streamlit==1.22.0
scikit-learn==1.3.0
pandas==2.0.3
numpy==1.24.3"""
    },
    "Alternative To Polsia (Python 3.14.6)": {
        "project_type": "Alternative To Polsia",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0
openai>=1.0.0"""
    },
    "Thrift Store v1 (Python 3.14.6)": {
        "project_type": "Thrift Store v1",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0
pandas>=2.2.0"""
    },
    "AI Construction Software (Python 3.14.6)": {
        "project_type": "AI Construction Software",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0
pandas>=2.2.0                  # For any future data handling / reports
plotly>=5.24.0"""
    },
    "Burst Agents To JSON (Python 3.14.6)": {
        "project_type": "Burst Agents To JSON",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0
pandas>=2.2.0          # Good to have for future data handling
openpyxl>=3.1.0        # If you want Excel export later"""
    },
    "Prompt Library (Python 3.14.6)": {
        "project_type": "Prompt Library",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0"""
    },
    "Business Metrics Tracker (Python 3.14.6)": {
        "project_type": "Business Metrics Tracker",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0
pandas>=2.0.0"""
    },
    "Godot Guide v1 (Python 3.14.6)": {
        "project_type": "Godot Guide v1",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0"""
    },
    "Grok Build Guide (Python 3.14.6)": {
        "project_type": "Grok Build Guide",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0"""
    },
    "Top Selling Products (Python 3.14.6)": {
        "project_type": "Top Selling Products",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.42
pandas>=2.2
altair>=5.4
numpy>=1.26
pyarrow>=15.0"""
    },
    "C-D-O-Q-v-1 (Python 3.14.6)": {
        "project_type": "C-D-O-Q-v-1",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0
pandas>=2.2.0"""
    },
    "rsr-plus-stations-reporting-tool-v1 (Python 3.14.6)": {
        "project_type": "rsr-plus-stations-reporting-tool-v1",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0
pandas>=2.2.0"""
    },
    ".EML To JSON (Python 3.14.6)": {
        "project_type": ".EML To JSON",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0
pandas>=2.2.0"""
    },
    "Cannabis Business (Python 3.14.6)": {
        "project_type": "Cannabis Business",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit==1.38.0"""
    },
    "Creator Risk Continuum (Python 3.14.6)": {
        "project_type": "Creator Risk Continuum",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0"""
    },
    "Handoff MD Creator Guide (Python 3.14.6)": {
        "project_type": "Handoff MD Creator Guide",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0"""
    },
    "OKR Tool (Python 3.14.6)": {
        "project_type": "OKR Tool",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0
pandas>=2.0.0"""
    },
    "N8N Guide (Python 3.14.6)": {
        "project_type": "N8N Guide",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0
pandas>=2.2.0"""
    },
    "Coding With Ai (Python 3.14.6)": {
        "project_type": "Coding With Ai",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0"""
    },
    "Liner Regession (Python 3.14.6)": {
        "project_type": "Liner Regession",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.35,<2.0
scikit-learn>=1.4,<2.0
pandas>=2.2,<3.0
numpy>=1.26,<3.0
plotly>=5.18.0"""
    },
    "amazon-rsr-plus-associate-tools-v1 (Python 3.14.6)": {
        "project_type": "amazon-rsr-plus-associate-tools-v1",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.42.0"""
    },
    "W-R-D-v1 (Python 3.14.6)": {
        "project_type": "W-R-D-v1",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0"""
    },
    "workplace accountability app (Python 3.14.6)": {
        "project_type": "workplace accountability app",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.45.1
watchdog>=6.0.0
python-dateutil>=2.9.0.post0
tzdata>=2025.2
packaging>=25.0
numpy>=2.2.6
pandas>=2.2.3
altair>=5.5.0
pyarrow>=20.0.0
protobuf>=6.31.0
rich>=14.0.0
requests>=2.32.3
toml>=0.10.2
typing_extensions>=4.13.2"""
    },
    "contradictory-data-driven-environment-v1 (Python 3.14.6)": {
        "project_type": "contradictory-data-driven-environment-v1",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.45.0
altair>=5.3.0
pandas>=2.2.2
numpy>=2.1.0
pyarrow>=16.1.0"""
    },
    "Talk-time-wage-theft-tool (Python 3.14.6)": {
        "project_type": "Talk-time-wage-theft-tool",
        "python_version": "Python 3.14.6",
        "requirements": """streamlit>=1.38.0
pandas>=2.2.0
altair>=5.0.0"""
    }
    # Add more presets here in the future
}
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

# ====================== MAIN APP ======================
st.title("Testing Documentation App")

# Version Information
st.header("Version Information")
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version:")
with col2:
    interpreter_version = st.text_input("Interpreter Version:", placeholder="e.g., Python 3.14.6")

if st.button("Save Version Information"):
    if app_version and app_version not in st.session_state.task_list:
        st.session_state.task_list.append(app_version)
        st.session_state.interpreter_dict[app_version] = interpreter_version

if app_version:
    st.header("Testing Notes")
    regression_notes = st.text_area("Enter Regression Testing Notes:")
    if st.button("Save Regression Testing Notes"):
        if app_version not in st.session_state.text_dict:
            st.session_state.text_dict[app_version] = []
        st.session_state.text_dict[app_version].append(f"Regression Notes: {regression_notes}")

    # ==================== REQUIREMENTS.TXT & PROJECT INFO ====================
    st.header("requirements.txt & Project Info")
    
    preset_choice = st.selectbox(
        "Choose Project Preset:",
        options=list(PRESETS.keys()),
        index=0,
        help="Select a project type or Custom"
    )

    selected = PRESETS[preset_choice]

    st.info(f"**Selected Project Type:** {selected['project_type']}")

    requirements_input = st.text_area(
        "requirements.txt content:",
        value=selected["requirements"],
        height=240,
        placeholder="Edit requirements here if needed...",
    )

    if st.button("Save requirements.txt"):
        if app_version not in st.session_state.requirements_dict:
            st.session_state.requirements_dict[app_version] = []
        
        entry = {
            "project_type": selected["project_type"],
            "python_version": selected["python_version"] or interpreter_version or "Not specified",
            "content": requirements_input
        }
        st.session_state.requirements_dict[app_version].append(entry)
        st.success(f"Saved for {app_version} - {selected['project_type']}")

    # Terminal Output
    st.header("Terminal Output")
    terminal_output = st.text_area("Enter Terminal Output:", height=200)
    if st.button("Save Terminal Output"):
        if app_version not in st.session_state.terminal_dict:
            st.session_state.terminal_dict[app_version] = []
        st.session_state.terminal_dict[app_version].append(terminal_output)

    # Code Sections
    st.header("Code Input Sections")
    if 'code_sections' not in st.session_state:
        st.session_state.code_sections = 1

    if st.button("Add Another Code Section"):
        st.session_state.code_sections += 1

    for i in range(st.session_state.code_sections):
        st.subheader(f"Code Section {i+1}")
        code = st_ace(language="python", theme="monokai", key=f"ace-editor-{i}")
        if st.button(f"Save Code Section {i+1}"):
            if app_version not in st.session_state.code_dict:
                st.session_state.code_dict[app_version] = []
            st.session_state.code_dict[app_version].append(code)

# ====================== DISPLAY SAVED ITEMS ======================
st.write("## Saved Items")
for app_version in st.session_state.task_list:
    st.write(f"### App Version: {app_version}")
    
    if app_version in st.session_state.interpreter_dict:
        st.write(f"**Interpreter Version:** {st.session_state.interpreter_dict[app_version]}")

    if app_version in st.session_state.requirements_dict:
        st.write("#### requirements.txt:")
        for i, req in enumerate(st.session_state.requirements_dict[app_version]):
            with st.expander(f"Entry {i+1} - {req['project_type']}"):
                st.write(f"**Project Type:** {req['project_type']}")
                st.write(f"**Python Version:** {req['python_version']}")
                st.code(req['content'], language="text")

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
            pdf_elements.append(Spacer(1, 12))

        # Requirements Section
        if app_version in st.session_state.requirements_dict:
            pdf_elements.append(Paragraph("requirements.txt:", styles['Heading2']))
            for i, req in enumerate(st.session_state.requirements_dict[app_version]):
                if len(st.session_state.requirements_dict[app_version]) > 1:
                    pdf_elements.append(Paragraph(f"Entry {i+1}:", styles['Heading3']))
                
                pdf_elements.append(Paragraph(f"Project Type: {req['project_type']}", styles['Normal']))
                pdf_elements.append(Paragraph(f"Python Version: {req['python_version']}", styles['Normal']))
                pdf_elements.append(Spacer(1, 8))
                
                req_style = ParagraphStyle(name='ReqStyle', fontName='Courier', fontSize=9,
                                         leftIndent=10, rightIndent=10, leading=11, wordWrap='CJK')
                pdf_elements.append(Preformatted(req['content'], req_style, maxLineLength=70))
                pdf_elements.append(Spacer(1, 12))

        # Notes
        if app_version in st.session_state.text_dict:
            pdf_elements.append(Paragraph("Notes:", styles['Heading2']))
            for text in st.session_state.text_dict[app_version]:
                pdf_elements.append(Paragraph(f"• {text}", styles['Normal']))
            pdf_elements.append(Spacer(1, 12))

        # Terminal Outputs
        if app_version in st.session_state.terminal_dict:
            pdf_elements.append(Paragraph("Terminal Outputs:", styles['Heading2']))
            for i, output in enumerate(st.session_state.terminal_dict[app_version]):
                if len(st.session_state.terminal_dict[app_version]) > 1:
                    pdf_elements.append(Paragraph(f"Output {i+1}:", styles['Heading3']))
                term_style = ParagraphStyle(name='TerminalStyle', fontName='Courier', fontSize=8,
                                          leftIndent=10, rightIndent=10, leading=9, wordWrap='CJK')
                pdf_elements.append(Preformatted(output, term_style, maxLineLength=65))
                pdf_elements.append(Spacer(1, 12))

        # Code Sections
        if app_version in st.session_state.code_dict:
            pdf_elements.append(Paragraph("Code Sections:", styles['Heading2']))
            for i, code in enumerate(st.session_state.code_dict[app_version]):
                if len(st.session_state.code_dict[app_version]) > 1:
                    pdf_elements.append(Paragraph(f"Code Section {i+1}:", styles['Heading3']))
                code_style = ParagraphStyle(name='CodeStyle', fontName='Courier', fontSize=8,
                                          leftIndent=10, rightIndent=10, leading=9, wordWrap='CJK')
                pdf_elements.append(Preformatted(code, code_style, maxLineLength=65))
                pdf_elements.append(Spacer(1, 12))

    doc.build(pdf_elements)
    pdf_buffer.seek(0)
    pdf_data = pdf_buffer.read()
    st.markdown(create_download_link_pdf(pdf_data, "documentation.pdf"), unsafe_allow_html=True)
