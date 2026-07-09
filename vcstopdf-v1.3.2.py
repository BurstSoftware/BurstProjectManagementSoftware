import streamlit as st
from io import BytesIO
import base64
from streamlit_ace import st_ace
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ====================== PDF DOWNLOAD HELPER ======================
def create_download_link_pdf(pdf_data, download_filename):
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{download_filename}">📥 Download PDF</a>'
    return href

# ====================== SESSION STATE ======================
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

# ====================== MAIN APP ======================
st.title("🧪 Testing Documentation App")

# ------------------- Version Information -------------------
st.header("Version Information")
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version:", placeholder="e.g., vcstopdfv132.py")
with col2:
    interpreter_version = st.text_input("Interpreter Version:", placeholder="e.g., Python 3.10.20")

if st.button("Save Version Information", type="primary"):
    if app_version and app_version not in st.session_state.task_list:
        st.session_state.task_list.append(app_version)
        st.session_state.interpreter_dict[app_version] = interpreter_version
        st.success(f"Version {app_version} saved!")
    elif app_version:
        st.warning("This version already exists.")

# ------------------- Content Input (only if version exists) -------------------
if app_version and app_version in st.session_state.task_list:

    # Regression Notes
    st.header("Testing Notes")
    regression_notes = st.text_area("Enter Regression Testing Notes:", height=120)
    if st.button("Save Regression Testing Notes"):
        if app_version not in st.session_state.text_dict:
            st.session_state.text_dict[app_version] = []
        st.session_state.text_dict[app_version].append(regression_notes)
        st.success("Regression notes saved.")

    # requirements.txt
    st.header("requirements.txt")
    st.caption("Enter your project dependencies (one per line)")
    requirements_input = st.text_area(
        "requirements.txt content:",
        height=200,
        placeholder="streamlit\npandas\nnumpy\n...",
        help="Paste or type your requirements.txt content here"
    )
    if st.button("Save requirements.txt"):
        if app_version not in st.session_state.requirements_dict:
            st.session_state.requirements_dict[app_version] = []
        st.session_state.requirements_dict[app_version].append(requirements_input)
        st.success(f"requirements.txt saved for version {app_version}")

    # Terminal Output
    st.header("Terminal Output")
    terminal_output = st.text_area(
        "Enter Terminal Output / Logs / Errors:",
        height=200,
        help="Paste any relevant terminal output here"
    )
    if st.button("Save Terminal Output"):
        if app_version not in st.session_state.terminal_dict:
            st.session_state.terminal_dict[app_version] = []
        st.session_state.terminal_dict[app_version].append(terminal_output)
        st.success("Terminal output saved.")

    # Code Sections
    st.header("Code Input Sections")
    if st.button("➕ Add Another Code Section"):
        st.session_state.code_sections += 1

    for i in range(st.session_state.code_sections):
        st.subheader(f"Code Section {i+1}")
        code = st_ace(
            language="python",
            theme="monokai",
            key=f"ace-editor-{app_version}-{i}",
            placeholder="Enter your code here...",
            height=300
        )
        if st.button(f"Save Code Section {i+1}", key=f"save_code_{i}"):
            if app_version not in st.session_state.code_dict:
                st.session_state.code_dict[app_version] = []
            st.session_state.code_dict[app_version].append(code)
            st.success(f"Code Section {i+1} saved.")

# ====================== DISPLAY SAVED DATA ======================
st.divider()
st.write("## 📋 Saved Documentation")

for ver in st.session_state.task_list:
    with st.expander(f"📌 App Version: {ver}", expanded=True):
        # Interpreter
        if ver in st.session_state.interpreter_dict:
            st.write(f"**Interpreter Version:** {st.session_state.interpreter_dict[ver]}")

        # requirements.txt
        if ver in st.session_state.requirements_dict:
            st.write("#### requirements.txt")
            for i, req in enumerate(st.session_state.requirements_dict[ver]):
                with st.expander(f"requirements.txt {i+1}", expanded=False):
                    st.code(req, language="text")

        # Notes
        if ver in st.session_state.text_dict:
            st.write("#### Regression Testing Notes")
            for note in st.session_state.text_dict[ver]:
                st.info(note)

        # Terminal
        if ver in st.session_state.terminal_dict:
            st.write("#### Terminal Outputs")
            for i, out in enumerate(st.session_state.terminal_dict[ver]):
                with st.expander(f"Terminal Output {i+1}"):
                    st.code(out, language="bash")

        # Code
        if ver in st.session_state.code_dict:
            st.write("#### Code Sections")
            for i, code in enumerate(st.session_state.code_dict[ver]):
                with st.expander(f"Code Section {i+1}", expanded=False):
                    st.code(code, language="python")

# ====================== GENERATE PDF ======================
if st.button("📄 Generate Clean PDF", type="primary"):
    if not st.session_state.task_list:
        st.error("No versions saved yet!")
    else:
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            leftMargin=40,
            rightMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        styles = getSampleStyleSheet()
        elements = []

        for app_version in st.session_state.task_list:
            # App Version Header
            elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))
            elements.append(Spacer(1, 12))

            # Interpreter
            if app_version in st.session_state.interpreter_dict:
                elements.append(Paragraph(
                    f"Interpreter Version: {st.session_state.interpreter_dict[app_version]}",
                    styles['Heading2']
                ))
                elements.append(Spacer(1, 12))

            # requirements.txt
            if app_version in st.session_state.requirements_dict:
                elements.append(Paragraph("requirements.txt", styles['Heading2']))
                elements.append(Spacer(1, 8))
                for i, req in enumerate(st.session_state.requirements_dict[app_version]):
                    if len(st.session_state.requirements_dict[app_version]) > 1:
                        elements.append(Paragraph(f"requirements.txt {i+1}", styles['Heading3']))
                    req_style = ParagraphStyle('ReqStyle', fontName='Courier', fontSize=9, 
                                             leftIndent=12, leading=11, spaceAfter=12)
                    elements.append(Preformatted(req.strip(), req_style, maxLineLength=85))
                    elements.append(Spacer(1, 8))

            # Notes
            if app_version in st.session_state.text_dict:
                elements.append(Paragraph("Regression Testing Notes", styles['Heading2']))
                elements.append(Spacer(1, 8))
                for text in st.session_state.text_dict[app_version]:
                    elements.append(Paragraph(f"• {text}", styles['Normal']))
                elements.append(Spacer(1, 12))

            # Terminal
            if app_version in st.session_state.terminal_dict:
                elements.append(Paragraph("Terminal Outputs", styles['Heading2']))
                elements.append(Spacer(1, 8))
                for i, output in enumerate(st.session_state.terminal_dict[app_version]):
                    if len(st.session_state.terminal_dict[app_version]) > 1:
                        elements.append(Paragraph(f"Terminal Output {i+1}", styles['Heading3']))
                    term_style = ParagraphStyle('TermStyle', fontName='Courier', fontSize=8.5, 
                                              leftIndent=12, leading=10, spaceAfter=12)
                    elements.append(Preformatted(output.strip(), term_style, maxLineLength=80))
                    elements.append(Spacer(1, 8))

            # Code
            if app_version in st.session_state.code_dict:
                elements.append(Paragraph("Code Sections", styles['Heading2']))
                elements.append(Spacer(1, 8))
                for i, code in enumerate(st.session_state.code_dict[app_version]):
                    elements.append(Paragraph(f"Code Section {i+1}", styles['Heading3']))
                    code_style = ParagraphStyle('CodeStyle', fontName='Courier', fontSize=8.5, 
                                              leftIndent=12, leading=10, spaceAfter=12)
                    elements.append(Preformatted(code.strip() if code else "# No code provided", 
                                               code_style, maxLineLength=80))
                    elements.append(Spacer(1, 12))

            # Page break between versions
            if st.session_state.task_list.index(app_version) < len(st.session_state.task_list) - 1:
                elements.append(Spacer(1, 30))

        doc.build(elements)
        pdf_buffer.seek(0)
        pdf_data = pdf_buffer.read()

        st.success("✅ PDF Generated Successfully!")
        st.markdown(
            create_download_link_pdf(pdf_data, f"Testing_Documentation_{app_version}.pdf"),
            unsafe_allow_html=True
        )

st.caption("Built for clean PDF export • Ready for AI ingestion")
