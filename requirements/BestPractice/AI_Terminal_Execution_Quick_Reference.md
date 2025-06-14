# AI Terminal Execution Operational Guide

## 🎯 **PRIMARY AI OPERATIONAL REFERENCE**

**This is the ONLY document AI systems need for reliable terminal command execution in Nautilus Trader builds.**

All critical troubleshooting, monitoring, and recovery procedures are consolidated here for immediate AI use.

## ⚡ **COMMAND EXECUTION TEMPLATES**

### **For Simple Commands (< 30 seconds)**
```bash
# Use launch-process with wait=true, max_wait_seconds=30
launch-process:
  command: "rustc --version"
  wait: true
  max_wait_seconds: 30
```

### **For Package Installation (1-10 minutes)**
```bash
# Use launch-process with wait=true, max_wait_seconds=600
launch-process:
  command: "pip install poetry"
  wait: true
  max_wait_seconds: 600
```

### **For Rust Compilation (45-90 minutes)**
```bash
# Use launch-process with wait=false, then monitor
launch-process:
  command: "cargo build --release --features ffi,python,extension-module"
  wait: false
  max_wait_seconds: 5400  # 90 minutes

# Then use read-process with wait=true to monitor
read-process:
  terminal_id: [returned_id]
  wait: true
  max_wait_seconds: 300  # Check every 5 minutes
```

## 🔍 **PROGRESS MONITORING PATTERNS**

### **Rust Compilation Progress**
Look for these patterns in output:
```
✅ NORMAL: "Compiling package 1/715"
✅ NORMAL: "Compiling package 500/715"
✅ NORMAL: "Compiling package 712/715" ← APPEARS STUCK BUT IS NORMAL
✅ NORMAL: "Linking..." or high CPU usage
✅ SUCCESS: "Finished release [optimized] target(s)"
❌ HANG: No output + No CPU + No file growth for >30 minutes
```

### **File Monitoring Commands**
```bash
# Check if key files are being created/modified
dir nautilus_core\target\release\deps\nautilus_pyo3.dll
# Look for file size growth over time
```

## 🚨 **CRITICAL HANG DETECTION**

### **Signs of Normal Operation (DO NOT INTERRUPT)**
- ✅ High CPU usage (>50%)
- ✅ File size of `nautilus_pyo3.dll` growing
- ✅ "712/715" or "713/715" in output (linking phase)
- ✅ Recent file modification timestamps

### **Signs of Actual Hang (NEEDS INTERVENTION)**
- ❌ Zero CPU usage for >10 minutes
- ❌ No file modification for >30 minutes
- ❌ Terminal shows ^C symbols
- ❌ No response to simple commands

## 🛠️ **RECOVERY PROCEDURES**

### **CRITICAL: Fix ^C Symbol Hangs (IMMEDIATE)**
```bash
# Step 1: Kill hanging process
kill-process:
  terminal_id: [hanging_terminal_id]

# Step 2: Wait for cleanup
browser_wait_browsermcp:
  time: 5

# Step 3: Start fresh terminal
launch-process:
  command: "cd nautilus_trader-develop"
  wait: true
  max_wait_seconds: 30
```

### **Level 1: Check Status**
```bash
# Check if process is still running
list-processes

# Read current output
read-process:
  terminal_id: [id]
  wait: false
  max_wait_seconds: 10
```

### **Level 2: Gentle Intervention**
```bash
# Send input to potentially unstuck process
write-process:
  terminal_id: [id]
  input_text: "\n"  # Send newline
```

### **Level 3: Process Termination**
```bash
# Kill hanging process
kill-process:
  terminal_id: [id]

# Start fresh terminal
launch-process:
  command: "cd nautilus_trader-develop"
  wait: true
  max_wait_seconds: 30
```

### **Emergency: Complete Terminal Freeze**
```bash
# Step 1: Attempt graceful termination
kill-process:
  terminal_id: [frozen_terminal]

# Step 2: Wait for cleanup
browser_wait_browsermcp:
  time: 10

# Step 3: Verify process termination
list-processes

# Step 4: Clean restart
launch-process:
  command: "cd nautilus_trader-develop && echo 'Terminal restored'"
  wait: true
  max_wait_seconds: 30
```

### **Emergency: Build Process Corruption**
```bash
# Step 1: Stop all cargo processes
launch-process:
  command: "taskkill /f /im cargo.exe"  # Windows
  wait: true
  max_wait_seconds: 30

# Step 2: Clean build artifacts
launch-process:
  command: "cd nautilus_core && cargo clean"
  wait: true
  max_wait_seconds: 120

# Step 3: Restart build from clean state
launch-process:
  command: "cargo build --release --features ffi,python,extension-module"
  wait: false
  max_wait_seconds: 5400
```

## 📊 **OUTPUT INTERPRETATION GUIDE**

### **Rust Build Success Indicators**
```
✅ "Finished release [optimized] target(s) in 49m 08s"
✅ File exists: nautilus_core/target/release/deps/nautilus_pyo3.dll
✅ File size: >100MB (typical for nautilus_pyo3.dll)
```

### **Python Build Success Indicators**
```
✅ "Build completed" (in green text)
✅ File exists: nautilus_trader/core/nautilus_pyo3.cp312-win_amd64.pyd
✅ 138 .pyd files created in nautilus_trader/ directories
```

### **Import Test Success**
```bash
python -c "import nautilus_trader; print('✅ Version:', nautilus_trader.__version__)"
# Expected output: ✅ Version: 1.211.0
```

## ⏱️ **TIMING EXPECTATIONS**

| Operation | Normal Duration | AI Wait Time | Check Interval |
|-----------|----------------|--------------|----------------|
| `rustc --version` | 2-5 seconds | 30 seconds | N/A |
| `pip install poetry` | 30-120 seconds | 300 seconds | N/A |
| `cargo build --release` | 45-60 minutes | 90 minutes | 5 minutes |
| `python build.py` | 4-8 minutes | 15 minutes | 2 minutes |
| `poetry install` | 2-5 minutes | 10 minutes | N/A |

## 🔄 **STEP-BY-STEP EXECUTION PROTOCOL**

### **Step 1: Pre-Execution**
```bash
# Always verify environment first
launch-process:
  command: "python --version"
  wait: true
  max_wait_seconds: 30

# Check current directory
launch-process:
  command: "pwd"  # Linux/macOS
  # OR "cd"      # Windows
  wait: true
  max_wait_seconds: 10
```

### **Step 2: Execute Command**
```bash
# For long processes, use wait=false
launch-process:
  command: "[your_command]"
  wait: false
  max_wait_seconds: [appropriate_timeout]

# Store terminal_id for monitoring
terminal_id = [returned_value]
```

### **Step 3: Monitor Progress**
```bash
# Check every 5 minutes for long processes
read-process:
  terminal_id: [terminal_id]
  wait: true
  max_wait_seconds: 300

# Look for progress indicators in output
# Apply interpretation rules from this guide
```

### **Step 4: Verify Completion**
```bash
# Check if process finished
list-processes

# Verify expected artifacts
launch-process:
  command: "ls -la [expected_file_path]"
  wait: true
  max_wait_seconds: 30
```

## 🎯 **NAUTILUS TRADER SPECIFIC COMMANDS**

### **Rust Compilation**
```bash
# Navigate to correct directory
launch-process:
  command: "cd nautilus_core"
  wait: true
  max_wait_seconds: 10

# Start compilation (LONG PROCESS)
launch-process:
  command: "cargo build --release --features ffi,python,extension-module"
  wait: false
  max_wait_seconds: 5400  # 90 minutes

# Monitor every 5 minutes
# EXPECT: "712/715" to appear stuck for 10-30 minutes (NORMAL)
```

### **Python Build**
```bash
# Return to project root
launch-process:
  command: "cd .."
  wait: true
  max_wait_seconds: 10

# Verify dependencies
launch-process:
  command: "python -c \"import numpy, Cython, setuptools; print('✅ Ready')\""
  wait: true
  max_wait_seconds: 30

# Start Python build
launch-process:
  command: "python build.py"
  wait: true
  max_wait_seconds: 900  # 15 minutes
```

### **Verification Tests**
```bash
# Test basic import
launch-process:
  command: "python -c \"import nautilus_trader; print('✅ Version:', nautilus_trader.__version__)\""
  wait: true
  max_wait_seconds: 60

# Test OKX adapter
launch-process:
  command: "python -c \"from nautilus_trader.adapters.okx import OKXHttpClient; print('✅ OKX OK')\""
  wait: true
  max_wait_seconds: 60
```

## 🚨 **EMERGENCY PROCEDURES**

### **If Terminal Completely Hangs**
1. ✅ Use `kill-process` to terminate
2. ✅ Wait 30 seconds
3. ✅ Start new terminal with `launch-process`
4. ✅ Navigate back to project directory
5. ✅ Resume from last successful step

### **If Build Appears Stuck at 712/715**
1. ✅ **DO NOT INTERRUPT** - This is normal
2. ✅ Check file growth: `dir nautilus_core\target\release\deps\nautilus_pyo3.dll`
3. ✅ Wait additional 30 minutes
4. ✅ Only intervene if no file growth AND no CPU usage

### **If Import Tests Fail**
1. ✅ Check if Python build completed successfully
2. ✅ Verify `.pyd` files exist in `nautilus_trader/core/`
3. ✅ Re-run `python build.py` if files missing
4. ✅ Check virtual environment activation

## 🔧 **PRE-EXECUTION ENVIRONMENT CHECK**

### **Before Any Major Operation**
```bash
# Check 1: Operating System
launch-process:
  command: "echo $env:OS"  # Windows
  wait: true
  max_wait_seconds: 10

# Check 2: Python Version
launch-process:
  command: "python --version"
  wait: true
  max_wait_seconds: 30

# Check 3: Rust Toolchain
launch-process:
  command: "rustc --version"
  wait: true
  max_wait_seconds: 30

# Check 4: Current Directory
launch-process:
  command: "cd"  # Windows
  wait: true
  max_wait_seconds: 10
```

### **Command Validation**
```bash
# Always verify command exists before execution
launch-process:
  command: "Get-Command cargo"  # PowerShell
  wait: true
  max_wait_seconds: 30

# If command not found, install or fix PATH
```

## 📋 **STAGED MONITORING FOR LONG PROCESSES**

### **4-Stage Rust Build Monitoring**
```bash
# Stage 1: Start Process (0-5 minutes)
launch-process:
  command: "cargo build --release --features ffi,python,extension-module"
  wait: false
  max_wait_seconds: 300

terminal_id = [store_returned_id]

# Stage 2: Initial Progress Check (5-15 minutes)
read-process:
  terminal_id: [terminal_id]
  wait: true
  max_wait_seconds: 600

# Stage 3: Mid-Build Monitoring (15-45 minutes)
# Check every 10 minutes, look for compilation count increases

# Stage 4: Linking Phase Monitoring (45-90 minutes)
# Check every 5 minutes during critical "712/715" linking phase
# Monitor file growth, verify CPU usage
```

---

**🎯 COMPLETE AI OPERATIONAL GUIDE - NO OTHER DOCUMENTS NEEDED**

**Status**: ✅ **READY FOR IMMEDIATE USE**
**Target**: AI systems in dual-development environment
**Compatibility**: All Augment AI terminal tools
**Coverage**: All critical execution, monitoring, and recovery procedures
