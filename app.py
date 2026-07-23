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

st.sidebar.markdown("### 🎯 **SUBSTATION CONFIGURATION**")

# Basic Parameters
with st.sidebar:
    col1, col2 = st.columns(2)

    with col1:
        substation_name = st.text_input(
            "Substation Name",
            value="YELAHANKA SUBSTATION",
            help="Name of the substation"
        )

    with col2:
        title_text = st.text_input(
            "Title",
            value="POWERGRID CORPORATION OF INDIA LTD",
            help="Header text for SLD"
        )

    st.divider()

    # Voltage Configuration
    st.markdown("**Voltage Configuration**")

    col1, col2 = st.columns(2)

    with col1:
        hv_voltage = st.selectbox(
            "HV Voltage (kV)",
            options=[11, 33, 66, 110, 132, 220, 400, 765],
            index=6,  # 400kV default
            help="High Voltage bus voltage"
        )

    with col2:
        single_voltage = st.checkbox(
            "Single Voltage?",
            value=False,
            help="Uncheck for dual-voltage (HV/LV)"
        )

    if not single_voltage:
        lv_voltage = st.selectbox(
            "LV Voltage (kV)",
            options=[11, 33, 66, 110, 132, 220, 400],
            index=2,  # 220kV default
            help="Low Voltage bus voltage"
        )
    else:
        lv_voltage = None

    st.divider()

    # Bus Configuration
    st.markdown("**Bus Configuration**")
    configuration = st.radio(
        "Select Configuration",
        options=["single_bus", "double_bus_coupler", "double_bus_sectionalizer"],
        format_func=lambda x: {
            "single_bus": "🔌 Single Bus",
            "double_bus_coupler": "🔀 Double Bus with Coupler",
            "double_bus_sectionalizer": "🔀 Double Bus with Sectionalizer"
        }[x],
        help="Bus architecture type"
    )

    st.divider()

    # Bay Configuration
    st.markdown("**Bay Configuration**")

    col1, col2, col3 = st.columns(3)

    with col1:
        line_bay_count = st.number_input(
            "OHL Line Bays",
            min_value=0,
            max_value=20,
            value=4,
            help="Overhead line bays (gantry termination)"
        )

    with col2:
        transformer_bay_count = st.number_input(
            "Transformer Bays",
            min_value=0,
            max_value=20,
            value=2,
            help="Number of power transformer bays"
        )

    with col3:
        reactor_bay_count = st.number_input(
            "Reactor Bays",
            min_value=0,
            max_value=10,
            value=1,
            help="Number of shunt reactor bays"
        )

    cable_bay_count = st.number_input(
        "Cable Feeder Bays",
        min_value=0,
        max_value=20,
        value=0,
        help="Line bays terminating in cable sealing ends"
    )

    bus_coupler_count = st.number_input(
        "Bus Couplers",
        min_value=0,
        max_value=5,
        value=1 if configuration != "single_bus" else 0,
        help="Number of bus coupler bays"
    )

    st.divider()

    # Custom Names (Optional)
    st.markdown("**Custom Bay Names (Optional)**")

    with st.expander("Add custom names for bays"):
        line_names = []
        transformer_names = []
        reactor_names = []

        if line_bay_count > 0:
            st.markdown("**Line Bay Names**")
            for i in range(line_bay_count):
                name = st.text_input(
                    f"Line Bay {i+1}",
                    value=f"",
                    key=f"line_bay_{i}"
                )
                if name:
                    line_names.append(name)

        if transformer_bay_count > 0:
            st.markdown("**Transformer Bay Names**")
            for i in range(transformer_bay_count):
                name = st.text_input(
                    f"Transformer Bay {i+1}",
                    value=f"",
                    key=f"tx_bay_{i}"
                )
                if name:
                    transformer_names.append(name)

        if reactor_bay_count > 0:
            st.markdown("**Reactor Bay Names**")
            for i in range(reactor_bay_count):
                name = st.text_input(
                    f"Reactor Bay {i+1}",
                    value=f"",
                    key=f"reactor_bay_{i}"
                )
                if name:
                    reactor_names.append(name)

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
                params = SLDGenerationParams(
                    substation_name=substation_name,
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
                    title_text=title_text
                )

                # Generate SLD
                fig, renderer = generate_sld(params)

                # Store in session state for download
                ss.fig = fig
                ss.renderer = renderer
                ss.params = params

                # Display preview
                st.pyplot(fig, use_container_width=True)

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
