"""
STREAMLIT APP - Intelligent SLD Generator
====================================
Web interface for testing SLD generation with custom inputs.
Run: streamlit run app.py
"""

import streamlit as st
from streamlit import session_state as ss
import matplotlib.pyplot as plt
from pathlib import Path
import io
import sys

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sld_renderer import SLDGenerationParams, generate_sld
from config_configurations import BusScheme, get_voltage_profile, VOLTAGE_PROFILES

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Intelligent SLD Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .main {
        max-width: 1400px;
    }
    .title-text {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subtitle-text {
        text-align: center;
        color: #666;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    .section-header {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-top: 20px;
        margin-bottom: 10px;
        font-weight: bold;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# TITLE
# ============================================================================

st.markdown('<p class="title-text">⚡ Intelligent SLD Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Test the system with custom parameters and generate professional SLDs</p>', unsafe_allow_html=True)

st.divider()

# ============================================================================
# SIDEBAR - INPUT PARAMETERS
# ============================================================================

st.sidebar.markdown("## ⚡ SLD Builder")
st.sidebar.caption("Fill the steps below, then press **Generate**.")

with st.sidebar:

    # ---- STEP 1 · SUBSTATION ------------------------------------------
    with st.expander("① Substation", expanded=True):
        substation_name = st.text_input(
            "Substation Name",
            value="",
            help="Leave blank for auto: e.g. 400/220kV Standard Substation"
        )
        title_text = st.text_input(
            "Drawing Title",
            value="Typical Substation Single Line Diagram"
        )

    # ---- STEP 2 · VOLTAGE ---------------------------------------------
    with st.expander("② Voltage Levels", expanded=True):
        single_voltage = st.toggle(
            "Single voltage substation",
            value=False,
            help="Off = dual-voltage (HV bus + LV bus via transformers)"
        )
        c1, c2 = st.columns(2)
        with c1:
            hv_voltage = st.selectbox(
                "HV (kV)",
                options=[11, 33, 66, 110, 132, 220, 400, 765],
                index=6
            )
        with c2:
            if not single_voltage:
                lv_voltage = st.selectbox(
                    "LV (kV)",
                    options=[11, 33, 66, 110, 132, 220, 400],
                    index=2
                )
            else:
                lv_voltage = None
                st.markdown("&nbsp;")

    # ---- STEP 3 · BUS SCHEME ------------------------------------------
    with st.expander("③ Bus Scheme", expanded=True):
        configuration = st.radio(
            "Configuration",
            options=["single_bus", "double_bus_coupler",
                     "double_bus_sectionalizer"],
            format_func=lambda x: {
                "single_bus": "🔌 Single Bus",
                "double_bus_coupler": "🔀 Double Bus + Coupler",
                "double_bus_sectionalizer": "🔀 Double Bus + Sectionalizer"
            }[x],
        )

        sectionalizer_count = 2
        if configuration == "double_bus_sectionalizer":
            sectionalizer_count = st.radio(
                "Sectionalizers",
                options=[1, 2], index=1, horizontal=True,
                help="1 = only BUS-1 split (1A/1B). 2 = both buses split."
            )

        if configuration == "single_bus":
            bus_coupler_count = 0
            st.caption("Single bus — no coupler.")
        elif configuration == "double_bus_coupler":
            bus_coupler_count = 1
            st.caption("Coupler scheme — exactly 1 bus coupler (fixed).")
        else:
            bus_coupler_count = st.radio(
                "Bus Couplers", options=[0, 1, 2], index=2, horizontal=True,
                help="C1 ties left sections, C2 ties right sections."
            )

    # ---- STEP 4 · BAYS ------------------------------------------------
    with st.expander("④ Bays", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            line_bay_count = st.number_input(
                "OHL Line", min_value=0, max_value=20, value=4,
                help="Overhead line bays (gantry termination)")
            reactor_bay_count = st.number_input(
                "Reactor", min_value=0, max_value=10, value=1)
        with c2:
            cable_bay_count = st.number_input(
                "Cable Feeder", min_value=0, max_value=20, value=0,
                help="Line bays with cable sealing-end termination")
            transformer_bay_count = st.number_input(
                "Transformer", min_value=0, max_value=20, value=2)
        total_bays = (line_bay_count + cable_bay_count
                      + transformer_bay_count + reactor_bay_count
                      + bus_coupler_count)
        st.caption(f"Total bays: **{total_bays}**")

    # ---- STEP 5 · RATINGS ---------------------------------------------
    with st.expander("⑤ Ratings"):
        st.markdown("**Busbar**")
        rc1, rc2 = st.columns(2)
        with rc1:
            bus_fault_ka = st.number_input(
                "S/C (kA)", min_value=10, max_value=100, value=63)
        with rc2:
            bus_fault_sec = st.number_input(
                "Duration (Sec)", min_value=1, max_value=5, value=1)

        tx_mva, tx_z, tx_vg = [], [], []
        if transformer_bay_count > 0:
            st.markdown("**Transformers**")
            for i in range(transformer_bay_count):
                st.caption(f"Tr.{i + 1}")
                t1, t2, t3 = st.columns(3)
                with t1:
                    tx_mva.append(st.text_input(
                        "MVA", "500", key=f"tx_mva_{i}"))
                with t2:
                    tx_z.append(st.text_input(
                        "%Z", "12.5", key=f"tx_z_{i}"))
                with t3:
                    tx_vg.append(st.text_input(
                        "Vector", "YNa0d11", key=f"tx_vg_{i}"))

        reactor_mvar = []
        if reactor_bay_count > 0:
            st.markdown("**Reactors**")
            for i in range(reactor_bay_count):
                reactor_mvar.append(st.text_input(
                    f"Reactor-{i + 1} (MVAr)", "80", key=f"re_mvar_{i}"))

    # ---- STEP 6 · BAY NAMES (optional) --------------------------------
    with st.expander("⑥ Bay Names (optional)"):
        line_names, transformer_names, reactor_names = [], [], []
        if line_bay_count > 0:
            st.markdown("**Line Bays**")
            for i in range(line_bay_count):
                nm = st.text_input(f"Line {i+1}", "", key=f"line_bay_{i}")
                if nm:
                    line_names.append(nm)
        if transformer_bay_count > 0:
            st.markdown("**Transformer Bays**")
            for i in range(transformer_bay_count):
                nm = st.text_input(f"Tx {i+1}", "", key=f"tx_bay_{i}")
                if nm:
                    transformer_names.append(nm)
        if reactor_bay_count > 0:
            st.markdown("**Reactor Bays**")
            for i in range(reactor_bay_count):
                nm = st.text_input(f"Reactor {i+1}", "", key=f"reactor_bay_{i}")
                if nm:
                    reactor_names.append(nm)

    # ---- STEP 7 · TITLE BLOCK -----------------------------------------
    with st.expander("⑦ Drawing Details (Title Block)"):
        tb_client = st.text_input("Client", "", key="tb_client")
        tb_project = st.text_input("Project", "", key="tb_project")
        tb_drawn = st.text_input("Drawn By", "", key="tb_drawn")
        tb_drgno = st.text_input("Drawing No.", "", key="tb_drgno")
        tb_rev = st.text_input("Rev", "1", key="tb_rev")

    # ---- Live validation ----------------------------------------------
    if configuration == "double_bus_sectionalizer" and bus_coupler_count > 2:
        st.error("❌ Max TWO bus couplers in sectionalizer scheme.")

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Create tabs
tab1, tab2, tab3 = st.tabs(["📊 Preview", "📥 Download", "📋 Summary"])

with tab1:
    st.markdown("### SLD Preview")

    # Generate button
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        generate_button = st.button(
            "🎨 GENERATE SLD",
            use_container_width=True,
            type="primary"
        )

    if generate_button:
        # Show generating status
        with st.spinner("⚙️ Generating SLD..."):
            try:
                # Create parameters
                auto_name = (
                    f"{int(hv_voltage)}/{int(lv_voltage)}kV Standard Substation"
                    if lv_voltage
                    else f"{int(hv_voltage)}kV Standard Substation"
                )
                import dataclasses as _dc
                _raw = dict(
                    substation_name=substation_name.strip() or auto_name,
                    hv_voltage=float(hv_voltage),
                    lv_voltage=float(lv_voltage) if lv_voltage else None,
                    configuration=configuration,
                    line_bay_count=line_bay_count,
                    cable_bay_count=cable_bay_count,
                    transformer_bay_count=transformer_bay_count,
                    reactor_bay_count=reactor_bay_count,
                    bus_coupler_count=bus_coupler_count,
                    line_names=line_names if 'line_names' in locals() else [],
                    transformer_names=transformer_names if 'transformer_names' in locals() else [],
                    reactor_names=reactor_names if 'reactor_names' in locals() else [],
                    title_text=title_text,
                    bus_fault_ka=float(bus_fault_ka),
                    bus_fault_sec=float(bus_fault_sec),
                    sectionalizer_count=int(sectionalizer_count),
                    client=tb_client,
                    project=tb_project,
                    drawn_by=tb_drawn,
                    drg_no=tb_drgno,
                    rev=tb_rev,
                    tx_mva=tx_mva,
                    tx_z=tx_z,
                    tx_vg=tx_vg,
                    reactor_mvar=reactor_mvar
                )
                _valid = {f.name for f in _dc.fields(SLDGenerationParams)}
                _dropped = [k for k in _raw if k not in _valid]
                if _dropped:
                    st.warning(
                        "⚠️ Deployed engine is older than the UI — ignored "
                        f"inputs: {', '.join(_dropped)}. Upload the latest "
                        "sld_renderer.py to GitHub to enable them.")
                params = SLDGenerationParams(
                    **{k: v for k, v in _raw.items() if k in _valid})

                # Generate SLD
                fig, renderer = generate_sld(params)

                # Store in session state for download
                ss.fig = fig
                ss.renderer = renderer
                ss.params = params

                # Display preview as SVG (VECTOR) — stays sharp at any zoom,
                # exactly like the PDF / CAD output (no pixel blurring).
                import streamlit.components.v1 as components
                svg_buf = io.StringIO()
                fig.savefig(svg_buf, format='svg')
                svg_data = svg_buf.getvalue()
                svg_inline = svg_data[svg_data.find('<svg'):]
                html = (
                    "<div style='width:100%;overflow:auto;border:1px solid "
                    "#ccc;background:#fff;'>"
                    "<style>svg{width:100%;height:auto;}</style>"
                    f"{svg_inline}</div>"
                )
                components.html(html, height=640, scrolling=True)
                st.caption(
                    "🔍 Vector preview (SVG) — zoom stays sharp. "
                    "PDF & DXF downloads are fully vector and CAD-editable."
                )

                # Success message
                st.success("✅ SLD generated successfully!")

                # Show summary
                summary = renderer.get_summary()
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Bays", summary['total_bays'])
                with col2:
                    st.metric("Components", summary['components_drawn'])
                with col3:
                    st.metric("Dual Voltage", "✓" if summary['is_dual_voltage'] else "✗")
                with col4:
                    st.metric("Dual Bus", "✓" if summary['is_dual_bus'] else "✗")

            except Exception as e:
                st.error(f"❌ Error generating SLD: {str(e)}")
                st.code(str(e))

with tab2:
    st.markdown("### Download Outputs")

    if 'renderer' in ss and ss.renderer is not None:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📄 PDF Export")
            st.write("High-resolution PDF for printing and sharing")

            # Generate PDF
            pdf_io = io.BytesIO()
            ss.fig.savefig(pdf_io, format='pdf', dpi=300, bbox_inches='tight')
            pdf_io.seek(0)

            st.download_button(
                label="📥 Download PDF",
                data=pdf_io.getvalue(),
                file_name=f"{ss.params.substation_name.replace(' ', '_')}_SLD.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with col2:
            st.markdown("#### 🎨 DXF Export")
            st.write("AutoCAD-compatible vector format for editing")

            # Generate DXF (as string)
            dxf_buffer = io.StringIO()
            ss.renderer.export_dxf(dxf_buffer)
            dxf_content = dxf_buffer.getvalue()

            st.download_button(
                label="📥 Download DXF",
                data=dxf_content,
                file_name=f"{ss.params.substation_name.replace(' ', '_')}_SLD.dxf",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.info("⚠️ Generate an SLD first to enable downloads")

with tab3:
    st.markdown("### Generation Summary")

    if 'renderer' in ss and ss.renderer is not None:
        summary = ss.renderer.get_summary()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Configuration**")
            st.json({
                "Substation": summary['substation'],
                "HV Voltage": f"{summary['hv_voltage']} kV",
                "LV Voltage": f"{summary['lv_voltage']} kV" if summary['lv_voltage'] else "N/A",
                "Bus Configuration": summary['configuration'],
                "Dual Voltage": summary['is_dual_voltage'],
                "Dual Bus": summary['is_dual_bus']
            })

        with col2:
            st.markdown("**Bay Breakdown**")
            st.json({
                "Line Bays": summary['line_bays'],
                "Transformer Bays": summary['transformer_bays'],
                "Reactor Bays": summary['reactor_bays'],
                "Total Bays": summary['total_bays'],
                "Components Drawn": summary['components_drawn']
            })
    else:
        st.info("⚠️ Generate an SLD to see summary")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("""
    **About**

    Intelligent SLD Generator v1.0
    - 11 component types
    - 3 bus configurations
    - Multi-voltage support
    """)

with col2:
    st.markdown("""
    **Features**

    ✓ Auto-layout
    ✓ PDF export
    ✓ DXF export
    ✓ Custom naming
    ✓ Any voltage
    """)

with col3:
    st.markdown("""
    **Status**

    🟢 System Ready for Testing
    📝 Report issues on GitHub
    🚀 Continuous improvement
    """)

st.caption("Built with Streamlit | Data-driven Architecture | Intelligent Rendering")
