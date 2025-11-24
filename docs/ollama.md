Setting up Ollama in WSL is pretty straightforward, but there’s one tiny wrinkle: Ollama needs **NVIDIA GPU passthrough** (if you want acceleration), and WSL needs to be configured correctly before Ollama will behave. Let’s walk through it in a clean, practical way.

Think of this as bootstrapping a small AI forge under your Windows hood.

---

## 1. Make sure WSL is ready for GPU workloads

WSL2 must be enabled and the right GPU drivers installed.

### a) Confirm WSL version

In PowerShell:

```powershell
wsl -l -v
```

Your distro should show version `WSL 2`. If not:

```powershell
wsl --set-version <your-distro-name> 2
```

### b) Install the NVIDIA CUDA driver for WSL

This is a Windows-side driver. Download from NVIDIA:
Search for “NVIDIA CUDA WSL Driver” → install it on Windows (not inside Linux).
This gives WSL access to your GPU through `/dev/nvidia*`.

Then confirm inside WSL:

```bash
nvidia-smi
```

If it prints a nice GPU table, you're golden.

---

## 2. Install Ollama inside WSL

Inside your WSL shell (Ubuntu recommended):

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Then verify:

```bash
ollama --version
```

---

## 3. Enable GPU support for Ollama (WSL-specific bit)

Create or edit the WSL config on Windows:

Open:

```
C:\Users\<you>\.wslconfig
```

Add:

```
[wsl2]
gpu=true
```

Restart WSL completely:

```powershell
wsl --shutdown
```

Then reopen your distro.

---

## 4. Run a model

Inside WSL:

```bash
ollama run llama3
```

Or if you want a small model to test:

```bash
ollama run mistral
```

---

## 5. If you want to use Ollama from Windows apps

Ollama runs on `http://localhost:11434` inside WSL, which Windows can access automatically.
But if you're scripting from Windows and want clean separation, expose:

Inside WSL:

```bash
export OLLAMA_HOST=0.0.0.0
ollama serve
```

Then Windows can hit it like:

```
http://localhost:11434/api/generate
```

---

## 6. Common errors you might hit

**“nvidia-smi: command not found”**
→ Means Windows-side CUDA GPU driver missing.

**GPU shows 0% usage in Ollama**
→ Ensure you're using an NVIDIA GPU; AMD GPU passthrough still isn’t fully supported.

**“CUDA initialization failed”**
→ Sometimes WSL boots without GPU access. Restart WSL:

```powershell
wsl --shutdown
```

---

If you want, I can help you wire it to VS Code, Docker, or automatic systemd startup under WSL so you don’t have to start Ollama manually every time.