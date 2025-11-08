# 🐍 Python Environment Setup with Pyenv and Pyenv-Virtualenv

This guide explains how to install and configure **Pyenv** and **Pyenv-Virtualenv** on macOS to manage multiple Python versions and isolated virtual environments.

---

## 📦 1. Install Dependencies

> Using **Homebrew** (recommended on macOS):

```bash
brew update
brew install pyenv pyenv-virtualenv
```

> Manual installation (without Homebrew):

```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
```

---

## ⚙️ 2. Configure Your Shell (`~/.zshrc`)

macOS uses **Zsh** as the default shell.  
Open your configuration file:

```bash
nano ~/.zshrc
```

Add the following lines **at the end** of the file:

```bash
# Pyenv setup
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

# Initialize Pyenv and Pyenv-Virtualenv
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Save and close (`Ctrl + O`, `Enter`, `Ctrl + X`).

---

## 🔄 3. Reload the Shell

Apply the configuration by running:

```bash
exec "$SHELL"
```

or simply close and reopen your terminal.

---

## 🧪 4. Verify Installation

Check that Pyenv and Virtualenv are properly loaded:

```bash
pyenv --version
pyenv virtualenvs
```

Expected output (example):

```
pyenv 2.6.12
  no virtualenvs detected
```

---

## 🐍 5. Install Python Versions

List all available versions:

```bash
pyenv install --list
```

Install a specific version:

```bash
pyenv install 3.12.12
```

Set it as your global (system-wide) version:

```bash
pyenv global 3.12.12
```

Verify it’s active:

```bash
python --version
```

---

## 🧱 6. Create a Virtual Environment

Create an isolated environment:

```bash
pyenv virtualenv 3.12.12 .venv
```

List your environments:

```bash
pyenv virtualenvs
```

Activate the environment:

```bash
pyenv activate .venv
```

If successful, your terminal prompt should change, e.g.:

```
(.venv) user@MacBook-Pro project %
```

---

## 💡 7. Auto-Activation per Project

To automatically activate the environment when entering a project directory:

```bash
pyenv local .venv
```

This creates a `.python-version` file that tells Pyenv which environment to use.

---

## 🔍 8. Useful Commands

| Command | Description |
|----------|-------------|
| `pyenv versions` | List all installed Python versions |
| `pyenv version` | Show the currently active version |
| `pyenv install -v <version>` | Install a specific version of Python |
| `pyenv uninstall <version>` | Remove a specific version |
| `pyenv deactivate` | Deactivate the current virtual environment |
| `pyenv update` | Update Pyenv and all plugins |

---

## 🧼 9. Troubleshooting

**Error:**
```
`pyenv activate' requires Pyenv and Pyenv-Virtualenv to be loaded into your shell.
```

✅ **Fix:**
Make sure your `~/.zshrc` contains the three initialization lines:

```bash
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Then reload your shell:

```bash
exec "$SHELL"
```

---

## 📚 Official References

- [Pyenv Documentation](https://github.com/pyenv/pyenv)
- [Pyenv-Virtualenv Plugin](https://github.com/pyenv/pyenv-virtualenv)
- [Python.org Downloads](https://www.python.org/downloads/)

---

> 🧠 **Tip:**  
> You can combine Pyenv with tools like `poetry` or `pip-tools` for even better dependency management.
