# Intelligent SLD Generation System - Architecture

## 🎯 System Overview

A fully **parametric, data-driven, intelligent Single Line Diagram (SLD) generator** for electrical substations.

**Key Features:**
- ✅ All components defined globally (once, used everywhere)
- ✅ Bus configurations as templates (Double Bus, Single Bus, with Coupler/Sectionalizer)
- ✅ Bay types fully configurable (Line, Transformer, Reactor, etc.)
- ✅ Multi-voltage support (any kV level: 400, 220, 110, 33, 11, etc.)
- ✅ Dual-voltage support (400/220, 400/110, 220/110 combinations)
- ✅ Flexible bay numbering (Odd/Even/Sequential)
- ✅ Auto-layout based on bay count
- ✅ PDF + DXF export with precision

---

## 📁 System Architecture

```
intelligent_sld_system/
│
├── config_components.py          [✓ COMPLETE]
│   ├── ComponentProperties (dataclass)
│   ├── ComponentLibrary (all 11 equipment types)
│   ├── ComponentDrawer (rendering methods)
│   └── DRAWER_REGISTRY (function lookup)
│
├── config_configurations.py       [✓ COMPLETE]
│   ├── BusScheme (Enum)
│   ├── BusConfiguration (template)
│   ├── BusConfigurations (SINGLE_BUS, DOUBLE_BUS_COUPLER, DOUBLE_BUS_SECTIONALIZER)
│   ├── ConfigConstraints (hardware limits)
│   ├── VoltageProfile (styling per voltage)
│   └── BayNumberingScheme (401, 402, 421, etc.)
│
├── config_bays.py                [✓ COMPLETE]
│   ├── BayType (Enum)
│   ├── ComponentPlacement (component positioning)
│   ├── BayTemplate (bay assembly)
│   ├── BayTemplates (LINE, TRANSFORMER, REACTOR, BUS_COUPLER, etc.)
│   ├── BayArrangement (sequence spec)
│   ├── BayArrangementValidator (validation logic)
│   └── BAY_REGISTRY (lookup)
│
├── sld_renderer.py               [✓ COMPLETE]
│   ├── SLDGenerationParams (input parameters)
│   ├── SLDRenderer (main engine)
│   │   ├── render() - Generate diagram
│   │   ├── export_pdf() - PDF output
│   │   ├── export_dxf() - DXF output
│   │   └── get_summary() - Generation report
│   └── generate_sld() - Convenience function
│
├── main.py                       [📋 TODO]
│   └── Streamlit interface for end users
│
├── REFERENCE_ANALYSIS.md         [✓ COMPLETE]
└── SYSTEM_ARCHITECTURE.md        [✓ THIS FILE]
```

---

## 🔧 Component Library

**11 Equipment Types Defined (Global):**

1. **Isolator (89A, 89B, 89C, 89D)**
   - Symbol: Two circles + diagonal break
   - Used in: All bay types
   - Properties: Height 0.8, Color: Red

2. **Circuit Breaker (52)**
   - Symbol: Rectangle with vertical connections
   - Used in: All bay types
   - Properties: 0.2 x 0.4 units

3. **Breaker Coupler**
   - Symbol: Horizontal rectangle
   - Used in: Bus coupler bays
   - Purpose: Connect parallel buses

4. **Current Transformer (CT, ACT, BCT)**
   - Symbol: Two semicircles (coil)
   - Color: Blue
   - Used in: Line and transformer bays

5. **Voltage Transformer (WT)**
   - Symbol: Arc + line
   - Color: Red
   - Alternative: CVT (Capacitive VT, complex)

6. **Lightning Arrester (LA)**
   - Symbol: Line with parallel earth
   - Color: Green (earth)
   - Used in: Line bays

7. **Reactor**
   - Symbol: Four arc segments
   - Color: Red
   - Used in: Reactor bays, transfer bus couplers

8. **Power Transformer**
   - Symbol: Three coils (HV, LV, Tertiary)
   - Used in: Transformer bays
   - Connects two voltage levels

9. **Earth/Grounding Switch (89E, 89AE)**
   - Symbol: Dual arcs + break line
   - Color: Red
   - Used in: Most bays

10. **Earth/Grounding Symbol (GND)**
    - Symbol: Three horizontal lines
    - Color: Green
    - Used in: Base of most bays

11. **Bus Connection Lines**
    - Automatic: Connects bays to buses
    - Color: Voltage-specific

---

## 📋 Bus Configurations

### 1. Single Bus
```
┌──────────────────────────────────────────┐
│        MAIN BUS (400kV)                 │
│  Line | Tx | Line | Reactor | Coupler  │
└──────────────────────────────────────────┘
```
- Simple, low cost
- No redundancy
- All feeders on one bus

### 2. Double Bus Bar with Coupler
```
┌──────────────────────────────────────────┐
│        MAIN BUS-1 (400kV)               │
│  Line | Tx | Line | Line | Coupler     │
└──────────────────────────────────────────┘
         |                        |
    ┌────────────────┐    ┌────────────────┐
    │   Coupler      │    │   Coupler      │
    │   Breaker(52)  │    │   Breaker(52)  │
    └────────────────┘    └────────────────┘
         |                        |
┌──────────────────────────────────────────┐
│        MAIN BUS-2 (400kV)               │
│  Line | Tx | Line | Line | Coupler     │
└──────────────────────────────────────────┘
```
- High reliability
- Motorized breaker coupler
- Each feeder can switch to either bus
- Cost: Higher (breaker redundancy)

### 3. Double Bus Bar with Sectionalizer
```
Similar to above, but:
- Coupler is motorized isolator (not breaker)
- Slightly cheaper
- Same switching capability
- Manual operation possible
```

---

## 🏗️ Bay Types

### Fully Templated (Reusable)

| Bay Type | Components | Used For | Numbering |
|----------|-----------|----------|-----------|
| **Line** | Isolators, Breaker, CT, WT/CVT, LA, Earth | Feed transmission/distribution lines | Odd: 401, 403, 405... |
| **Transformer** | HV Isolators/Breaker, Power TX, LV Isolators/Breaker | Voltage transformation | Even: 402, 404, 406... |
| **Reactor** | Isolators, Breaker, Reactor, CT, Earth | Reactive power, voltage support | Sequential: 421, 422, 423... |
| **Bus Coupler** | Coupler Breaker/Sectionalizer, CT | Connect parallel buses | Special |
| **Transfer Bus Coupler** | Coupler Breaker, Reactor | 1.5-breaker scheme (future) | Special |
| **Future Bay** | None (empty) | Reserved space | Flexible |
| **No Bay** | None (empty) | Empty placeholder | Flexible |

---

## 🎯 Input Parameters

```python
@dataclass
class SLDGenerationParams:
    # Essential Inputs
    substation_name: str          # "YELAHANKA SS"
    hv_voltage: float             # 400
    lv_voltage: Optional[float]   # 220 (None for single voltage)
    configuration: str            # "double_bus_coupler"

    # Bay Counts
    line_bay_count: int           # 4
    transformer_bay_count: int    # 2
    reactor_bay_count: int        # 1
    bus_coupler_count: int        # 1

    # Custom Names (Optional)
    line_names: List[str]         # ["TUMKUR-1 72km", "DEVANAHALLI", ...]
    transformer_names: List[str]  # ["TX-1 (500MVA)", ...]
    reactor_names: List[str]      # ["Reactor-1"]

    # Styling (Optional)
    title_text: str               # "POWERGRID..."
    show_legend: bool             # True
    dpi: int                      # 300
```

---

## 🚀 Usage Example

```python
from sld_renderer import SLDGenerationParams, generate_sld

# Define parameters
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

# Generate SLD
fig, renderer = generate_sld(params)

# Export
renderer.export_pdf("output.pdf")
renderer.export_dxf("output.dxf")

# Get summary
summary = renderer.get_summary()
print(summary)
# Output: {
#   'substation': 'YELAHANKA SUBSTATION',
#   'hv_voltage': 400,
#   'lv_voltage': 220,
#   'configuration': 'double_bus_coupler',
#   'total_bays': 8,
#   'line_bays': 4,
#   'transformer_bays': 2,
#   'reactor_bays': 1,
#   'components_drawn': 68,
#   'is_dual_voltage': True,
#   'is_dual_bus': True
# }
```

---

## 🔢 Bay Numbering System

### Line Bays (Odd Numbers)
```
400kV: 401, 403, 405, 407, 409, 411, 413, 415, 417, 419, ... 439 (max 20)
220kV: 201, 203, 205, 207, ... 239
110kV: 101, 103, 105, 107, ... 139
```

### Transformer Bays (Even Numbers)
```
400kV: 402, 404, 406, 408, 410, 412, 414, 416, 418, 420, ... 440 (max 20)
220kV: 202, 204, 206, 208, ... 240
110kV: 102, 104, 106, 108, ... 140
```

### Reactor Bays (Sequential)
```
400kV: 421, 422, 423, 424, ... (independent of line/transformer count)
220kV: 221, 222, 223, 224, ...
110kV: 121, 122, 123, 124, ...
```

### Bus Couplers (Special)
```
Typically drawn as special horizontal connections
Not assigned standard bay numbers (or use special numbering)
```

---

## 💡 Intelligent Features

### 1. **Automatic Layout**
- Calculates page size based on total bay count
- Positions bays automatically with optimal spacing
- Handles dual-voltage (upper/lower bus)
- Handles dual-bus scenarios

### 2. **Component Reusability**
- Define component once → Use in any bay, any voltage
- Change component properties → Affects all instances
- No code duplication

### 3. **Voltage Scalability**
- Any voltage: 11kV to 765kV
- Auto-adjusts sizing and colors
- Voltage profiles for styling rules

### 4. **Configuration Flexibility**
- Add new bus configurations easily
- Add new bay types without affecting others
- Custom bay arrangements via API

### 5. **Export Precision**
- PDF: High-quality raster output (300 DPI)
- DXF: Precision vector for CAD editing
- Both preserve all symbols and text

---

## 📈 System Capabilities

| Feature | Capability | Status |
|---------|-----------|--------|
| **Voltages Supported** | 11kV to 765kV (any level) | ✓ Complete |
| **Bus Configurations** | Single, Double Coupler, Double Sectionalizer | ✓ Complete |
| **Bay Types** | 7 types (Line, Transformer, Reactor, Coupler, Future, No-bay) | ✓ Complete |
| **Component Types** | 11 equipment types (Breaker, CT, WT, Reactor, etc.) | ✓ Complete |
| **Multi-Voltage** | 400/220, 400/110, 220/110, custom combinations | ✓ Complete |
| **Dual Bus Support** | Two parallel buses with coupler/sectionalizer | ✓ Complete |
| **Auto-Layout** | Dynamic positioning based on bay count | ✓ Complete |
| **PDF Export** | High-resolution output | ✓ Complete |
| **DXF Export** | AutoCAD-compatible vector format | ✓ Complete |
| **Excel Integration** | Embedded image in workbook | 📋 TODO |
| **User Interface** | Streamlit web app for inputs | 📋 TODO |
| **Reference Analyzer** | Extract properties from reference SLD | 📋 TODO |

---

## 🔄 Workflow

```
User Input (UI) → Validation → Parameter Config
    ↓
Component Library (Global) + Bay Templates
    ↓
SLD Renderer Engine
    ├── Calculate Layout
    ├── Draw Buses
    ├── Draw All Bays
    ├── Add Labels/Title
    └── Render Complete Diagram
    ↓
Export
├── PDF (High-quality raster)
├── DXF (CAD vector)
└── Excel (with embedded image)
```

---

## 📊 Extensibility

### Adding New Component Type:
```python
# In config_components.py
NEW_COMPONENT = ComponentProperties(
    name="New Equipment",
    symbol_type="new_type",
    height=0.8,
    width=0.3,
    # ... other properties
)

# Add drawer function
@staticmethod
def draw_new_component(ax, x, y, label=""):
    # Draw logic here
    pass

# Register
DRAWER_REGISTRY['new_type'] = ComponentDrawer.draw_new_component
```

### Adding New Bay Type:
```python
# In config_bays.py
NEW_BAY = BayTemplate(
    bay_type=BayType.NEW,
    name="New Bay Type",
    components=[
        ComponentPlacement("component_type", relative_y, "label", "description"),
        # ...
    ]
)

BAY_REGISTRY['new_bay'] = NEW_BAY
```

### Adding New Voltage Profile:
```python
# In config_configurations.py
VOLTAGE_PROFILES[765] = VoltageProfile(
    voltage=765,
    region='transmission',
    color_scheme={...},
    # ... styling rules
)
```

---

## 📝 Next Steps

1. **Create Streamlit UI** (main.py)
   - Input parameter form
   - Preview generation
   - Export buttons

2. **Excel Integration**
   - Embed generated image in workbook
   - Add metadata sheet

3. **Reference Analyzer**
   - Load reference SLD
   - Extract component properties
   - Auto-suggest configurations

4. **Testing & Refinement**
   - Unit tests for components
   - Integration tests for full workflows
   - Edge case handling

5. **Documentation & Training**
   - User guide
   - API reference
   - Configuration examples

---

## 🎓 Key Principles

1. **DRY (Don't Repeat Yourself)**: Each component/configuration defined once
2. **Separation of Concerns**: Config → Templates → Rendering → Export
3. **Extensibility**: Easy to add new components/configurations
4. **Validation**: Input constraints checked before rendering
5. **Precision**: Exact positioning and sizing for professional output
6. **Flexibility**: Support any voltage, any bus configuration, any bay count

---

## ✅ Completed Modules

✓ `config_components.py` - 11 component types fully defined
✓ `config_configurations.py` - 3 bus configurations + voltage profiles
✓ `config_bays.py` - 7 bay types with full assembly logic
✓ `sld_renderer.py` - Complete rendering engine with PDF/DXF export
✓ `REFERENCE_ANALYSIS.md` - Detailed reference SLD analysis
✓ `SYSTEM_ARCHITECTURE.md` - This document

---

**Status: Core System READY FOR TESTING & UI DEVELOPMENT** 🚀
