# ROTTWEILER

**Advanced Dark Web Intelligence and OSINT Engine**

A production-grade tool for systematic Tor network reconnaissance, onion service discovery, and intelligence analysis with integrated LLM-powered threat assessment.

---

## Overview

ROTTWEILER is a specialized dark web intelligence platform designed for security researchers, threat analysts, and OSINT professionals. It provides automated discovery, concurrent scraping, relevance ranking, and multi-provider LLM analysis of Tor hidden services.

Built with a modular architecture, ROTTWEILER supports multiple search engines, concurrent Tor-proxied requests, and configurable LLM backends for automated intelligence extraction from dark web sources.

**Value Proposition:**
- Systematic onion service discovery across multiple search engines
- Concurrent, Tor-proxied content retrieval with configurable thread pools
- BM25-based relevance ranking for query-focused results
- Multi-provider LLM analysis (Anthropic, OpenAI, Google, Groq, OpenRouter)
- Uptime monitoring system for discovered services
- Timeline tracking for intelligence operations
- Dockerized deployment for operational security

---

## Key Features

- **Multi-Engine Search**: Queries multiple Tor search engines simultaneously (Ahmia, Torch, Onionland)
- **Onion Link Extraction**: Automatic .onion URL discovery and validation
- **Concurrent Scraping**: Thread-pooled content retrieval via Tor SOCKS proxy
- **BM25 Ranking**: Information retrieval scoring for relevance-based result ordering
- **LLM Analysis Layer**: Configurable backend support for:
  - Anthropic Claude (claude-sonnet-4-20250514, claude-opus-4-20250514)
  - OpenAI GPT-4o (gpt-4o, gpt-4o-mini)
  - Google Gemini (gemini-2.0-flash-exp, gemini-1.5-pro)
  - Groq (llama-3.3-70b-versatile)
  - OpenRouter (multiple model routing)
- **Monitoring System**: Tracks uptime and availability of discovered onion services
- **Timeline Tracking**: Maintains operational chronology of discovered services
- **Modular Architecture**: Separated scraper, pipeline, monitor, and LLM components
- **Streamlit Interface**: Clean web UI for query submission and result visualization
- **Dockerized Deployment**: Container-based deployment with Tor daemon integration
- **Secure Configuration**: Environment variable-based API key and configuration management

---

## Architecture

ROTTWEILER is designed with a modular, pipeline-based architecture:

### Components

**Search Module (`modules/scraper.py`)**
- Interfaces with Tor search engines (Ahmia, Torch, Onionland)
- Extracts and validates .onion URLs from search results
- Handles Tor proxy configuration and connection management

**Pipeline Module (`modules/pipeline.py`)**
- Concurrent scraping engine with configurable thread pools
- Tor SOCKS proxy integration for anonymous requests
- Content extraction and preprocessing
- BM25 ranking implementation for result relevance
- Caching layer for performance optimization

**Monitor Module (`modules/monitor.py`)**
- Uptime tracking for discovered onion services
- Availability checking via Tor proxy
- Historical status logging
- Service health metrics

**LLM Module (`modules/llm.py`)**
- Abstraction layer for multiple LLM providers
- Unified interface for Anthropic, OpenAI, Google, Groq, OpenRouter
- Context-aware prompt engineering for threat intelligence
- Error handling and fallback logic

**Streamlit Interface (`app.py`)**
- Query input and configuration
- Real-time search progress visualization
- Tabbed result presentation (Summary, Details, Monitoring)
- LLM provider selection and model configuration

---

## Installation

### Prerequisites

- Python 3.9 or higher
- Tor daemon (installed and running)
- Docker and Docker Compose (for containerized deployment)

### Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/rottweiler.git
cd rottweiler
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install and configure Tor**

On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install tor
sudo systemctl start tor
sudo systemctl enable tor
```

On macOS:
```bash
brew install tor
brew services start tor
```

4. **Configure environment variables**

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` with your API keys (see Environment Variables section below).

5. **Verify Tor connectivity**
```bash
curl --socks5-hostname localhost:9050 https://check.torproject.org
```

6. **Run the application**
```bash
streamlit run app.py
```

Access the interface at `http://localhost:8501`

---

## Environment Variables

Create a `.env` file in the project root with the following structure:
```env
# Anthropic Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Groq Configuration
GROQ_API_KEY=your_groq_api_key_here

# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Tor Configuration (default values)
TOR_PROXY_HOST=localhost
TOR_PROXY_PORT=9050

# Application Configuration
MAX_WORKERS=10
TIMEOUT_SECONDS=30
```

**Note**: Only configure API keys for the LLM providers you intend to use. Missing keys for unused providers will not affect functionality.

---

## Docker Deployment

ROTTWEILER includes a Docker Compose configuration with integrated Tor daemon.

### Build and Run

1. **Ensure `.env` file is configured**

2. **Build the containers**
```bash
docker-compose build
```

3. **Start the services**
```bash
docker-compose up -d
```

4. **Access the application**

Navigate to `http://localhost:8501`

5. **View logs**
```bash
docker-compose logs -f
```

6. **Stop the services**
```bash
docker-compose down
```

### Docker Configuration

The `docker-compose.yml` includes:
- Tor daemon container (official Tor image)
- ROTTWEILER application container (Streamlit + dependencies)
- Network isolation for Tor proxy communication
- Volume mounting for persistent data

---

## Usage Guide

### Basic Search Workflow

1. **Launch the application** (local or Docker)

2. **Enter a search query**
   - Use targeted keywords related to your intelligence objective
   - Example: "ransomware marketplace", "leaked database", "exploit forum"

3. **Select LLM provider and model**
   - Choose based on your requirements (speed, depth, cost)
   - Claude recommended for structured analysis
   - GPT-4o for conversational insights
   - Gemini for multimodal tasks
   - Groq for high-speed inference

4. **Configure search parameters** (optional)
   - Max results per engine
   - Concurrent workers
   - Timeout values

5. **Execute search**
   - ROTTWEILER queries multiple Tor search engines
   - Extracts onion URLs from results
   - Scrapes content concurrently via Tor proxy
   - Ranks results using BM25 relevance scoring

6. **Review results**
   - **Summary Tab**: LLM-generated intelligence summary
   - **Details Tab**: Full content of discovered services
   - **Monitoring Tab**: Uptime and availability metrics

### Advanced Usage

**Monitoring Discovered Services**

ROTTWEILER automatically adds discovered onion services to the monitoring system. Access monitoring data via the Monitoring tab to track:
- Service availability over time
- Uptime percentage
- Last successful check timestamp
- Historical status changes

**Timeline Tracking**

The system maintains a chronological record of discovered services, enabling:
- Temporal analysis of dark web infrastructure
- Discovery pattern identification
- Historical service availability trends

---

## LLM Configuration

### Provider Selection

ROTTWEILER supports multiple LLM backends. Select based on operational requirements:

| Provider | Models | Use Case |
|----------|--------|----------|
| **Anthropic Claude** | claude-sonnet-4-20250514, claude-opus-4-20250514 | Structured threat intelligence, detailed analysis |
| **OpenAI** | gpt-4o, gpt-4o-mini | Conversational insights, rapid prototyping |
| **Google Gemini** | gemini-2.0-flash-exp, gemini-1.5-pro | Multimodal analysis, large context windows |
| **Groq** | llama-3.3-70b-versatile | High-speed inference, cost optimization |
| **OpenRouter** | Multiple models | Model routing, fallback strategies |

### Prompt Engineering

The LLM module uses context-aware prompts optimized for:
- Threat intelligence extraction
- Infrastructure pattern recognition
- Service categorization
- Risk assessment
- Indicator of Compromise (IOC) identification

Prompts are designed to minimize hallucination and maximize factual accuracy.

---

## Monitoring System

### Overview

The monitoring subsystem tracks availability and uptime of discovered onion services.

### Features

- **Periodic Health Checks**: Automated connectivity tests via Tor proxy
- **Uptime Calculation**: Percentage-based availability metrics
- **Status Logging**: Historical record of service state changes
- **Visualization**: Real-time monitoring dashboard in Streamlit interface

### Implementation

Monitoring is implemented as a background process that:
1. Maintains a database of discovered onion URLs
2. Performs periodic HTTP requests via Tor SOCKS proxy
3. Records response status and timing
4. Calculates uptime metrics
5. Updates Streamlit interface with current status

### Use Cases

- Tracking persistence of threat actor infrastructure
- Identifying takedown events
- Measuring service stability
- Building temporal threat models

---

## Security Considerations

### Operational Security

**Tor Usage**
- All dark web requests are routed through Tor SOCKS proxy
- No direct connections to .onion services
- Tor circuit isolation per request (configurable)

**API Key Management**
- Environment variable-based configuration
- No hardcoded credentials in source code
- `.env` file excluded from version control via `.gitignore`

**Data Handling**
- Scraped content stored locally only
- No data transmission to third parties (except LLM providers)
- Clear data retention policies required by operator

### Legal and Ethical Considerations

- ROTTWEILER is designed for lawful security research and threat intelligence
- Operators are responsible for compliance with applicable laws
- Accessing illegal content is the responsibility of the user
- No warranty or liability for misuse

### Recommendations

1. **Isolate deployment environment**: Use dedicated VM or container
2. **Secure API keys**: Use secrets management (HashiCorp Vault, AWS Secrets Manager)
3. **Monitor Tor logs**: Ensure proper circuit isolation
4. **Implement access controls**: Restrict application access to authorized personnel
5. **Maintain audit logs**: Track all queries and discovered services
6. **Regular security updates**: Keep dependencies patched

---

## Roadmap

### Planned Features

**Enhanced Search Capabilities**
- Additional Tor search engine integrations (DarkSearch, Not Evil)
- Advanced query operators (Boolean, proximity, fuzzy matching)
- Search result deduplication across engines

**Intelligence Automation**
- Automated IOC extraction (Bitcoin addresses, email addresses, PGP keys)
- Entity recognition and relationship mapping
- Automated report generation with structured output

**Monitoring Enhancements**
- Configurable check intervals
- Alert system for service status changes
- Historical trend analysis and visualization
- Bulk monitoring from onion URL lists

**Analysis Improvements**
- Multi-document summarization
- Cross-reference analysis across discovered services
- Threat actor profiling
- Content classification (marketplace, forum, leak site, etc.)

**Platform Enhancements**
- REST API for programmatic access
- Database backend for persistent storage (PostgreSQL, MongoDB)
- Multi-user support with role-based access control
- Export functionality (JSON, CSV, STIX/TAXII)

### Performance Optimization

- Improved caching mechanisms
- Connection pooling for Tor proxy
- Asynchronous scraping with `asyncio`
- Result streaming for large datasets

---

## Disclaimer

### Legal Notice

ROTTWEILER is provided for lawful security research, threat intelligence, and open-source intelligence gathering. Users are solely responsible for compliance with all applicable laws and regulations in their jurisdiction.

### Intended Use

This tool is intended for:
- Security researchers conducting threat intelligence
- Law enforcement agencies investigating cybercrime
- Corporate security teams monitoring dark web threats
- Academic researchers studying dark web ecosystems

### Prohibited Use

This tool must not be used for:
- Illegal access to computer systems
- Downloading, distributing, or accessing illegal content
- Harassment, stalking, or invasion of privacy
- Any activity prohibited by applicable law

### No Warranty

ROTTWEILER is provided "as is" without warranty of any kind, express or implied. The authors assume no liability for damages resulting from the use of this software.

### Ethical Responsibility

Users are expected to:
- Respect privacy and data protection laws
- Obtain necessary authorizations before conducting research
- Report discovered illegal content to appropriate authorities
- Use the tool responsibly and ethically

### Tor Network

ROTTWEILER relies on the Tor network for anonymity. Users should understand:
- Tor provides anonymity but not perfect security
- Correlation attacks and traffic analysis are possible
- Exit node operators can monitor unencrypted traffic
- Proper operational security practices are essential

---

## Badges

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Docker](https://img.shields.io/badge/docker-supported-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![Tor](https://img.shields.io/badge/tor-required-purple.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## License

MIT License - See LICENSE file for details

---

## Contributing

Contributions are welcome. Please submit pull requests with:
- Clear description of changes
- Test coverage for new features
- Documentation updates
- Adherence to existing code style

---

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**ROTTWEILER** - Professional Dark Web Intelligence Platform
