<div align="center">

<img src="images/logo.png" alt="ROTTWEILER" width="220"/>

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

User --> Streamlit
Streamlit --> Pipeline

Pipeline --> SearchEngine
Pipeline --> Scraper
Pipeline --> Monitor
Pipeline --> Timeline

SearchEngine --> TorProxy
Scraper --> TorProxy
TorProxy --> OnionSites

Scraper --> BM25
BM25 --> LLM

LLM --> Claude
LLM --> OpenAI
LLM --> Gemini
LLM --> Groq
LLM --> OpenRouter
Installation
Prerequisites

Python 3.9+

Tor daemon

Docker (optional)

Local Setup
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

Access: http://localhost:8501

Docker Setup
docker-compose up -d
docker-compose logs -f
docker-compose down

Access: http://localhost:8501

Environment Configuration
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=

TOR_PROXY_HOST=localhost
TOR_PROXY_PORT=9050
MAX_WORKERS=10
TIMEOUT_SECONDS=30
Legal Notice

ROTTWEILER is provided for lawful security research and threat intelligence. Users are responsible for compliance with applicable laws.

<div align="center"> ROTTWEILER — Hunt. Analyze. Protect. </div> ```
