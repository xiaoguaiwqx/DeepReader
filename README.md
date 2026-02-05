# DeepReader: AI-Powered Research Assistant & Knowledge Manager

## 📖 Project Overview
**DeepReader** (Project Code: `ScholarFlow`) is an intelligent, automated system designed to streamline the workflow of tracking, summarizing, and managing academic research papers (focusing on AI/LLM domains). 

It automates the process of discovering new papers from ArXiv, summarizing them using LLMs, archiving them in a local database, and delivering personalized insights via email. It also aims to bridge the gap between research and engineering by linking papers to their GitHub implementations and generating actionable CLI skills.

## 🌟 Key Features

### 1. Automated Discovery & Collection
- **Multi-Source Fetching**: Automatically fetches the latest papers from **ArXiv** (and potentially Semantic Scholar) based on user-defined keywords (e.g., `MLLM`, `Data Synthesis`, `Data Selection`).
- **GitHub Correlation**: Searches for and links relevant GitHub repositories associated with the papers.

### 2. Intelligent Processing (The "Intel" Engine)
- **AI Summarization**: Uses Large Language Models (LLM) to generate structured, high-quality summaries in Chinese/English.
  - *Structure*: Problem Definition, Methodology, Key Results, Limitations.
- **Auto-Tagging**: Automatically categorizes papers into specific sub-domains.

### 3. Local Knowledge Base (The "Vault")
- **Persistent Storage**: Stores metadata and AI summaries in a local **SQLite** database.
- **Vector Search**: Embeds paper summaries into **ChromaDB** to enable semantic search and personalized recommendations.
- **Offline Access**: (Future) Option to download and index full PDFs.

### 4. Smart Notification & Recommendation
- **Daily Briefing**: Sends a scheduled email report containing the latest discoveries.
- **Fallback Recommendation**: If no new papers match the criteria, the system uses **RAG (Retrieval-Augmented Generation)** to recommend highly relevant historical papers from the Vault based on user reading habits.

### 5. Interactive Dashboard (Web UI)
- **Modern UI**: A clean, responsive web interface (built with Next.js/Streamlit) to browse the library, search papers, and manage settings.
- **Chat with Papers**: (Future) An interface to Q&A with the local knowledge base.

### 6. Skill Generation (Advanced)
- **Repo-to-Skill**: Analyzes a linked GitHub repository's `README` and code to generate a ready-to-use **Gemini CLI Skill** configuration, facilitating immediate experimentation.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+ (FastAPI)
- **Frontend**: Next.js (React) or Streamlit
- **Database**: 
  - Metadata: SQLite
  - Vector Store: ChromaDB
- **LLM Integration**: Google Gemini API / OpenAI API / Ollama (Local)
- **Scheduling**: APScheduler (Python)
- **Containerization**: Docker & Docker Compose

---

## 📅 Roadmap & Phases

### Phase 1: The Core Loop (MVP)
- [ ] Set up Python environment and project structure.
- [ ] Implement `Collector` module to fetch papers from ArXiv API.
- [ ] Implement `Storage` module with SQLite.
- [ ] Implement basic `Notifier` (SMTP Email) for daily updates.
- [ ] **Goal**: A background script that runs daily, fetches papers, and emails a raw list.

### Phase 2: Intelligence & UI
- [ ] Integrate LLM for structured summarization (Abstract -> Briefing).
- [ ] Develop the Web Dashboard (Paper list, Search, Configuration).
- [ ] Integrate ChromaDB for vector embeddings of summaries.
- [ ] Implement "Fallback Recommendation" logic in the Notifier.
- [ ] **Goal**: A usable web app with intelligent summaries and smart recommendations.

### Phase 3: Engineering Integration
- [ ] Implement GitHub API search to find code repositories.
- [ ] Develop the "Skill Generator" prototype (Repo -> XML Skill).
- [ ] Add "Chat with Papers" feature in Web UI.
- [ ] **Goal**: A complete research-to-engineering bridge.

---

## 🤝 Collaboration & Workflow (GitHub Flow)

We follow the **GitHub Flow** for development to ensure a clean and deployable `main` branch.

### 1. The `main` Branch
- The `main` branch always contains deployable, stable code.
- **Do not commit directly to `main`** (except for initial setup or documentation fixes).

### 2. Feature Branches
- For every new feature, bug fix, or experiment, create a new branch from `main`.
- **Naming Convention**:
  - `feature/add-arxiv-collector`
  - `fix/email-encoding-error`
  - `docs/update-readme`

### 3. Commit Messages
- Use clear, descriptive commit messages.
- Format: `[Module] Action: Description`
  - Example: `[Collector] Feat: Add support for filtering by date`
  - Example: `[UI] Fix: Resolve layout issue on mobile`

### 4. Pull Requests (PR)
- When development on a branch is ready (or for feedback), open a **Pull Request** to `main`.
- Describe the changes, link related issues, and provide screenshots if applicable.
- Wait for code review (or self-review) before merging.

### 5. Merge & Deploy
- Once approved, merge the PR into `main`.
- Delete the feature branch after merging.


