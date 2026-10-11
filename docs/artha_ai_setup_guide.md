# Artha AI: Local, Privacy-First Financial LLM Setup & Architecture Guide

## 1. Overview
**Artha AI** is the local, privacy-first financial intelligence assistant for **FIN4YOU**.
It operates under a strict architectural separation of concerns:
> **"LLM understands. Python calculates. Decision Engine decides. Artha AI explains."**

Artha AI does not independently determine balances, simulate interest rates, or calculate arithmetic. Instead, it ingests verified context from the deterministic engine, retrieves relevant financial definitions from local documentation, validates every numerical claim against authoritative backend figures, and explains results in transparent, empathetic natural language.

---

## 2. Hardware Profile & Model Selection
During system profiling on the host workstation:
- **Operating System:** Windows 11 Home Single Language (64-bit)
- **RAM:** 16 GB Physical RAM (TotalVisible: 16.39 GB, ~2.6 GB available free)
- **GPU & VRAM:** NVIDIA GeForce RTX 4050 Laptop GPU with **6,141 MiB (6 GB VRAM)**, CUDA 13.1 supported (Driver: 592.82)
- **Available Storage:** >162 GB free on C: drive
- **Runtime:** Python 3.13.14 with PyTorch 2.6.0+cu124, FastAPI, Pydantic, HTTPX

### Chosen Local Model: `llama3.2:3b` (Alternative: `qwen2.5:3b`)
1. **Memory Fit:** `llama3.2:3b` requires ~2.0 GB - 2.5 GB of VRAM. It fits completely inside the RTX 4050's 6 GB VRAM, avoiding CPU swapping and leaving ample headroom for Windows desktop tasks.
2. **Speed & Latency:** Delivers high token throughput (>40 tokens/second on RTX 4050).
3. **Instruction Following & JSON:** Strong adherence to negative constraints ("Never invent numbers") and structured contracts.
4. **Privacy & Licensing:** 100% locally hosted via Ollama under permissive licensing with zero data transmission to cloud APIs.

---

## 3. Subsystem Architecture (`backend/app/artha_ai/`)

| Module | Responsibility |
| :--- | :--- |
| `config.py` | Local Ollama host (`http://127.0.0.1:11434`), model names, timeouts, and privacy flags. |
| `schemas.py` | Typed contracts: `ArthaFinancialContextContract`, `ValidationResult`, `SourceReference`. |
| `ollama_client.py` | HTTP client with localhost validation, health checks, generation/chat, and timeout/retry. |
| `prompts.py` | Hardened system prompts enforcing zero hallucinations, factuality, and prompt injection defense. |
| `context_builder.py` | Privacy-preserving context transformer implementing data minimization and PII exclusion. |
| `retrieval.py` | Lightweight local RAG engine indexing `formula_sheet.md` and repository docs with injection filtering. |
| `response_validator.py` | Deterministic grounding gatekeeper verifying numerical claims against backend values. |
| `service.py` | Facade coordinating inference, RAG, prompt assembly, validation, and deterministic fallbacks. |

---

## 4. Quickstart & Installation

### Step 1: Install Ollama
Download and install Ollama for Windows from [ollama.com](https://ollama.com) or using winget:
```powershell
winget install Ollama.Ollama
```

### Step 2: Download the Local Model
Once Ollama is installed, open PowerShell and pull the model (requires one-time network connection):
```powershell
ollama pull llama3.2:3b
# Or alternative:
ollama pull qwen2.5:3b
```

### Step 3: Verify Local Daemon
Ensure Ollama is running locally:
```powershell
# In PowerShell:
Test-NetConnection -ComputerName 127.0.0.1 -Port 11434
```
Ollama will serve endpoints at `http://127.0.0.1:11434`.

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env` or set environment variables:
```env
ARTHA_OLLAMA_HOST=http://127.0.0.1:11434
ARTHA_OLLAMA_MODEL=llama3.2:3b
ARTHA_OLLAMA_FALLBACK_MODEL=qwen2.5:3b
ARTHA_INFERENCE_TIMEOUT=30.0
ARTHA_CONNECT_TIMEOUT=5.0
ARTHA_STRICT_PRIVACY_LOGGING=true
ARTHA_FALLBACK_TO_DETERMINISTIC=true
ARTHA_RAG_ENABLED=true
ARTHA_RAG_TOP_K=3
ARTHA_TEMPERATURE=0.1
```

---

## 5. Offline Operation
After the initial model pull, **Artha AI operates completely offline**:
- No outbound internet calls are made.
- Prompts, transactions, embeddings, and context never leave `127.0.0.1`.
- If Ollama is offline or unavailable, the system automatically falls back to deterministic rule-based output without crashing.

---

## 6. Running Automated Tests

Run the Artha AI local LLM test suite and Copilot regression tests:
```powershell
# Run Artha AI tests:
python -m pytest tests/test_artha_ai.py -v

# Run full Copilot & Artha AI integration suite:
python -m pytest tests/test_artha_ai.py tests/test_copilot_api.py -v
```

All 23 unit, mock, grounding, privacy, and regression tests pass deterministically.
