<div align="center">

<img src="images/logo.png" alt="ROTTWEILER" width="300"/>

# ROTTWEILER

**Dark Web Intelligence Engine**

Multi-engine Tor search with AI-powered intelligence analysis and structured report generation.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Tor](https://img.shields.io/badge/tor-required-purple.svg)](https://www.torproject.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## Interface

### Hunt Dashboard
<img src="images/screen.png" alt="Hunt Interface" width="100%"/>

### AI Analysis Page
<img src="images/Analysis-screen.png" alt="AI Analysis" width="100%"/>

---

## Features

### Intelligence Collection
- 13 integrated Tor search engines  
- Concurrent scraping via Tor SOCKS5 proxy  
- BM25 relevance ranking (Okapi BM25)  
- Service uptime monitoring  
- Timeline-based intelligence tracking  

### AI Analysis
- Multi-provider LLM support (Claude, GPT-4o, Gemini, Groq Llama 3.3, OpenRouter)  
- Automated intelligence brief generation  
- Export results as structured `.md` reports  

### Deployment
- Dockerized architecture with integrated Tor daemon  
- Environment-based secure configuration  
- Modular scraper, pipeline, monitor, and LLM layers  

---

## Architecture
```mermaid
graph TD
    User[User Browser] --> Streamlit[Streamlit Frontend]
    Streamlit --> Pipeline[Pipeline Controller]
    Pipeline --> SearchEngine[Search Engine Module]
    Pipeline --> Scraper[Scraper Module]
    Pipeline --> Monitor[Monitoring System]
    Pipeline --> Timeline[Timeline Tracker]
    
    SearchEngine --> TorProxy[Tor Proxy SOCKS5]
    Scraper --> TorProxy
    TorProxy --> OnionSites[Dark Web Onion Sites]
    
    Scraper --> BM25[BM25 Ranking Engine]
    BM25 --> LLM[Multi-Provider LLM Engine]
    
    LLM --> Claude[Anthropic Claude]
    LLM --> OpenAI[OpenAI GPT-4o]
    LLM --> Gemini[Google Gemini]
    LLM --> Groq[Groq Llama 3.3]
    LLM --> OpenRouter[OpenRouter]
    
    style Streamlit fill:#4a5568,stroke:#cbd5e0
    style Pipeline fill:#4a5568,stroke:#cbd5e0
    style BM25 fill:#4a5568,stroke:#cbd5e0
    style LLM fill:#742a2a,stroke:#fc8181
    style Claude fill:#742a2a,stroke:#fc8181
    style OpenAI fill:#742a2a,stroke:#fc8181
    style Gemini fill:#742a2a,stroke:#fc8181
    style Groq fill:#742a2a,stroke:#fc8181
    style OpenRouter fill:#742a2a,stroke:#fc8181
    style TorProxy fill:#4a5568,stroke:#cbd5e0
```

---

## Installation

### Prerequisites

- Python 3.9+
- Tor daemon
- Docker (optional)

### Local Setup
```bash
git clone https://github.com/yourusername/rottweiler.git
cd rottweiler
pip install -r requirements.txt

# macOS
brew install tor
brew services start tor

# Ubuntu/Debian
sudo apt update && sudo apt install tor
sudo systemctl start tor

cp .env.example .env
# Add your API keys inside .env

streamlit run app.py
```

Access: `http://localhost:8501`

### Docker Setup
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

Access: `http://localhost:8501`

### Environment Configuration
```env
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=

TOR_PROXY_HOST=localhost
TOR_PROXY_PORT=9050
MAX_WORKERS=10
TIMEOUT_SECONDS=30
```

---

## Legal Notice

ROTTWEILER is provided for lawful security research and threat intelligence. Users are responsible for compliance with applicable laws.

---

<div align="center">

**ROTTWEILER** — Hunt. Analyze. Protect.

</div>
