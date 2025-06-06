# Complete Nautilus Trader Development Environment Setup Guide

## 🎯 **MISSION: COMPLETE FRESH ENVIRONMENT SETUP**

This is the **ONLY** document you need for setting up a complete Nautilus Trader development environment from scratch. All other build documents have been archived.

**CRITICAL**: Follow these instructions EXACTLY in order. Do not skip steps or use shortcuts.

## 0️⃣ **STEP 0: SYSTEM PREPARATION (PREREQUISITES)**

Before proceeding with the Nautilus Trader specific setup, ensure your system has the following base tools installed. These instructions are for a "blank" or unprepared system.

### **0.1 Install Python (3.11 or 3.12)**

Nautilus Trader requires Python 3.11 or 3.12. Python 3.13 is NOT currently supported.

**Windows:**
1.  Download the Python installer from [python.org](https://www.python.org/downloads/windows/).
2.  Run the installer. **Crucially, check the box that says "Add Python to PATH"** during installation.
3.  Verify installation: Open a new Command Prompt or PowerShell and type `python --version` and `pip --version`.

**Linux:**
Most Linux distributions come with Python. You might need to install a specific version or ensure `pip` is available.
```bash
# Example for Debian/Ubuntu
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git
# Verify
python3 --version
pip3 --version
```

**macOS:**
Python is usually pre-installed. Consider using Homebrew for managing versions:
```bash
# Install Homebrew (if not already installed) from https://brew.sh/
brew install python@3.11 git
# Verify
python3 --version
pip3 --version
```

### **0.2 Install Git**

Git is required for cloning the repository.

**Windows:**
1.  Download and install Git for Windows from [git-scm.com](https://git-scm.com/download/win).
2.  Use the default options during installation.
3.  Verify installation: Open a new Command Prompt or PowerShell and type `git --version`.

**Linux:**
```bash
# Example for Debian/Ubuntu
sudo apt install git
# Example for Fedora
sudo dnf install git
# Verify
git --version
```

**macOS:**
Git is usually pre-installed. If not, or to get the latest version:
```bash
brew install git
# Verify
git --version
```

### **0.3 Note for AI System Installers / Full Automation**
- **Visual Studio Build Tools (Windows):** The main challenge for fully automated AI installation on Windows is the GUI-based Visual Studio Build Tools setup (detailed in Step 1.3). If a non-interactive, command-line method to install *only* the "Desktop development with C++" workload becomes reliably available and robust, it would greatly enhance full automation. Currently, this step often requires manual intervention or complex GUI automation. The subsequent system restart can also interrupt a single script flow.

Once these prerequisites are met, you can proceed with the Nautilus Trader specific setup.

## 📋 **SYSTEM REQUIREMENTS**

### **Hardware Requirements**
- **RAM**: Minimum 16GB (Rust compilation is memory-intensive)
- **Storage**: 30GB+ free disk space for build artifacts
- **CPU**: Multi-core recommended (compilation takes 60-90 minutes)
- **Internet**: Stable connection for downloading dependencies

### **Software Requirements**
- **Operating System**: Windows 10/11, Linux, or macOS
- **Python**: 3.11 or 3.12 (3.13 NOT supported)
- **Git**: Latest version for repository management
- **PowerShell**: For Windows users (built-in)

## 🔧 **STEP 1: INSTALL CORE TOOLS**

### **1.1 Install Rust Toolchain**

**Windows:**
```powershell
# Method 1: Using winget (recommended)
winget install Rustlang.Rustup

# Method 2: Manual download
# Download from: https://rustup.rs/ and run installer

# Restart terminal after installation
```

**Linux/macOS:**
```bash
# Install Rust using rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

**Verification:**
```bash
# These commands MUST work before proceeding
rustc --version
cargo --version
# Expected: rustc 1.xx.x and cargo 1.xx.x
```

### **1.2 Install Poetry (Python Package Manager)**
```bash
# Install Poetry globally
pip install poetry

# Verify installation
poetry --version
# Expected: Poetry (version 1.x.x)
```

### **1.3 Install Visual Studio Build Tools (Windows Only)**
**CRITICAL for Windows users:**
1. Download Visual Studio Build Tools 2019 or later from:
   https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019
2. Install with C++ build tools selected
3. Restart computer after installation

**Verification:**
```powershell
# This MUST show a path to cl.exe
where cl.exe
# Expected: C:\Program Files (x86)\Microsoft Visual Studio\...\cl.exe
```

## 🏗️ **STEP 2: REPOSITORY SETUP**

### **2.1 Clone Repository and Create Environment**

```bash
# Clone the repository
git clone https://github.com/Jens-AIMLX/-nautilus_trader-develop.git
cd nautilus_trader-develop

# Create dedicated virtual environment
python -m venv venv_new

# Activate virtual environment
# Windows:
venv_new\Scripts\activate
# Linux/macOS:
source venv_new/bin/activate

# Upgrade pip to latest version
python -m pip install --upgrade pip
```

### **2.2 Install EXACT Build Dependencies**

**CRITICAL**: These exact versions are required. Do not use different versions.

```bash
# Install Poetry in virtual environment
pip install poetry

# Install EXACT build dependencies (versions are critical!)
pip install setuptools>=75
pip install numpy>=1.26.4
pip install "Cython==3.1.0a1"

# Verify critical versions
python -c "import numpy; print('✅ NumPy:', numpy.__version__)"
python -c "import Cython; print('✅ Cython:', Cython.__version__)"
python -c "import setuptools; print('✅ Setuptools:', setuptools.__version__)"
```

**Expected Output:**
```
✅ NumPy: 1.26.4 (or higher)
✅ Cython: 3.1.0a1 (EXACT version required)
✅ Setuptools: 75.x.x (or higher)
```

## 🔨 **STEP 3: RUST CORE COMPILATION (60-90 MINUTES)**

### **3.1 Set Environment Variables**

**Windows:**
```powershell
# Set critical environment variables
$env:RUST_TOOLCHAIN="stable"
$env:BUILD_MODE="release"
$env:HIGH_PRECISION="false"  # Windows doesn't support 128-bit integers
```

**Linux/macOS:**
```bash
# Set critical environment variables
export RUST_TOOLCHAIN="stable"
export BUILD_MODE="release"
export HIGH_PRECISION="false"
```

### **3.2 Execute Rust Compilation**

```bash
# Navigate to Rust core directory
cd nautilus_core

# Build all 715 Rust packages with EXACT features required
cargo build --release --features ffi,python,extension-module
```

### **3.3 What to Expect During Compilation**

**Timeline:**
- **Minutes 0-5**: Downloading and compiling dependencies
- **Minutes 5-45**: Compiling 715 Rust packages
- **Minutes 45-60**: Final linking phase (may appear "stuck" at 712/715)

**CRITICAL**: The build may appear "stuck" at 712/715 packages - **THIS IS NORMAL!**
The final linking phase takes 10-30 minutes. Do not interrupt the process.

**Expected Output:**
- ✅ Compiles 715 Rust packages successfully
- ✅ Creates optimized `.dll` files in `target/release/deps/`
- ✅ **Key artifact**: `nautilus_pyo3.dll` (main Python extension)
- ✅ **Critical libraries**:
  - `nautilus_backtest.lib`
  - `nautilus_common.lib`
  - `nautilus_core.lib`
  - `nautilus_model.lib`
  - `nautilus_persistence.lib`

**Build Time**: ~49 minutes on modern hardware (16GB RAM, SSD)

## 🐍 **STEP 4: PYTHON PACKAGE BUILD (5-10 MINUTES)**

### **4.1 Verify Build Dependencies**

```bash
# Return to project root
cd ..

# CRITICAL: Verify all build dependencies are available
python -c "import numpy, Cython, setuptools; print('✅ Build dependencies ready')"
```

**Expected Output:**
```
✅ Build dependencies ready
```

### **4.2 Execute Python Build**

```bash
# Run complete build process using the official build script
python build.py
```

### **4.3 What Happens During Python Build**

The `build.py` script will:
1. ✅ Copy `nautilus_pyo3.dll` to `nautilus_trader/core/`
2. ✅ Build 138 Cython extension modules
3. ✅ Compile with MSVC using parallel compilation
4. ✅ Copy all `.pyd` files back to source tree

**Expected Output:**
- ✅ **Rust library copy**: `nautilus_pyo3.dll` → `nautilus_trader/core/nautilus_pyo3.cp312-win_amd64.pyd`
- ✅ **Cython compilation**: 138 Python extension modules (.pyx → .c → .pyd)
- ✅ **Parallel compilation**: Uses all CPU cores for faster build
- ✅ **File locations**: All `.pyd` files copied to `nautilus_trader/` source tree
- ✅ **Build time**: ~4-5 minutes
- ✅ **Final message**: "Build completed" in green text

**Build Environment Variables Used:**
- `BUILD_MODE=release` (optimized build)
- `PARALLEL_BUILD=true` (use all CPU cores)
- `COPY_TO_SOURCE=true` (copy files back to source)
- `PYO3_ONLY=false` (build both Rust and Python extensions)

## 📦 **STEP 5: POETRY DEPENDENCIES INSTALLATION**

### **5.1 Install Core Dependencies**

```bash
# Install all dependencies using Poetry
poetry install

# Install development and testing dependencies
poetry install --with dev,test

# Alternative: Install with all extras for full functionality
poetry install --all-extras

# Verify Poetry installation
poetry show | grep nautilus
```

### **5.2 Install Additional Testing Dependencies**

```bash
# Install essential testing tools
pip install pytest pytest-asyncio pytest-cov pytest-mock

# Install API integration dependencies
pip install supabase

# Verify testing dependencies
python -c "import pytest, pytest_asyncio, pytest_cov; print('✅ Testing dependencies ready')"
```

## ✅ **STEP 6: INSTALLATION VERIFICATION**

### **6.1 Basic Import Tests**

```bash
# Test basic import
python -c "import nautilus_trader; print('✅ Version:', nautilus_trader.__version__)"
```

**Expected Output:**
```
✅ Version: 1.211.0
```

### **6.2 Core Functionality Tests**

```bash
# Test core functionality
python -c "from nautilus_trader.core.nautilus_pyo3 import UUID4; from nautilus_trader.model.data import Bar; print('✅ Core imports successful')"

# Test OKX adapter (critical for our project)
python -c "from nautilus_trader.adapters.okx import OKXHttpClient, OKXWebSocketClient; print('✅ OKX adapter imports successful')"

# Test configuration classes
python -c "from nautilus_trader.adapters.okx.config import OKXDataClientConfig; print('✅ Configuration classes working')"
```

**Expected Output:**
```
✅ Core imports successful
✅ OKX adapter imports successful
✅ Configuration classes working
```

### **6.3 Run Verification Tests**

```bash
# Run verification tests (if available)
python -m pytest simple_tests/test_setup_verification.py -v
```

## 🌍 **STEP 7: ENVIRONMENT CONFIGURATION**

### **7.1 Create Environment Variables File**

Create a `.env` file in the project root directory:

```bash
# OKX API Configuration (Demo Environment for Safety)
OKX_API_KEY=your_okx_demo_api_key
OKX_API_SECRET=your_okx_demo_api_secret
OKX_PASSPHRASE=your_okx_demo_passphrase
OKX_IS_DEMO=true

# Market Whisperer Supabase Integration
SUPABASE_URL=https://hwlphzuqvzqgpgkukbqf.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_JWT_SECRET=OTBkyEr6heeOc9bjB5FRqx8n638QC900uLC3KVcYU5+H4w9jdlmLw0rTvdSC2Kcp54QjsU6vGlmu4oueAnQcHQ==

# Testing Configuration
PYTEST_TIMEOUT=300
PYTEST_VERBOSE=true
```

### **7.2 Configure VS Code Python Test Adapter (Optional)**

If using VS Code, install the Python Test Adapter extension:
- Extension ID: `littlefoxteam.vscode-python-test-adapter`
- This enables visual test execution and results viewing

### **7.3 Install Pre-commit Hooks (Optional)**

```bash
# Install pre-commit for code quality
pip install pre-commit
pre-commit install
```

## 🧪 **STEP 8: TESTING SETUP**

### **8.1 Configure pytest**

Ensure `simple_tests/pytest.ini` contains:

```ini
[tool:pytest]
testpaths = simple_tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers --cov=nautilus_trader --cov-report=html
markers =
    unit: Unit tests
    integration: Integration tests
    system: System tests
    performance: Performance tests
    acceptance: Acceptance tests
    slow: Tests that take longer than 30 seconds
```

### **8.2 Run Basic Test Suite**

```bash
# Navigate to test directory
cd simple_tests

# Run basic verification tests
python -m pytest test_setup_verification.py -v

# Run a simple unit test to verify everything works
python -m pytest test_1_1_U_okx_timeframe_manager.py -v
```

## 🚨 **TROUBLESHOOTING GUIDE**

### **Common Issue 1: Rust Compilation Appears Stuck**

**Symptom**: Build appears stuck at "712/715" packages
**Solution**:
- ✅ **THIS IS NORMAL** - final linking phase takes 10-30 minutes
- ✅ Do NOT interrupt the process
- ✅ Monitor file size growth of `nautilus_pyo3.dll` in `nautilus_core/target/release/deps/`

### **Common Issue 2: Memory Issues During Build**

**Symptom**: Build fails with out-of-memory errors or "killed" messages
**Solutions**:
- ✅ Close other applications, ensure 16GB+ available RAM
- ✅ Reduce parallel compilation: `export CARGO_BUILD_JOBS=1`
- ✅ Use swap file if necessary
- ✅ Restart computer and try again

### **Common Issue 3: Import Errors After Build**

**Symptom**: `ModuleNotFoundError` after build
**Solutions**:
- ✅ Ensure Python build (Step 4) completed successfully
- ✅ Check that `nautilus_trader/core/nautilus_pyo3.cp312-win_amd64.pyd` exists
- ✅ Verify virtual environment is activated
- ✅ Run `python build.py` again if files are missing

### **Common Issue 4: Cython Version Issues**

**Symptom**: Build fails with Cython compilation errors
**Solutions**:
- ✅ Ensure EXACT Cython version: `pip install "Cython==3.1.0a1"`
- ✅ Verification: `python -c "import Cython; print(Cython.__version__)"`
- ✅ Uninstall and reinstall if wrong version

### **Common Issue 5: MSVC Compiler Not Found (Windows)**

**Symptom**: "Microsoft Visual C++ 14.0 is required"
**Solutions**:
- ✅ Install Visual Studio Build Tools 2019 or later
- ✅ Download: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019
- ✅ Verification: `where cl.exe` should show compiler path
- ✅ Restart computer after installation

### **Common Issue 6: Poetry Installation Issues**

**Symptom**: Poetry commands fail or dependencies not found
**Solutions**:
- ✅ Reinstall Poetry: `pip uninstall poetry && pip install poetry`
- ✅ Clear Poetry cache: `poetry cache clear --all pypi`
- ✅ Use pip fallback: `pip install -e .`

### **Common Issue 7: Terminal Hangs with ^C**

**Symptom**: PowerShell terminals hang and don't execute commands
**Solutions**:
- ✅ Close all PowerShell windows
- ✅ Open new PowerShell as Administrator
- ✅ Restart computer if problem persists
- ✅ Use Command Prompt instead of PowerShell

## 📊 **FINAL VERIFICATION CHECKLIST**

### **Prerequisites Verification** ✅
- [ ] **Rust toolchain**: `rustc --version` shows stable version
- [ ] **Python 3.11+**: `python --version` shows 3.11 or 3.12
- [ ] **Virtual environment**: Activated and isolated
- [ ] **MSVC compiler** (Windows): `where cl.exe` shows path
- [ ] **Build dependencies**: Exact versions installed
  - [ ] `setuptools>=75`
  - [ ] `numpy>=1.26.4`
  - [ ] `Cython==3.1.0a1`

### **Build Process Verification** ✅
- [ ] **Repository cloned**: Latest code from master branch
- [ ] **Rust compilation**: 715 packages compiled successfully
- [ ] **Key artifacts created**:
  - [ ] `nautilus_core/target/release/deps/nautilus_pyo3.dll`
  - [ ] `nautilus_core/target/release/nautilus_backtest.lib`
  - [ ] `nautilus_core/target/release/nautilus_common.lib`
  - [ ] `nautilus_core/target/release/nautilus_core.lib`
  - [ ] `nautilus_core/target/release/nautilus_model.lib`
  - [ ] `nautilus_core/target/release/nautilus_persistence.lib`
- [ ] **Python build**: 138 Cython modules compiled
- [ ] **File copy**: `nautilus_trader/core/nautilus_pyo3.cp312-win_amd64.pyd` exists
- [ ] **Poetry installation**: Dependencies installed successfully

### **Functionality Verification** ✅
- [ ] **Basic import**: `import nautilus_trader` works
- [ ] **Version check**: `nautilus_trader.__version__` shows 1.211.0
- [ ] **Core functionality**: `UUID4()` and `Bar` imports work
- [ ] **OKX adapter**: `OKXHttpClient` and `OKXWebSocketClient` import
- [ ] **Configuration**: `OKXDataClientConfig` works with `is_demo=True`
- [ ] **Testing framework**: `pytest` runs successfully

### **Performance Verification** ✅
- [ ] **Import speed**: < 5 seconds for basic imports
- [ ] **Memory usage**: Reasonable levels during operation
- [ ] **Build time**: ~60-90 minutes total (49 Rust + 4-5 Python)

### **Integration Readiness** ✅
- [ ] **Environment variables**: Detection and configuration working
- [ ] **Test infrastructure**: pytest and extensions configured
- [ ] **Development tools**: All dependencies available
- [ ] **API integration**: Ready for OKX and Supabase connections

## 🎉 **SUCCESS CONFIRMATION**

When all checklist items are complete, you should see:

```bash
✅ Rust toolchain: rustc 1.xx.x
✅ Python: 3.11.x or 3.12.x
✅ NumPy: 1.26.4+
✅ Cython: 3.1.0a1
✅ Setuptools: 75.x.x+
✅ Build dependencies ready
✅ Version: 1.211.0
✅ Core imports successful
✅ OKX adapter imports successful
✅ Configuration classes working
✅ Testing dependencies ready
```

## 🚀 **NEXT STEPS AFTER SUCCESSFUL BUILD**

1. **Configure API Credentials**: Set up OKX API and Supabase connections
2. **Run Integration Tests**: Validate real API connectivity
3. **Development Workflow**: Use Poetry for dependency management
4. **Testing**: Execute comprehensive test suites

## 📞 **SUPPORT**

For build issues:
1. ✅ Check this document's troubleshooting section first
2. ✅ Verify all prerequisites are met exactly
3. ✅ Ensure sufficient system resources (16GB+ RAM)
4. ✅ Review build logs for specific error messages
5. ✅ Try restarting computer and running again

---

**🎯 This is the ONLY build document you need. All other build documents have been archived.**

**Last Updated**: January 2025
**Build System**: Cargo + Poetry + MSVC
**Target Platform**: Cross-platform (Windows/Linux/macOS)
**Status**: ✅ COMPLETE AND TESTED
