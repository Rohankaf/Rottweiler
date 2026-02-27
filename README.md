<div align="center">
  <img src="images/logo.png" width="350">
</div>

<h1 align="center">ROTTWEILER</h1>
<p align="center"><strong>Dark Web Intelligence Engine</strong></p>

Multi-engine Tor search with AI-powered intelligence analysis and structured report generation.

---

## Interface

### Hunt Dashboard
![Hunt Interface](images/screen.png)

### AI Analysis Page
![AI Analysis](images/Analysis-screen.png)

---

## Features

- 13 integrated Tor search engines  
- Concurrent scraping via Tor SOCKS proxy  
- BM25 relevance ranking  
- Multi-provider LLM analysis (Claude, GPT-4o, Gemini, Groq, OpenRouter)  
- Dedicated AI Analysis page with intel brief generation  
- Export results as downloadable `.md` intelligence reports  
- Docker-based deployment with integrated Tor daemon  

---

## Architecture
Streamlit Interface
│
┌──────┴──────┐
Scraper LLM
│
Pipeline
(Tor • BM25 • Cache)
│
Monitor


---

## Installation

### Local

```bash
git clone https://github.com/yourusername/rottweiler.git
cd rottweiler
pip install -r requirements.txt

# Start Tor
brew install tor        # macOS
sudo apt install tor    # Linux

streamlit run app.py
Docker
docker-compose up -d

Access: http://localhost:8501


---

This version:

- Adds your AI Analysis image properly  
- Keeps README clean and professional  
- Removes unnecessary sections  
- Keeps it short but powerful  

If you want, I can make it look even more premium like a production SaaS repo layout.
