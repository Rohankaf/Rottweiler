# ROTTWEILER

![ROTTWEILER Logo](/logo-rott.png)

**Advanced Dark Web Intelligence and OSINT Engine**

A production-grade tool for systematic Tor network reconnaissance, onion service discovery, and intelligence analysis with integrated LLM-powered threat assessment.

---

## Features

- **Multi-Engine Search**: Queries Ahmia, Torch, and Onionland simultaneously
- **Concurrent Scraping**: Thread-pooled content retrieval via Tor SOCKS proxy
- **BM25 Ranking**: Relevance-based result ordering
- **Multi-Provider LLM Analysis**: Support for Anthropic Claude, OpenAI GPT-4o, Google Gemini, Groq Llama 3.3 70B, and OpenRouter
- **Monitoring System**: Tracks uptime and availability of discovered onion services
- **Timeline Tracking**: Maintains operational chronology
- **Dockerized Deployment**: Container-based deployment with integrated Tor daemon
- **Secure Configuration**: Environment variable-based API key management

---

## Architecture

### Core Components

**Search Module** (`modules/scraper.py`)
- Interfaces with Tor search engines
- Extracts and validates .onion URLs
- Handles Tor proxy configuration

**Pipeline Module** (`modules/pipeline.py`)
- Concurrent scraping engine with thread pools
- Tor SOCKS proxy integration
- BM25 ranking implementation
- Caching layer for performance

**Monitor Module** (`modules/monitor.py`)
- Uptime tracking for discovered services
- Availability checking via Tor proxy
- Historical status logging

**LLM Module** (`modules/llm.py`)
- Abstraction layer for multiple providers
- Unified interface for all supported LLMs
- Context-aware prompt engineering

**Streamlit Interface** (`app.py`)
- Query input and configuration
- Real-time search progress visualization
- Result presentation and monitoring dashboard

---

## Installation

### Local Installation
```bash
# Clone repository
git clone https://github.com/yourusername/rottweiler.git
cd rottweiler

# Install dependencies
pip install -r requirements.txt

# Install Tor
# Ubuntu/Debian:
sudo apt update && sudo apt install tor
sudo systemctl start tor

# macOS:
brew install tor
brew services start tor

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run application
streamlit run app.py
```

### Docker Deployment
```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Access at http://localhost:8501
```

### Environment Variables

Create a `.env` file:
```env
# LLM API Keys (configure only what you need)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here

# Tor Configuration
TOR_PROXY_HOST=localhost
TOR_PROXY_PORT=9050

# Application Settings
MAX_WORKERS=10
TIMEOUT_SECONDS=30
```

---

## Usage

1. Launch the application (local or Docker)
2. Enter a search query related to your intelligence objective
3. Select LLM provider and model
4. Execute search and review results in Summary, Details, and Monitoring tabs

---

## Security Considerations

- All requests routed through Tor SOCKS proxy
- No hardcoded credentials
- Local-only data storage
- Operators responsible for legal compliance
- Use only for lawful security research

---

## Disclaimer

ROTTWEILER is provided for lawful security research and threat intelligence. Users are solely responsible for compliance with applicable laws. This tool must not be used for illegal access, downloading illegal content, or any prohibited activities. No warranty provided.

---

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Docker](https://img.shields.io/badge/docker-supported-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![Tor](https://img.shields.io/badge/tor-required-purple.svg)

---

**MIT License** | For issues or contributions, open an issue on GitHub
