# Quick-Start Guide - Testing the SLD System

## ⚡ 3-Minute Quick Test

### **Step 1: Open Command Prompt**
Press `Win + R`, type `cmd`, press Enter

### **Step 2: Navigate to Project**
```bash
cd E:\Master_Claude\01_Career\Innovation_Ideas\SLD Creator
```

### **Step 3: Run Tests**
```bash
python test_sld_basic.py
```

### **Step 4: Check Results**
Look for this at the end:
```
✅ ALL BASIC TESTS PASSED - SYSTEM IS WORKING!
```

Output files will be in: `test_outputs/`

---

## 📁 Generated Files

After running tests, you'll have:

```
test_outputs/
├── test_1_double_bus_400_220.pdf     ← Open in PDF reader
├── test_1_double_bus_400_220.dxf     ← Open in AutoCAD
├── test_2_single_bus_220.pdf
├── test_2_single_bus_220.dxf
├── test_3_double_sectionalizer_110.pdf
└── test_3_double_sectionalizer_110.dxf
```

---

## 🔍 What to Check

### **In PDF Files:**
1. ✓ Two buses visible (if dual voltage/dual bus)
2. ✓ Bays are evenly spaced
3. ✓ Bay numbers correct
4. ✓ Components visible in each bay
5. ✓ Title and labels readable

### **In DXF Files:**
1. ✓ Opens in AutoCAD without errors
2. ✓ Bus lines are clean vectors
3. ✓ Component symbols visible
4. ✓ Text labels present

---

## 📝 Report Issues

If you see any problems, note:
- **What's wrong?** (e.g., "Missing components in bay 401")
- **Where?** (PDF/DXF, which test, which bay)
- **Screenshot?** (Help me see it)

---

## 🎬 Common Scenarios to Test

After basic tests pass, you can try:

### **Test 4: More Bays**
Edit `test_sld_basic.py`, change Test 1:
```python
line_bay_count=8,           # Try 8 instead of 4
transformer_bay_count=5,    # Try 5 instead of 2
reactor_bay_count=3,        # Try 3 instead of 1
```

### **Test 5: Different Voltage**
Create new test:
```python
params = SLDGenerationParams(
    substation_name="HIGH VOLTAGE STATION",
    hv_voltage=765,  # Try 765kV
    lv_voltage=400,
    configuration='double_bus_coupler',
    line_bay_count=3,
    transformer_bay_count=2,
)
fig, renderer = generate_sld(params)
renderer.export_pdf("test_765kv.pdf")
```

### **Test 6: Minimum Config**
```python
params = SLDGenerationParams(
    substation_name="MINIMAL",
    hv_voltage=33,
    configuration='single_bus',
    line_bay_count=1,
    transformer_bay_count=1,
)
fig, renderer = generate_sld(params)
renderer.export_pdf("test_minimal.pdf")
```

---

## 🆘 Troubleshooting

### **"ModuleNotFoundError: No module named 'matplotlib'"**
```bash
pip install matplotlib ezdxf openpyxl pandas
```

### **"No such file or directory: test_sld_basic.py"**
Make sure you're in the right directory:
```bash
cd E:\Master_Claude\01_Career\Innovation_Ideas\SLD Creator
dir  # Should see test_sld_basic.py in the list
```

### **PDF File is Blank**
- Check console output for errors
- Try opening with different PDF reader
- Report with screenshot

### **DXF Won't Open in AutoCAD**
- Try online DXF viewer first
- Check if file size is > 0 KB
- Report error message

---

## 📞 Next Steps

1. **Run the basic tests** ✓ (CURRENT)
2. **Check outputs** - Do they look right?
3. **Report any issues** - Describe what's wrong
4. **I'll fix code** - Update components/rendering
5. **Re-run and verify** - See the improvement
6. **Iterate** - Until perfect ✓
7. **Then build UI** - Streamlit interface

---

## 💬 Questions?

- Check `TESTING_GUIDE.md` for detailed testing info
- Check `REFERENCE_ANALYSIS.md` for component details
- Check `SYSTEM_ARCHITECTURE.md` for system design

---

**Ready? Let's go!** 🚀

```bash
python test_sld_basic.py
```

Come back with the outputs and any issues you find!
