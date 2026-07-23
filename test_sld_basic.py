"""
BASIC SLD TEST SCRIPT
====================================
Simple test to generate SLD with basic inputs and verify outputs.
Run this to test the intelligent system before UI development.
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sld_renderer import SLDGenerationParams, generate_sld
import matplotlib.pyplot as plt


def test_basic_sld():
    """Test 1: Basic Double Bus Bar Configuration (400kV/220kV)"""
    print("\n" + "="*70)
    print("TEST 1: Basic Double Bus Bar with Coupler (400kV/220kV)")
    print("="*70)

    params = SLDGenerationParams(
        substation_name="YELAHANKA SUBSTATION",
        hv_voltage=400,
        lv_voltage=220,
        configuration='double_bus_coupler',
        line_bay_count=4,
        transformer_bay_count=2,
        reactor_bay_count=1,
        bus_coupler_count=1,
        line_names=["TUMKUR-1 72km", "DEVANAHALLI", "Local-1", "Local-2"],
        transformer_names=["TX-1 (500MVA)", "TX-2 (315MVA)"],
        reactor_names=["Reactor-1"]
    )

    print(f"\nInput Parameters:")
    print(f"  ✓ Substation: {params.substation_name}")
    print(f"  ✓ Voltage: {params.hv_voltage}kV / {params.lv_voltage}kV")
    print(f"  ✓ Configuration: {params.configuration}")
    print(f"  ✓ Bays: {params.line_bay_count} lines + {params.transformer_bay_count} transformers + {params.reactor_bay_count} reactor")
    print(f"  ✓ Bus Couplers: {params.bus_coupler_count}")

    try:
        print(f"\nGenerating SLD...")
        fig, renderer = generate_sld(params)

        # Get summary
        summary = renderer.get_summary()
        print(f"\nGeneration Summary:")
        print(f"  ✓ Total Bays Created: {summary['total_bays']}")
        print(f"  ✓ Line Bays: {summary['line_bays']}")
        print(f"  ✓ Transformer Bays: {summary['transformer_bays']}")
        print(f"  ✓ Reactor Bays: {summary['reactor_bays']}")
        print(f"  ✓ Components Drawn: {summary['components_drawn']}")
        print(f"  ✓ Dual Voltage: {summary['is_dual_voltage']}")
        print(f"  ✓ Dual Bus: {summary['is_dual_bus']}")

        # Export to files
        output_dir = Path(__file__).parent / "test_outputs"
        output_dir.mkdir(exist_ok=True)

        pdf_path = output_dir / "test_1_double_bus_400_220.pdf"
        dxf_path = output_dir / "test_1_double_bus_400_220.dxf"

        print(f"\nExporting outputs...")
        renderer.export_pdf(str(pdf_path))
        renderer.export_dxf(str(dxf_path))

        print(f"  ✓ PDF: {pdf_path}")
        print(f"  ✓ DXF: {dxf_path}")

        print(f"\n✅ TEST 1 PASSED: Basic SLD generated successfully!")

        return fig, renderer

    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def test_single_bus():
    """Test 2: Single Bus Configuration (220kV only)"""
    print("\n" + "="*70)
    print("TEST 2: Single Bus (220kV)")
    print("="*70)

    params = SLDGenerationParams(
        substation_name="DISTRIBUTION STATION",
        hv_voltage=220,
        lv_voltage=None,  # Single voltage
        configuration='single_bus',
        line_bay_count=3,
        transformer_bay_count=1,
        reactor_bay_count=0,
        bus_coupler_count=0,
        line_names=["Feeder-1", "Feeder-2", "Feeder-3"],
        transformer_names=["TX-Main"]
    )

    print(f"\nInput Parameters:")
    print(f"  ✓ Substation: {params.substation_name}")
    print(f"  ✓ Voltage: {params.hv_voltage}kV (Single)")
    print(f"  ✓ Configuration: {params.configuration}")
    print(f"  ✓ Bays: {params.line_bay_count} lines + {params.transformer_bay_count} transformer")

    try:
        print(f"\nGenerating SLD...")
        fig, renderer = generate_sld(params)

        summary = renderer.get_summary()
        print(f"\nGeneration Summary:")
        print(f"  ✓ Total Bays: {summary['total_bays']}")
        print(f"  ✓ Components: {summary['components_drawn']}")

        output_dir = Path(__file__).parent / "test_outputs"
        output_dir.mkdir(exist_ok=True)

        pdf_path = output_dir / "test_2_single_bus_220.pdf"
        dxf_path = output_dir / "test_2_single_bus_220.dxf"

        print(f"\nExporting outputs...")
        renderer.export_pdf(str(pdf_path))
        renderer.export_dxf(str(dxf_path))

        print(f"  ✓ PDF: {pdf_path}")
        print(f"  ✓ DXF: {dxf_path}")

        print(f"\n✅ TEST 2 PASSED: Single bus SLD generated successfully!")

        return fig, renderer

    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def test_double_bus_sectionalizer():
    """Test 3: Double Bus with Sectionalizer (110kV)"""
    print("\n" + "="*70)
    print("TEST 3: Double Bus with Sectionalizer (110kV)")
    print("="*70)

    params = SLDGenerationParams(
        substation_name="GRID STATION",
        hv_voltage=110,
        lv_voltage=None,
        configuration='double_bus_sectionalizer',
        line_bay_count=2,
        transformer_bay_count=1,
        reactor_bay_count=0,
        bus_coupler_count=1,
        line_names=["North-Line", "South-Line"],
        transformer_names=["TX-110/33"]
    )

    print(f"\nInput Parameters:")
    print(f"  ✓ Substation: {params.substation_name}")
    print(f"  ✓ Voltage: {params.hv_voltage}kV (Dual Bus with Sectionalizer)")
    print(f"  ✓ Configuration: {params.configuration}")
    print(f"  ✓ Bays: {params.line_bay_count} lines + {params.transformer_bay_count} transformer")

    try:
        print(f"\nGenerating SLD...")
        fig, renderer = generate_sld(params)

        summary = renderer.get_summary()
        print(f"\nGeneration Summary:")
        print(f"  ✓ Total Bays: {summary['total_bays']}")
        print(f"  ✓ Components: {summary['components_drawn']}")

        output_dir = Path(__file__).parent / "test_outputs"
        output_dir.mkdir(exist_ok=True)

        pdf_path = output_dir / "test_3_double_sectionalizer_110.pdf"
        dxf_path = output_dir / "test_3_double_sectionalizer_110.dxf"

        print(f"\nExporting outputs...")
        renderer.export_pdf(str(pdf_path))
        renderer.export_dxf(str(dxf_path))

        print(f"  ✓ PDF: {pdf_path}")
        print(f"  ✓ DXF: {dxf_path}")

        print(f"\n✅ TEST 3 PASSED: Double bus with sectionalizer SLD generated successfully!")

        return fig, renderer

    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def main():
    """Run all tests"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  INTELLIGENT SLD GENERATION SYSTEM - BASIC TESTS".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)

    # Create output directory
    output_dir = Path(__file__).parent / "test_outputs"
    output_dir.mkdir(exist_ok=True)

    test_results = []

    # Run tests
    fig1, renderer1 = test_basic_sld()
    test_results.append(("TEST 1: Double Bus Coupler (400/220kV)", renderer1 is not None))

    fig2, renderer2 = test_single_bus()
    test_results.append(("TEST 2: Single Bus (220kV)", renderer2 is not None))

    fig3, renderer3 = test_double_bus_sectionalizer()
    test_results.append(("TEST 3: Double Bus Sectionalizer (110kV)", renderer3 is not None))

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    print(f"\n📁 Output files saved to: {output_dir}")
    print(f"\nNext Steps:")
    print(f"  1. Check PDF files for visual correctness")
    print(f"  2. Check DXF files in AutoCAD for precision")
    print(f"  3. Verify:")
    print(f"     - Correct number of bays")
    print(f"     - Correct bay numbering (odd/even)")
    print(f"     - Correct components in each bay")
    print(f"     - Correct bus configurations")
    print(f"     - Correct voltage labels")
    print(f"     - Overall layout and spacing")
    print(f"  4. Report any issues for code updates")

    print("\n" + "█"*70 + "\n")

    if passed == total:
        print("✅ ALL BASIC TESTS PASSED - SYSTEM IS WORKING!\n")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED - CHECK ERRORS ABOVE\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
