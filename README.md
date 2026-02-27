<div align="center">

<img src="images/logo.png" alt="ROTTWEILER" width="300"/>

# ROTTWEILER - **Dark Web Intelligence Engine**

Multi-engine Tor search with AI-powered intelligence analysis and structured report generation.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Tor](https://img.shields.io/badge/tor-required-purple.svg)](https://www.torproject.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## Overview

ROTTWEILER is a production-grade OSINT platform for systematic Tor network reconnaissance and threat intelligence analysis. Built for security researchers, threat analysts, and intelligence professionals.

---

## Interface

### Hunt Dashboard
<img src="images/screen.png" alt="Hunt Interface" width="100%"/>

*Real-time search execution with multi-engine queries, concurrent scraping, and source status tracking*

---

## Features

### Intelligence Collection
- **13 Search Engines**: Ahmia, OnionLand, Torgle, Ahmesia, Torland, Find Tor, Excavator, Onionway, Tor66, OSS, Torgol, The Deep Searches, Dark Search
- **Concurrent Scraping**: Multi-threaded content retrieval via Tor SOCKS5 proxy
- **BM25 Ranking**: Query-relevance scoring using Okapi BM25 algorithm
- **Service Monitoring**: Real-time uptime tracking of discovered onion services
- **Timeline Tracking**: Chronological logging of intelligence operations

### AI-Powered Analysis
- **Multi-Provider LLM Support**:
  - Anthropic Claude (Sonnet 4, Opus 4)
  - OpenAI GPT-4o
  - Google Gemini 2.0
  - Groq Llama 3.3 70B
  - OpenRouter
- **Intelligence Brief Generation**: Automated threat assessment and report creation
- **Export Functionality**: Download results as structured `.md` intelligence reports

### Deployment
- **Dockerized Architecture**: Container-based deployment with integrated Tor daemon
- **Secure Configuration**: Environment variable-based credential management
- **Modular Design**: Separated scraper, pipeline, monitor, and LLM components

---

## Architecture

### System Design
```
┌─────────────────────────────────────────────────────────────────┐
│                         Layer 1: User Interface                 │
│                                                                 │
│  ┌──────────┐  ┌───────────────┐  ┌──────────┐  ┌────────┐   │
│  │  User    │→ │   Streamlit   │→ │ Pipeline │→ │ Search │→  │
│  │(Browser) │  │Frontend       │  │          │  │        │   │
│  └──────────┘  │(app.py, ui.uy)│  └──────────┘  └────────┘   │
│                └───────────────┘                               │
│                                              ↓                  │
│                                         ┌────────┐  ┌──────────┐│
│                                         │  Tor   │→ │  Onion   ││
│                                         │        │  │  Sites   ││
│                                         └────────┘  └──────────┘│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Layer 2: Core Application Layer               │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Pipeline    │  │Search Engine │  │   Scraper    │         │
│  │  Controller  │  │   Module     │  │   Module     │         │
│  │(pipeline.py) │  │(tor_search.py)│  │ (scraper.py) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │  Monitoring  │  │   Timeline   │                           │
│  │   System     │  │   Tracker    │                           │
│  │(monitor.py)  │  │(timeline.py) │                           │
│  └──────────────┘  └──────────────┘                           │
│                                                                 │
│         Monitoring → Scraper → Status Tracking                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Layer 3: Intelligence Layer                  │
│                                                                 │
│  Scraper → BM25 → LLM → Intelligence Report → UI               │
│                                                                 │
│  ┌──────────────┐          ┌──────────────────────┐           │
│  │     BM25     │          │ Multi-Provider LLM   │           │
│  │   Ranking    │          │      Engine          │           │
│  │   Engine     │          │  (llm_prompt.py)     │           │
│  └──────────────┘          └──────────────────────┘           │
│                                      ↓                         │
│                            ┌──────────────────┐               │
│                            │  Anthropic       │               │
│                            │  (Claude)        │               │
│                            ├──────────────────┤               │
│                            │  OpenAI          │               │
│                            │  (GPT-4o)        │               │
│                            ├──────────────────┤               │
│                            │  Google Gemini   │               │
│                            ├──────────────────┤               │
│                            │  Groq            │               │
│                            │  (Llama 3.3)     │               │
│                            ├──────────────────┤               │
│                            │  OpenRouter      │               │
│                            └──────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Layer 4: Network Layer                    │
│                                                                 │
│  ┌──────────────────────┐          ┌──────────────────────┐   │
│  │     Tor Proxy        │    →     │      Dark Web        │   │
│  │(SOCKS5 127.0.0.1:9050)│          │    (.onion sites)    │   │
│  └──────────────────────┘          └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Layer 5: Infrastructure Layer                 │
│                                                                 │
│  ┌──────────────────────┐          ┌──────────────────────┐   │
│  │   Docker Container   │          │    Environment       │   │
│  │                      │          │     Variables        │   │
│  │                      │          │      (.env)          │   │
│  └──────────────────────┘          └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Layer | Component | Function |
|-------|-----------|----------|
| **Layer 1** | User Interface | Browser-based Streamlit frontend for query input and result visualization |
| | | Routes requests through Pipeline → Search → Tor → Onion Sites |
| **Layer 2** | Core Application | Pipeline Controller orchestrates search and scraping operations |
| | | Search Engine Module queries 13 Tor search engines |
| | | Scraper Module performs concurrent content retrieval |
| | | Monitoring System tracks service uptime and availability |
| | | Timeline Tracker maintains chronological operation logs |
| **Layer 3** | Intelligence | BM25 Ranking Engine scores results by query relevance |
| | | Multi-Provider LLM Engine generates intelligence reports |
| | | Supports Anthropic, OpenAI, Google, Groq, OpenRouter |
| **Layer 4** | Network | Tor Proxy routes all requests through SOCKS5 (127.0.0.1:9050) |
| | | Provides anonymous access to dark web .onion sites |
| **Layer 5** | Infrastructure | Docker Container encapsulates application and Tor daemon |
| | | Environment Variables manage API keys and configuration |

---

## Installation

### Prerequisites

- Python 3.9+
- Tor daemon
- Docker (optional)

### Local Installation
```bash
# Clone repository
git clone https://github.com/yourusername/rottweiler.git
cd rottweiler

# Install dependencies
pip install -r requirements.txt

# Install and start Tor
# macOS
brew install tor
brew services start tor

# Ubuntu/Debian
sudo apt update && sudo apt install tor
sudo systemctl start tor

# Configure environment variables
cp .env.example .env
nano .env  # Add your API keys

# Launch application
streamlit run app.py
```

Access at `http://localhost:8501`

### Docker Installation
```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

Access at `http://localhost:8501`

### Environment Configuration
```env
# .env file
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
GOOGLE_API_KEY=xxxxx
GROQ_API_KEY=gsk_xxxxx
OPENROUTER_API_KEY=sk-or-xxxxx

TOR_PROXY_HOST=localhost
TOR_PROXY_PORT=9050
MAX_WORKERS=10
TIMEOUT_SECONDS=30
```

---

## Usage

1. Launch application (local or Docker)
2. Enter search query in Hunt dashboard
3. Select LLM provider and model
4. Configure search engines and max results
5. Click HUNT to initiate search
6. Review results: Requested / Active Sources / Offline Sources
7. Navigate to AI Analysis tab for intelligence brief
8. Export results as `.md` report

---

## Security

- All requests routed through Tor SOCKS5 proxy
- No direct connections to .onion services
- Environment variable-based credential management
- Local-only data storage
- Docker isolation for deployment

**Legal Notice**: ROTTWEILER is provided for lawful security research and threat intelligence. Users are solely responsible for legal compliance. Do not use for illegal activities.

---

## License

MIT License - See [LICENSE](LICENSE)

---

<div align="center">

**ROTTWEILER** - Hunt. Analyze. Protect.

</div>
