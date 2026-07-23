# Testing Guide - Intelligent SLD Generation System

## 🎯 Purpose

Before building the Streamlit UI and integrations, we need to verify that the **core rendering engine works correctly** with basic inputs.

This guide walks you through running tests and validating outputs.

---

## 📋 Test Scenarios

### **Test 1: Double Bus Bar with Coupler (400kV/220kV) - PRIMARY TEST**
This matches your reference SLD most closely.

**Input:**
```
Substation Name: YELAHANKA SUBSTATION
HV Voltage: 400 kV
LV Voltage: 220 kV
Configuration: Double Bus Bar with Coupler
Line Bays: 4 (numbered 401, 403, 405, 407)
Transformer Bays: 2 (numbered 402, 404)
Reactor Bays: 1 (numbered 421)
Bus Couplers: 1
```

**Expected Output:**
- ✓ Two horizontal buses (HV at top, LV at bottom)
- ✓ 4 line bays with components (Isolator, Breaker, CT, WT, LA, Earth)
- ✓ 2 transformer bays with power transformer symbols
- ✓ 1 reactor bay with reactor symbol
- ✓ 1 bus coupler connection between buses
- ✓ Correct bay numbering (401, 402, 403, 404, 405, 407, 421, Coupler)
- ✓ Proper spacing and layout

---

### **Test 2: Single Bus (220kV)**
Simple configuration with one bus.

**Input:**
```
Substation Name: DISTRIBUTION STATION
Voltage: 220 kV (single voltage)
Configuration: Single Bus
Line Bays: 3
Transformer Bays: 1
Reactor Bays: 0
Bus Couplers: 0
```

**Expected Output:**
- ✓ Single horizontal bus
- ✓ 3 line bays
- ✓ 1 transformer bay
- ✓ No coupler (single bus doesn't need it)
- ✓ Simpler layout than Test 1

---

### **Test 3: Double Bus with Sectionalizer (110kV)**
Double bus with motorized isolator instead of breaker.

**Input:**
```
Substation Name: GRID STATION
Voltage: 110 kV (dual bus)
Configuration: Double Bus Bar with Sectionalizer
Line Bays: 2
Transformer Bays: 1
Reactor Bays: 0
Bus Couplers: 1
```

**Expected Output:**
- ✓ Two buses
- ✓ Smaller/compact layout (110kV styling)
- ✓ Sectionalizer coupler (isolator symbol)
- ✓ 2 line + 1 transformer bay

---

## 🚀 How to Run Tests

### **Step 1: Open Terminal/Command Prompt**

Navigate to your SLD Creator folder:
```bash
cd E:\Master_Claude\01_Career\Innovation_Ideas\SLD Creator
```

### **Step 2: Install Required Libraries** (one-time only)
```bash
pip install matplotlib ezdxf openpyxl pandas
```

### **Step 3: Run Test Script**
```bash
python test_sld_basic.py
```

### **Expected Console Output:**
```
======================================================================
TEST 1: Basic Double Bus Bar with Coupler (400kV/220kV)
======================================================================

Input Parameters:
  ✓ Substation: YELAHANKA SUBSTATION
  ✓ Voltage: 400kV / 220kV
  ✓ Configuration: double_bus_coupler
  ✓ Bays: 4 lines + 2 transformers + 1 reactor

Generating SLD...

Generation Summary:
  ✓ Total Bays Created: 8
  ✓ Line Bays: 4
  ✓ Transformer Bays: 2
  ✓ Reactor Bays: 1
  ✓ Components Drawn: 68
  ✓ Dual Voltage: True
  ✓ Dual Bus: True

Exporting outputs...
  ✓ PDF: test_outputs/test_1_double_bus_400_220.pdf
  ✓ DXF: test_1_double_bus_400_220.dxf

✅ TEST 1 PASSED: Basic SLD generated successfully!

...
(Tests 2 and 3 similar output)

======================================================================
SUMMARY
======================================================================
✅ PASS: TEST 1: Double Bus Coupler (400/220kV)
✅ PASS: TEST 2: Single Bus (220kV)
✅ PASS: TEST 3: Double Bus Sectionalizer (110kV)

Total: 3/3 tests passed

📁 Output files saved to: test_outputs/
```

---

## 📊 Verification Checklist

After running tests, verify the outputs:

### **For PDF Files** (Open in any PDF viewer)

**Visual Check:**
- [ ] Two buses visible (upper = 400kV, lower = 220kV)
- [ ] Buses are horizontal lines across the page
- [ ] 4 line bays with complete symbol sets
- [ ] 2 transformer bays with large coil symbols
- [ ] 1 reactor bay with coil symbol
- [ ] Bays are evenly spaced
- [ ] Components within each bay are vertically aligned
- [ ] No overlapping or misaligned elements
- [ ] Title "POWERGRID..." visible at top
- [ ] Substation name visible
- [ ] Color scheme correct (Red lines, Green earth)

**Labeling Check:**
- [ ] Bay numbers correct: 401, 402, 403, 404, 405, 407, 421
- [ ] Component labels visible (52, CT, WT, LA, etc.)
- [ ] Voltage labels on buses (400 kV, 220 kV)

### **For DXF Files** (Open in AutoCAD or online viewer)

**DXF-Specific Checks:**
- [ ] Can open without errors in AutoCAD
- [ ] All bus lines present
- [ ] All components rendered as vectors
- [ ] Text labels readable
- [ ] No broken references
- [ ] Proper layering/color mapping

### **Bay Component Details**

**Line Bay (should have):**
- [ ] Two isolators at top (HV side)
- [ ] One breaker in middle
- [ ] One CT (Current Transformer)
- [ ] One WT/CVT (Voltage Transformer)
- [ ] One LA (Lightning Arrester)
- [ ] Earth/grounding symbols
- [ ] Isolators at bottom (LV side)

**Transformer Bay (should have):**
- [ ] HV isolators and breaker at top
- [ ] Large transformer symbol in middle
- [ ] LV isolators and breaker at bottom
- [ ] Connections between HV and LV sides

**Reactor Bay (should have):**
- [ ] Isolators at top
- [ ] Breaker
- [ ] Reactor coil symbol
- [ ] CT
- [ ] Grounding

---

## 🔍 What to Look For (Issues to Report)

If you see any of these issues, report them for code updates:

| Issue | Impact | Report |
|-------|--------|--------|
| Bays not evenly spaced | Layout looks poor | "Bays have uneven spacing" |
| Components overlapping | Diagram unreadable | "Component overlap at bay X" |
| Missing components | Incomplete bay | "Missing CT in Line bay 401" |
| Wrong bay numbering | Confusion | "Bay numbers incorrect: showing X but should be Y" |
| Bus lines not straight | Unprofessional | "Bus lines not horizontal" |
| Text misaligned | Hard to read | "Labels overlapping components" |
| Colors wrong | Cannot distinguish | "Line components should be red, not blue" |
| Transformers not bridging buses | Electrical error | "Transformer not connecting HV to LV" |
| DXF won't open | Export broken | "DXF file corruption" |
| PDF export failed | Cannot deliver | "PDF export error: ..." |

---

## 📝 Feedback Format

When reporting issues, use this format:

```
TEST ISSUE REPORT
================

Test Number: [1, 2, or 3]
Issue: [Brief description]
Severity: [Critical / High / Medium / Low]

Expected Behavior:
[What should happen]

Actual Behavior:
[What actually happened]

Evidence:
[PDF screenshot, DXF error message, etc.]

Suggested Fix:
[If you have an idea]

Code Reference:
[File and line if known, e.g., config_components.py line 45]
```

---

## 🎬 Step-by-Step Example

### **Example: Testing Test 1**

1. **Run command:**
   ```bash
   python test_sld_basic.py
   ```

2. **Check console output** - Should show 3/3 tests passed ✅

3. **Open PDF** - `test_outputs/test_1_double_bus_400_220.pdf`
   - Look for two horizontal buses
   - Count the bays (should be 8 total)
   - Verify components in each bay

4. **Open in AutoCAD** - `test_outputs/test_1_double_bus_400_220.dxf`
   - Should import without errors
   - Verify vectors are clean
   - Check text labels readable

5. **Report findings:**
   ```
   TEST ISSUE REPORT
   ================
   
   Test Number: 1
   Issue: Bus lines appear to be disconnected
   Severity: High
   
   Expected Behavior:
   Two continuous horizontal buses spanning the entire page
   
   Actual Behavior:
   Buses appear broken/segmented
   
   Evidence: See test_outputs/test_1_double_bus_400_220.pdf
   
   Code Reference: sld_renderer.py, _draw_bus_section()
   ```

---

## ✅ Success Criteria

**System is ready for UI development when:**

- [ ] All 3 tests pass without errors
- [ ] PDFs generate with correct layouts
- [ ] DXF files open in AutoCAD without errors
- [ ] Bays have correct components
- [ ] Bay numbering is correct
- [ ] Color scheme is correct
- [ ] Spacing is reasonable
- [ ] No overlapping elements

---

## 🔄 Iteration Process

Once you run tests:

1. **Report any issues** using the format above
2. **I'll update the code** to fix them
3. **You re-run tests** to verify fix
4. **Repeat** until outputs match requirements perfectly
5. **Move forward** to UI and integration development

---

## 💡 Pro Tips

- **Run tests multiple times** to ensure consistency
- **Try different bay counts** to test scaling
- **Mix bay types** to test combinations
- **Check PDFs at 100% zoom** for precision details
- **Save outputs** for before/after comparison

---

## 📞 Questions During Testing?

If something is unclear:
1. Check REFERENCE_ANALYSIS.md for component definitions
2. Check SYSTEM_ARCHITECTURE.md for system design
3. Review the config files to understand structure
4. Report the issue with as much detail as possible

---

**Ready to test? Run this command and report back!**

```bash
python test_sld_basic.py
```

**Let me know what the outputs look like and any issues you spot!** 🚀
