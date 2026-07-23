# Reference SLD Analysis & Intelligent System Specification

## 📊 Reference Document Properties

**File:** Ref SLD.pdf (2-page high-voltage substation diagram)
**Configuration Type:** One-and-Half Busbar (1.5-Breaker Scheme)
**Voltage Levels:** Dual-Voltage (400kV HV / 220kV LV)
**Total Bays:** ~12-15 bays visible

---

## 🏗️ Configuration Structure

### Layout Architecture
```
┌─────────────────────────────────────────────────────┐
│        UPPER BUS (HV) - 400kV                       │
│  Bay-1 | Bay-2 | Bay-3 | Bay-4 | ... | Bay-N      │
│  (Line)(Trans )(Line )(Line )  ...   (Coupler)     │
└─────────────────────────────────────────────────────┘
         |          |
    [Transfer Bus Coupler & Reactor]
         |          |
┌─────────────────────────────────────────────────────┐
│        LOWER BUS (LV) - 220kV                       │
│  Bay-1 | Bay-2 | Bay-3 | Bay-4 | ... | Bay-N      │
│  (Line)(Trans )(Line )(Line )  ...   (Coupler)     │
└─────────────────────────────────────────────────────┘
```

**Bus Section Details:**
- Upper horizontal line = HV Bus (400kV) - Blue color
- Lower horizontal line = LV Bus (220kV) - Green color
- Vertical connections = Transformers bridging two voltage levels
- Transfer bus = Redundancy connection (black dashed line)

---

## 🔧 Component Library (Global Definitions)

All components extracted from reference with standardized properties:

### 1. **ISOLATOR** (89A, 89B, 89C, 89D, etc.)
```
Properties:
  - Symbol: Two circles + diagonal line (break indication)
  - Height: ~0.8-1.0 units
  - Width: ~0.2-0.3 units
  - Label position: Below/Right
  - Color: Red (HV line), Green (Earth)
  - Spacing from bus: 0.5 units
```

### 2. **CIRCUIT BREAKER / MAIN BREAKER** (52)
```
Properties:
  - Symbol: Rectangle (0.2 x 0.4 units)
  - Vertical connections above/below
  - Label position: Right side
  - Color: Black outline, Red lines
  - Used in: Every bay (mandatory)
```

### 3. **CURRENT TRANSFORMER** (CT, ACT, BCT)
```
Properties:
  - Symbol: Two semicircles (coil representation)
  - Height: ~0.6 units
  - Label position: Left side, offset 0.3 units
  - Color: Blue
  - Variants: CT (single), ACT (A-side), BCT (B-side)
  - Spacing: Below breaker at distance 0.5 units
```

### 4. **VOLTAGE TRANSFORMER** (WT - Voltage Transformer / CVT - Capacitive VT)
```
Properties:
  - WT: Arc + horizontal line symbol
  - CVT: Complex multi-stage symbol with capacitors
  - Label position: Left side
  - Color: Red
  - Position: Lower portion of bay
  - CVT height: ~1.5 units (complex drawing)
```

### 5. **LIGHTNING ARRESTER** (LA)
```
Properties:
  - Symbol: Horizontal line with parallel earth lines below
  - Earth component: 3 progressive shorter lines
  - Label position: Below, centered
  - Color: Green (earth), Red (line connection)
  - Position: Below CVT, upper part of bay
```

### 6. **EARTH/GROUNDING SWITCH** (89E, 89AE)
```
Properties:
  - Symbol: Dual arcs + break line
  - Height: ~0.5 units
  - Label position: Right side, offset 0.2 units
  - Color: Red
  - Position: Parallel to isolator
```

### 7. **POWER TRANSFORMER** (ICT/INTER-PHASE CURRENT TRANSFORMER)
```
Properties:
  - Symbol: Large coil circles (primary & secondary windings)
  - Height: ~1.2 units
  - Width: ~0.8 units
  - Label position: Left, below symbol
  - Color: Red coils with blue secondary
  - Used in: Transformer bays
```

### 8. **REACTOR** (Shunt Reactor)
```
Properties:
  - Symbol: Four arc segments (coil)
  - Height: ~0.6 units
  - Label position: Left side, offset 0.4 units
  - Color: Red
  - Position: Similar to CT but separate bay type
```

### 9. **BUS COUPLER BREAKER** (Horizontal orientation)
```
Properties:
  - Symbol: Rectangle (0.2 x 0.4 units)
  - Horizontal connection lines (different from main bays)
  - Label position: Above
  - Color: Red lines
  - Purpose: Connect HV-HV or LV-LV buses
```

### 10. **TRANSFER BUS COUPLER**
```
Properties:
  - Symbol: Similar to bus coupler
  - Connects to dashed transfer bus line
  - Position: Between main buses
  - Color: Black dashed lines
```

### 11. **EARTH/GROUNDING SYMBOL**
```
Properties:
  - Symbol: Three horizontal lines (decreasing length)
  - Color: Green
  - Position: Base of most components
  - Standard height: ~0.3 units
```

---

## 📐 Bay Types & Arrangements

### Type 1: LINE BAY (Odd numbers: 401, 403, 405, ...)
```
Structure from top to bottom:
1. HV Bus connection line
2. Isolator (89A)
3. Isolator (89B) - parallel
4. Earth Switch (89E/89AE)
5. Connection to Middle Breaker
6. Main Breaker (52)
7. CT (Current Transformer)
8. Earth Switch (89BE)
9. Isolator for Lower Bus (89B/89C)
10. WT/CVT (Voltage Transformer)
11. LA (Lightning Arrester)
12. Earth Grounding Symbol
13. LV Bus connection line

Spacing: Vertical gap ~0.8 units between major components
Width: ~2.5-3.0 units per bay
```

### Type 2: TRANSFORMER BAY (Even numbers: 402, 404, 406, ...)
```
Structure:
1. HV Bus (400kV) at top
2. HV Isolators (89A, 89B)
3. HV Breaker (52) - may be different for 1.5 scheme
4. Power Transformer (large symbol)
   - Primary: Connected to HV side
   - Secondary: Connected to LV side
   - Windings shown with detailed coil representation
   - Specifications: kVA, impedance, tap info
5. LV Bus (220kV) at bottom
6. LV Isolators & Breaker

Special: Has detailed transformer winding data box
Position: Every 2nd bay position (even numbers)
```

### Type 3: REACTOR BAY (421, 422, 423, ...)
```
Structure:
1. Bus connection
2. Isolators
3. Breaker (52)
4. Reactor coil symbol
5. Earth symbol
6. Grounding

Similar to Line Bay but with reactor instead of line equipment
Used for: Power factor correction, voltage support
```

### Type 4: BUS COUPLER BAY
```
Structure:
1. Horizontal connection between buses
2. Breaker symbol (horizontal orientation)
3. Minimal vertical components
4. Label: (Bus_Coupler)

Purpose: Connect two main buses for redundancy
Position: Special positions in bay arrangement
```

### Type 5: TRANSFER BUS COUPLER
```
Structure:
1. Connection to transfer/auxiliary bus (dashed line)
2. Breaker (52)
3. Associated CTs and protection devices
4. Label: (Transfer_Bus_Coupler)

Purpose: Redundancy mechanism for 1.5-breaker scheme
```

### Type 6: FUTURE BAY (Placeholder)
```
Structure:
- Empty space with label "(Future_Bay)"
- Dashed outline indicating reserved space
- No equipment
Purpose: Reserved for future expansion
```

---

## 🎨 Styling & Visual Properties

### Colors
- **Red** (#FF0000): HV line connections, main equipment, active components
- **Green** (#00AA00): Grounding/earth connections
- **Blue** (#0000FF): CTs, secondary windings
- **Black** (#000000): Bus lines, structure, text
- **Black Dashed**: Transfer bus (redundancy path)

### Line Widths
- Bus lines: 0.5 units (thick)
- Connection lines: 0.3-0.4 units (medium)
- Symbol outlines: 0.2 units (thin)
- Text: Font size 8-12pt depending on bay number/label

### Fonts
- Title: Arial, 28-32pt, Bold, Centered
- Substation name: Arial, 20-24pt, Bold
- Bus labels: Arial, 14-16pt
- Component labels: Arial, 10-12pt (bay numbers, equipment types)
- Text annotations: Arial, 8-10pt (specs, legends)

### Spacing Standards
- Between adjacent bays: 2.5-3.0 units
- Between buses (HV to LV vertical distance): 8-10 units
- Component vertical spacing: 0.6-0.8 units
- Label offset from symbol: 0.3-0.5 units

---

## 🔢 Bay Numbering Scheme

### Numbering Logic
```
Line Bays:        401, 403, 405, 407, 409, 411, 413, 415, 417, 419, ...
                  (Odd numbers, max ~20 lines = up to 439)

Transformer Bays: 402, 404, 406, 408, 410, 412, 414, 416, 418, 420, ...
                  (Even numbers, max ~20 transformers = up to 440)

Reactor Bays:     421, 422, 423, 424, ...
                  (Sequential, independent)

Bus Coupler:      (Follows configuration, often at specific positions)
                  Typically labeled with parent bay numbers

Transfer Bus:     (Separate designation, often integrated with main bay)
```

### Voltage-Specific Numbering
- **HV Bays**: Start with voltage prefix (e.g., 4xx for 400kV, 2xx for 220kV)
- **LV Bays**: Same numbering, just lower voltage
- **Transformer Bays**: Span both voltage levels, numbered in HV series

---

## 🏢 Multi-Voltage Support

### Supported Configurations
1. **400kV / 220kV (Double Transformation)**
   - Primary transformer: 400/220 kV
   - Reactor on 220kV side
   
2. **400kV / 110kV (Step-down)**
   - Primary transformer: 400/110 kV
   - Possible secondary: 220/110kV
   
3. **220kV / 110kV (Distribution)**
   - Direct transformer: 220/110 kV
   
4. **Single Voltage** (Any level, single bus)
   - 400kV, 220kV, 132kV, 110kV, 66kV, 33kV, 11kV

### Bus Architecture Pattern
```
Input: {hv_voltage, lv_voltage, config_type}
  ↓
Layout Engine:
  - If HV == LV → Single bus layout
  - If HV > LV → Dual bus layout (HV above, LV below)
  - Spacing adjusts based on voltage levels
  ↓
Component Styling:
  - Colors/sizes scale based on voltage
  - Label sizes adjust for readability
```

---

## 📋 System Input Parameters

```python
class SLDParameters:
    # Essential Parameters
    substation_name: str          # "YELAHANKA SS"
    hv_voltage: float             # 400 (kV)
    lv_voltage: float             # 220 (kV)
    configuration: str            # "1.5-Breaker", "Double-Bus", etc.
    
    # Bay Configuration
    line_bays_count: int          # Number of line bays (max 20)
    transformer_bays_count: int   # Number of transformer bays
    reactor_bays_count: int       # Number of reactor bays
    bus_coupler_count: int        # Number of bus couplers
    
    # Naming (Optional)
    line_names: List[str]         # ["TUMKUR-1 72km", "DEVANAHALLI", ...]
    transformer_names: List[str]  # ["ICT-1", "POWER-TX-1", ...]
    
    # Styling (Optional)
    color_scheme: str             # "standard", "custom"
    voltage_specific_style: bool  # Adjust colors/sizes per voltage
```

---

## 🎯 Intelligent System Features

### Auto-Layout Engine
- Takes input parameters
- Calculates optimal spacing based on bay count
- Positions bays left-to-right
- Adjusts bus section width dynamically
- Auto-generates page size (A0, A1, A2, etc.)

### Component Assembly
- Fetches component definitions from library
- Assembles into bays based on type
- Applies voltage-specific styling
- Generates labeling automatically

### Multi-Format Export
- **PDF**: Rendering via Matplotlib → PDF export
- **DXF**: Precision vector format via ezdxf
- **Excel**: Embedded image + metadata

### Extensibility
- Add new bay types: Define once, use everywhere
- Add new voltages: Create configuration, auto-scales
- Add new components: Define in library, apply globally

---

## 🚀 Implementation Roadmap

### Phase 1: Core Foundation
- [ ] Configuration schema (YAML/JSON templates)
- [ ] Component library (drawing functions + properties)
- [ ] Bus configuration templates
- [ ] Parameter validation

### Phase 2: Rendering Engine
- [ ] Component renderer (individual symbols)
- [ ] Bay builder (assemble components → bay)
- [ ] SLD renderer (layout all bays → complete diagram)
- [ ] Layout calculator (dynamic positioning)

### Phase 3: User Interface
- [ ] Streamlit app (parameter input)
- [ ] Preview generation
- [ ] Multi-format export (PDF/DXF/Excel)

### Phase 4: Advanced Features
- [ ] Reference SLD analyzer
- [ ] Custom component creation
- [ ] Voltage-specific presets
- [ ] Batch generation

---

## 📊 Expected Output Samples

### For 400/220kV Configuration with:
- 4 Line Bays (401, 403, 405, 407)
- 2 Transformer Bays (402, 404)
- 1 Reactor Bay (421)
- 1 Bus Coupler

**Expected Layout:**
```
    Line(401)  Tx(402)  Line(403)  Tx(404)  Line(405)  Line(407)  Reactor  Coupler
      |          ||        |          ||        |         |         |        |
  ====================================================== (400kV Bus) ================
      |          ||        |          ||        |         |         |        |
  ====================================================== (220kV Bus) ================
      |          ||        |          ||        |         |         |        |
```

---

## 📝 Notes

1. **Flexibility**: The system should handle any bay count, voltage combination, and configuration type
2. **Consistency**: Once defined, all future SLDs maintain visual consistency
3. **Scalability**: Easy to add new component types, bays, or voltage levels
4. **Validation**: Input parameters should be validated against hardware constraints
5. **Documentation**: Each generated SLD can include auto-generated legend and specifications

---

**Next Steps:**
1. Build component library (components.py)
2. Create configuration templates (configurations.py)
3. Implement bay builder (bays.py)
4. Build renderer engine (sld_renderer.py)
5. Create Streamlit interface
