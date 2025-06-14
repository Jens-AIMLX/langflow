# Installing Rust for Langflow Dependencies

Some Langflow dependencies (like `tiktoken`) require Rust to build. This README explains how to install Rust on your system.

## Why Rust is Needed

The error message you encountered (`error: can't find Rust compiler`) indicates that the `tiktoken` package needs to compile Rust code during installation. This is common for Python packages that use Rust for performance-critical components.

## Installing Rust

### Windows

1. Visit https://rustup.rs/ in your browser
2. Download and run the rustup-init.exe file
3. Follow the on-screen instructions (the default options are fine)
4. After installation, **restart your command prompt or PowerShell**
5. Verify the installation by running:
   ```
   rustc --version
   ```

### macOS / Linux

1. Open a terminal
2. Run the following command:
   ```
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```
3. Follow the on-screen instructions (the default options are fine)
4. After installation, either restart your terminal or run:
   ```
   source $HOME/.cargo/env
   ```
5. Verify the installation by running:
   ```
   rustc --version
   ```

## After Installing Rust

Once Rust is installed:

1. Make sure you have the correct Rust target for your Python architecture:
   ```
   # For 64-bit Python (most common)
   rustup target add x86_64-pc-windows-msvc

   # For 32-bit Python (uncommon)
   rustup target add i686-pc-windows-msvc
   ```

2. Run the `install_langflow_uv.bat` script again
3. The script will now be able to build the Rust-dependent packages

> **Important**: Architecture mismatch between Rust and Python is a common cause of build failures. Our script uses the 64-bit target by default, which matches most modern Python installations. If you're using 32-bit Python, you'll need to modify the script.

## Troubleshooting

If you still encounter issues after installing Rust:

1. Make sure you've restarted your command prompt or terminal
2. Verify that Rust is in your PATH by running `rustc --version`
3. If you're using a proxy or firewall, make sure it allows connections to Rust package repositories

## Alternative: Using Pre-built Wheels

If you continue to have issues with Rust, you can try finding pre-built wheels for the problematic packages:

1. Visit https://www.lfd.uci.edu/~gohlke/pythonlibs/
2. Search for the package (e.g., "tiktoken")
3. Download the appropriate wheel for your Python version and system architecture
4. Install it using:
   ```
   py -m uv pip install path\to\downloaded\wheel.whl
   ```

## More Information

- Rust Documentation: https://www.rust-lang.org/learn
- Rustup Documentation: https://rust-lang.github.io/rustup/
- Tiktoken Repository: https://github.com/openai/tiktoken
