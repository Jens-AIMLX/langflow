# Using Trunk for Standardized Code Formatting

## 1. Introduction & Purpose

To maintain a consistent, clean, and readable codebase across the entire project, we use **Trunk** as our primary code formatting and linting tool. Enforcing a single format prevents style-related debates and makes code reviews more efficient by focusing on logic rather than style.

Adherence to this formatting standard is mandatory for all contributors.

## 2. How to Format the Code

The primary tool for ensuring compliance is the `trunk.ps1` script located in the project root.

### Running the Formatter

To automatically format all relevant files in the project, open a PowerShell terminal in the root directory of the project and execute the following command:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\trunk.ps1 fmt
```

### What the Command Does

- `powershell.exe -ExecutionPolicy Bypass`: This ensures the script can run even if the system's execution policy is restrictive.
- `-File .\trunk.ps1`: Specifies the script to run.
- `fmt`: This is the argument passed to the Trunk script, telling it to run the formatting tools (like `black`, `prettier`, etc.) configured in the `.trunk/trunk.yaml` file.

The script will check all files and automatically correct any formatting issues it finds.

## 3. When to Format

Developers should format their code at the following times:

1.  **Before committing changes:** Always run the formatter on your staged files before creating a commit. This ensures that no poorly formatted code enters the version history.
2.  **After pulling changes:** It's good practice to run the formatter after pulling changes from the remote repository to resolve any potential merge conflicts related to formatting.
3.  **During development:** Feel free to run the formatter at any time during your work to keep your code clean.

## 4. CI/CD Integration

The same Trunk command (`trunk check`) is integrated into our Continuous Integration (CI) pipeline. Pull requests containing code that does not adhere to the formatting standards will fail the CI checks. This acts as a final safeguard to keep the main branch clean.

By following this simple process, we contribute to a higher-quality and more maintainable codebase.
