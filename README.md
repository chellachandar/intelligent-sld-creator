# ⚡ Intelligent SLD Generator

A data-driven, parametric Single Line Diagram (SLD) generation system for electrical substations. Generate professional power system SLDs in **any voltage level**, **any bus configuration**, with **automatic layout** and **precision exports** (PDF + DXF).

## 🎯 Quick Start

### **Option 1: Web Interface (Recommended for Testing)**
```bash
pip install -r requirements.txt
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

### **Option 2: Python Script**
```python
from sld_renderer import SLDGenerationParams, generate_sld

params = SLDGenerationParams(
    substation_name="YELAHANKA SS",
    hv_voltage=400,
    lv_voltage=220,
    configuration='double_bus_coupler',
    line_bay_count=4,
    transformer_bay_count=2,
    reactor_bay_count=1
)

fig, renderer = generate_sld(params)
renderer.export_pdf("output.pdf")
renderer.export_dxf("output.dxf")
```

---

## ✨ Features

### **🏗️ Complete System**
- ✅ **11 Component Types** - Globally defined, reusable everywhere
- ✅ **3 Bus Configurations** - Single Bus, Double Bus Coupler, Double Bus Sectionalizer
- ✅ **7 Bay Types** - Line, Transformer, Reactor, Bus Coupler, etc.
- ✅ **Multi-Voltage Support** - 11kV to 765kV (any level)
- ✅ **Dual-Voltage** - 400/220, 400/110, 220/110, custom combinations
- ✅ **Smart Layout** - Auto-calculates positioning based on bay count
- ✅ **Flexible Naming** - Custom names for bays and equipment

### **📤 Professional Exports**
- ✅ **PDF** - High-resolution (300 DPI) for printing
- ✅ **DXF** - AutoCAD-compatible vector format for CAD editing
- ✅ **Excel** - Embedded images with metadata (coming soon)

### **🔧 Intelligent Architecture**
- ✅ **Data-Driven** - Config-based, not hardcoded
- ✅ **Extensible** - Add new components/bays without touching existing code
- ✅ **Validated** - Hardware constraints and input validation
- ✅ **Modular** - Clean separation of concerns

---

## 📁 Project Structure

```
intelligent-sld-creator/
├── app.py                          # Streamlit web interface
├── sld_renderer.py                 # Main rendering engine
├── config_components.py            # 11 electrical components (global)
├── config_configurations.py        # Bus configurations & voltage profiles
├── config_bays.py                  # Bay types & assembly logic
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── TESTING_GUIDE.md               # Detailed testing instructions
├── GITHUB_STREAMLIT_SETUP.md      # GitHub & Streamlit deployment
├── SYSTEM_ARCHITECTURE.md          # Complete system design
├── REFERENCE_ANALYSIS.md           # Reference SLD analysis
└── .gitignore                     # Git ignore rules
```

---

## 🚀 Deployment

### **Local Testing**
```bash
git clone https://github.com/YOUR_USERNAME/intelligent-sld-creator.git
cd intelligent-sld-creator
pip install -r requirements.txt
streamlit run app.py
```

### **Streamlit Cloud (Free)**
1. Push code to GitHub (public repo)
2. Go to streamlit.io/cloud
3. Click "New app"
4. Select your repo, branch `main`, file `app.py`
5. Click "Deploy"

**Live App:** Your app is now accessible at `https://your-app.streamlit.app`

See [GITHUB_STREAMLIT_SETUP.md](GITHUB_STREAMLIT_SETUP.md) for detailed instructions.

---

## 📊 Supported Configurations

### **Bus Schemes**
| Scheme | Use Case | Reliability |
|--------|----------|-------------|
| **Single Bus** | Simple radial networks | Low |
| **Double Bus Coupler** | Critical substations (breaker switching) | Very High |
| **Double Bus Sectionalizer** | Double bus (isolator switching) | High |

### **Voltages Tested**
- 400 kV (Transmission)
- 220 kV (Sub-transmission)
- 110 kV (Distribution)
- 33 kV, 11 kV (Local distribution)

### **Bay Types**
| Type | Components | Usage |
|------|-----------|-------|
| **Line** | Isolator, Breaker, CT, WT, LA, Earth | Transmission/Distribution lines |
| **Transformer** | HV & LV Isolators/Breakers, Power TX | Voltage transformation |
| **Reactor** | Isolators, Breaker, Reactor, CT | Reactive power compensation |
| **Bus Coupler** | Coupler Breaker/Sectionalizer | Connect parallel buses |
| **Future** | Empty | Reserved for expansion |

---

## 🔍 Examples

### **Example 1: Basic Double Bus (400/220kV)**
```python
params = SLDGenerationParams(
    substation_name="YELAHANKA SUBSTATION",
    hv_voltage=400,
    lv_voltage=220,
    configuration='double_bus_coupler',
    line_bay_count=4,
    transformer_bay_count=2,
    reactor_bay_count=1,
    bus_coupler_count=1
)
fig, renderer = generate_sld(params)
```

### **Example 2: Single Voltage (110kV)**
```python
params = SLDGenerationParams(
    substation_name="GRID STATION",
    hv_voltage=110,
    lv_voltage=None,  # Single voltage
    configuration='double_bus_sectionalizer',
    line_bay_count=3,
    transformer_bay_count=1
)
fig, renderer = generate_sld(params)
```

### **Example 3: Custom Naming**
```python
params = SLDGenerationParams(
    substation_name="POWER STATION",
    hv_voltage=400,
    lv_voltage=220,
    line_names=["TUMKUR-1 72km", "DEVANAHALLI", "LOCAL-1", "LOCAL-2"],
    transformer_names=["TX-1 (500MVA)", "TX-2 (315MVA)"],
    reactor_names=["Reactor-1"]
)
fig, renderer = generate_sld(params)
```

---

## 📋 Component Library

### **Globally Defined Components**
Each component defined once, used everywhere:

1. **Isolator** (89A, 89B, 89C, 89D) - Two circles + break line
2. **Circuit Breaker** (52) - Rectangle with connections
3. **Breaker Coupler** - Horizontal breaker for bus couplers
4. **Current Transformer** (CT, ACT, BCT) - Two semicircles
5. **Voltage Transformer** (WT) - Arc + line
6. **Capacitive VT** (CVT) - Complex multi-stage symbol
7. **Lightning Arrester** (LA) - Line with parallel earth
8. **Reactor** - Four arc segments
9. **Power Transformer** - Three coils (HV, LV, Tertiary)
10. **Earth Switch** (89E, 89AE) - Dual arcs + break
11. **Earth/Grounding** (GND) - Three decreasing lines

---

## 🔢 Bay Numbering

### **Automatic Numbering**
- **Line Bays:** 401, 403, 405, 407, ... (Odd numbers)
- **Transformer Bays:** 402, 404, 406, 408, ... (Even numbers)
- **Reactor Bays:** 421, 422, 423, ... (Sequential)
- **Bus Couplers:** Special designation

Automatic for voltage: 400kV → 4xx, 220kV → 2xx, etc.

---

## 🧪 Testing

### **Run Built-in Tests**
```bash
python test_sld_basic.py
```

Generates 3 test SLDs:
1. Double Bus Coupler (400/220kV)
2. Single Bus (220kV)
3. Double Bus Sectionalizer (110kV)

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed verification steps.

---

## 🐛 Reporting Issues

Found a bug or have a feature request?

1. **Go to Issues:** Click "Issues" tab in GitHub
2. **Create Issue:** Click "New Issue"
3. **Describe Problem:**
   - What you were trying to do
   - What went wrong
   - Expected vs actual behavior
   - Screenshots/files if applicable

**Example Issue:**
```
Title: [Component] Bus lines not horizontal in PDF

Description:
When generating a 400/220kV double bus SLD, the bus lines appear tilted 
instead of horizontal. They should be perfectly level.

Steps to reproduce:
1. Set HV voltage: 400kV
2. Set LV voltage: 220kV
3. Generate SLD
4. Download PDF

Expected: Horizontal buses
Actual: Tilted buses (see attached PDF)

Severity: High - affects professional appearance
```

---

## 💡 Architecture Highlights

### **Config-Based Design**
```python
# Define once
component = ComponentProperties(
    name="Breaker",
    symbol_type="breaker",
    height=0.4,
    line_color='black'
)

# Use everywhere
ComponentDrawer.draw_breaker(ax, x, y, label="52")
```

### **Template-Based Bays**
```python
# Define bay type once
LINE_BAY = BayTemplate(
    bay_type=BayType.LINE,
    components=[
        ComponentPlacement("isolator", 11.0, "89A", "..."),
        ComponentPlacement("breaker", 9.0, "52", "..."),
        # ...
    ]
)

# Use for any line bay
renderer._draw_bay(line_bay_arrangement, x_pos)
```

### **Intelligent Layout**
```python
# Parameters → Automatic layout
params = SLDGenerationParams(
    line_bay_count=4,
    transformer_bay_count=2,
    # ... system calculates optimal spacing
)
```

---

## 📚 Documentation

- **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - Complete system design, capabilities, extensibility
- **[REFERENCE_ANALYSIS.md](REFERENCE_ANALYSIS.md)** - Analysis of reference SLD, component properties
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Detailed testing instructions and verification checklist
- **[GITHUB_STREAMLIT_SETUP.md](GITHUB_STREAMLIT_SETUP.md)** - GitHub repo setup, Streamlit Cloud deployment
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference for running tests

---

## 🔄 Development Roadmap

### **Phase 1: Core System** ✅ COMPLETE
- [x] Component library
- [x] Bus configurations
- [x] Bay templates
- [x] Rendering engine
- [x] PDF/DXF export

### **Phase 2: Web Interface** 🟢 IN PROGRESS
- [x] Streamlit app
- [x] Parameter input
- [x] PDF download
- [x] DXF download
- [ ] Excel integration

### **Phase 3: Advanced Features** 📋 PLANNED
- [ ] Reference SLD analyzer
- [ ] Custom component creation
- [ ] Batch generation
- [ ] Configuration templates
- [ ] API/REST interface

### **Phase 4: Production** 🎯 FUTURE
- [ ] Performance optimization
- [ ] Database integration
- [ ] Multi-user workspace
- [ ] Version control
- [ ] Audit trail

---

## 🤝 Contributing

Found a way to improve? Want to add features?

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes
4. Commit: `git commit -m "Add your feature"`
5. Push: `git push origin feature/your-feature`
6. Open Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👨‍💻 Authors

Created by: **Claude AI** for **Chella Chandar**

Initial requirements and reference SLD: **Chella Chandar**

---

## 📞 Support

- 📧 Issues: GitHub Issues tab
- 💬 Discussions: GitHub Discussions tab
- 📚 Docs: See documentation files above

---

## 🎓 Learning Resources

- [Electrical SLD Basics](https://en.wikipedia.org/wiki/One-line_diagram)
- [Power System Configuration](https://www.eaton.com/us/en-us/products/medium-voltage-products/metering-power-quality/medium-voltage-assets/metering-power-quality-training/documentation.html)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Python Data Visualization](https://matplotlib.org/)

---

## ✅ Status

🟢 **System Ready for Testing**
- Core rendering engine: Production ready
- Streamlit interface: Ready for testing
- Exports (PDF/DXF): Working
- Multi-voltage support: Full
- GitHub: Public repo available
- Streamlit Cloud: Ready to deploy

**Next:** Test with real inputs and report findings!

---

**Made with ❤️ for power system professionals**

🚀 Ready to generate professional SLDs? Try the live demo!
