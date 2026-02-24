# claude_ai.py
# Multi-provider LLM backend for ROTTWEILER
# Supports: Anthropic Claude, OpenAI GPT, Google Gemini, Groq, OpenRouter
# Prompts adapted from professional CTI analyst templates (llm.py)

import os
import warnings
import logging
from typing import List, Dict, Optional

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# THREAT INTELLIGENCE PROMPTS
# Professional CTI analyst prompts — adapted for dark web OSINT automation
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    # ── General dark web OSINT brief ────────────────────────────────────────
    "intel_brief": """
You are a Cybercrime Threat Intelligence Expert. Analyze dark web OSINT search results and generate a concise intelligence brief.

Rules:
1. Analyze the discovered .onion sites using their titles and scraped content.
2. Identify notable patterns, threat categories, and active services.
3. Surface key intelligence artifacts: marketplaces, forums, threat actors, malware, crypto addresses, leaked data references.
4. Generate 3–5 specific, actionable insights based on the data.
5. Be factual, analytical, and objective. Ignore NSFW content.
6. Format as a terminal-style intelligence summary starting with: INTEL BRIEF:

Output Format:
INTEL BRIEF:
[2–3 sentence executive summary of what was found]

KEY FINDINGS:
• [Finding 1]
• [Finding 2]
• [Finding 3]

THREAT CATEGORIES OBSERVED:
[Comma-separated list]

ARTIFACTS IDENTIFIED:
[Notable indicators: forum names, markets, actors, malware, crypto, domains]

RECOMMENDED NEXT QUERIES:
[2–3 follow-up search terms for deeper investigation]
""",

    # ── Full threat intelligence report ─────────────────────────────────────
    "threat_intel": """
You are a Cybercrime Threat Intelligence Expert tasked with generating context-based technical investigative insights from dark web OSINT search engine results.

Rules:
1. Analyze the dark web OSINT data provided using links and their raw scraped text.
2. Output the Source Links referenced for the analysis.
3. Provide a detailed, contextual, evidence-based technical analysis.
4. Surface intelligence artifacts with context: names, emails, phones, cryptocurrency addresses, domains, dark web markets, forum names, threat actor info, malware names, TTPs.
5. Generate 3–5 key insights — specific, actionable, context-based, and data-driven.
6. Include suggested next steps and follow-up queries.
7. Be objective and analytical. Ignore NSFW content.

Output Format:
1. INPUT QUERY: {query}
2. SOURCE LINKS REFERENCED — all .onion links used in the analysis
3. INVESTIGATION ARTIFACTS — technical IOCs: emails, crypto, domains, actors, malware, markets, forums
4. KEY INSIGHTS — numbered, specific, evidence-backed
5. NEXT STEPS — follow-up search queries and investigative actions

Format with clear section headings.
""",

    # ── Ransomware / malware focus ───────────────────────────────────────────
    "ransomware_malware": """
You are a Malware and Ransomware Intelligence Expert analyzing dark web data for malware-related threats.

Rules:
1. Analyze the dark web OSINT data using links and raw scraped text.
2. Output the Source Links referenced.
3. Focus on: ransomware groups, malware families, exploit kits, attack infrastructure.
4. Identify malware IOCs: file hashes, C2 domains/IPs, staging URLs, payload names, obfuscation techniques.
5. Map TTPs to MITRE ATT&CK where possible.
6. Identify victim organizations, sectors, or geographies mentioned.
7. Generate 3–5 insights focused on threat actor behavior and malware evolution.
8. Include next steps for containment, detection, and further hunting.
9. Be objective. Ignore NSFW content.

Output Format:
1. INPUT QUERY: {query}
2. SOURCE LINKS REFERENCED
3. MALWARE / RANSOMWARE INDICATORS — hashes, C2s, payload names, TTPs, MITRE mappings
4. THREAT ACTOR PROFILE — group name, aliases, known victims, sector targeting
5. KEY INSIGHTS
6. NEXT STEPS — hunting queries, detection rules, further investigation

Format with clear section headings.
""",

    # ── Personal identity / PII exposure ────────────────────────────────────
    "personal_identity": """
You are a Personal Threat Intelligence Expert analyzing dark web data for identity and personal information exposure.

Rules:
1. Analyze the dark web OSINT data using links and raw scraped text.
2. Output the Source Links referenced.
3. Focus on PII: names, emails, phones, addresses, SSNs, passport data, financial account details.
4. Identify breach sources, data brokers, and marketplaces selling personal data.
5. Assess exposure severity: what data is available and how actionable it is for a threat actor.
6. Generate 3–5 insights on exposure risk.
7. Include protective actions and further investigation queries.
8. Handle all personal data with discretion. Ignore NSFW content.

Output Format:
1. INPUT QUERY: {query}
2. SOURCE LINKS REFERENCED
3. EXPOSED PII ARTIFACTS — type, value, source context
4. BREACH / MARKETPLACE SOURCES IDENTIFIED
5. EXPOSURE RISK ASSESSMENT — severity rating and rationale
6. KEY INSIGHTS
7. NEXT STEPS — protective actions, further queries

Format with clear section headings.
""",

    # ── Corporate espionage / data leaks ────────────────────────────────────
    "corporate_espionage": """
You are a Corporate Intelligence Expert analyzing dark web data for corporate data leaks and espionage activity.

Rules:
1. Analyze the dark web OSINT data using links and raw scraped text.
2. Output the Source Links referenced.
3. Focus on leaked corporate data: credentials, source code, internal documents, financial records, employee data, customer databases.
4. Identify threat actors, insider threat indicators, and data broker activity targeting the organization.
5. Assess business impact: competitive or operational damage from the exposure.
6. Generate 3–5 insights on the corporate risk posture.
7. Include recommended IR steps and further investigation queries.
8. Be objective and analytical. Ignore NSFW content.

Output Format:
1. INPUT QUERY: {query}
2. SOURCE LINKS REFERENCED
3. LEAKED CORPORATE ARTIFACTS — credentials, documents, source code, databases
4. THREAT ACTOR / BROKER ACTIVITY
5. BUSINESS IMPACT ASSESSMENT
6. KEY INSIGHTS
7. NEXT STEPS — IR actions, legal considerations, further queries

Format with clear section headings.
""",
}

# ══════════════════════════════════════════════════════════════════════════════
# MODEL REGISTRY
# Maps display name → provider info used by _build_client()
# ══════════════════════════════════════════════════════════════════════════════

MODEL_REGISTRY: Dict[str, Dict] = {
    # Anthropic Claude
    "Claude Sonnet 3.5":   {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
    "Claude Sonnet":       {"provider": "anthropic", "model": "claude-3-5-sonnet-latest"},
    "Claude Haiku":        {"provider": "anthropic", "model": "claude-3-haiku-20240307"},
    "Claude Opus":         {"provider": "anthropic", "model": "claude-3-opus-20240229"},
    # OpenAI
    "GPT-4o":              {"provider": "openai",    "model": "gpt-4o"},
    "GPT-4o Mini":         {"provider": "openai",    "model": "gpt-4o-mini"},
    "GPT-4 Turbo":         {"provider": "openai",    "model": "gpt-4-turbo"},
    # Google Gemini
    "Gemini 1.5 Pro":      {"provider": "google",    "model": "gemini-1.5-pro"},
    "Gemini 1.5 Flash":    {"provider": "google",    "model": "gemini-1.5-flash"},
    # Groq (fast inference)
    "Llama 3 70B (Groq)":  {"provider": "groq",      "model": "llama3-70b-8192"},
    "Llama 3 8B (Groq)":   {"provider": "groq",      "model": "llama3-8b-8192"},
    "Mixtral (Groq)":      {"provider": "groq",      "model": "mixtral-8x7b-32768"},
    # OpenRouter (proxy to many models)
    "Llama 3 (OR)":        {"provider": "openrouter", "model": "meta-llama/llama-3-70b-instruct"},
    "GPT-4o (OR)":         {"provider": "openrouter", "model": "openai/gpt-4o"},
    "Claude Sonnet (OR)":  {"provider": "openrouter", "model": "anthropic/claude-3.5-sonnet"},
    "Mistral Large (OR)":  {"provider": "openrouter", "model": "mistralai/mistral-large"},
}

# Human-readable display names for the sidebar selector
MODEL_DISPLAY_NAMES = list(MODEL_REGISTRY.keys())


# ══════════════════════════════════════════════════════════════════════════════
# PROVIDER CLIENTS
# ══════════════════════════════════════════════════════════════════════════════

def _call_anthropic(model: str, system: str, user: str, max_tokens: int) -> str:
    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "[ANTHROPIC_API_KEY not set]"
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text


def _call_openai(model: str, system: str, user: str, max_tokens: int,
                 base_url: Optional[str] = None, api_key_env: str = "OPENAI_API_KEY") -> str:
    from openai import OpenAI
    api_key = os.getenv(api_key_env, "")
    if not api_key:
        return f"[{api_key_env} not set]"
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    resp = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return resp.choices[0].message.content


def _call_google(model: str, system: str, user: str, max_tokens: int) -> str:
    try:
        import google.generativeai as genai
    except ImportError:
        return "[google-generativeai not installed. Run: pip install google-generativeai]"
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        return "[GOOGLE_API_KEY not set]"
    genai.configure(api_key=api_key)
    gemini = genai.GenerativeModel(
        model_name=model,
        system_instruction=system,
        generation_config={"max_output_tokens": max_tokens},
    )
    resp = gemini.generate_content(user)
    return resp.text


def _call_groq(model: str, system: str, user: str, max_tokens: int) -> str:
    try:
        from groq import Groq
    except ImportError:
        return "[groq not installed. Run: pip install groq]"
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return "[GROQ_API_KEY not set]"
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return resp.choices[0].message.content


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CLASS
# ══════════════════════════════════════════════════════════════════════════════

class ClaudeAI:
    """
    Multi-provider LLM client for ROTTWEILER.
    Drop-in replacement for the original Anthropic-only ClaudeAI.
    model_name must be a key from MODEL_REGISTRY (or MODEL_DISPLAY_NAMES).
    """

    def __init__(self, model_name: str = "Claude Sonnet"):
        self.set_model(model_name)

    def set_model(self, model_name: str):
        """Switch active model at runtime (called from sidebar selector)."""
        if model_name not in MODEL_REGISTRY:
            # Graceful fallback
            logging.warning("Unknown model '%s', falling back to Claude Sonnet", model_name)
            model_name = "Claude Sonnet"
        self.model_name = model_name
        cfg = MODEL_REGISTRY[model_name]
        self.provider  = cfg["provider"]
        self.model_id  = cfg["model"]

    # ── Internal dispatcher ────────────────────────────────────────────────
    def _call(self, system: str, user: str, max_tokens: int = 1200) -> str:
        try:
            if self.provider == "anthropic":
                return _call_anthropic(self.model_id, system, user, max_tokens)

            elif self.provider == "openai":
                return _call_openai(self.model_id, system, user, max_tokens)

            elif self.provider == "google":
                return _call_google(self.model_id, system, user, max_tokens)

            elif self.provider == "groq":
                return _call_groq(self.model_id, system, user, max_tokens)

            elif self.provider == "openrouter":
                return _call_openai(
                    self.model_id, system, user, max_tokens,
                    base_url="https://openrouter.ai/api/v1",
                    api_key_env="OPENROUTER_API_KEY",
                )
            else:
                return f"[Unknown provider: {self.provider}]"

        except Exception as e:
            return f"[{self.model_name} API error: {e}]"

    # ── Public API (same interface as original ClaudeAI) ───────────────────

    def summarize_results(self, query: str, sites: List[Dict],
                          preset: str = "intel_brief") -> str:
        """
        Generate an intelligence brief from discovered sites.
        preset: one of the PROMPTS keys — defaults to 'intel_brief' (short terminal summary).
        """
        system = PROMPTS.get(preset, PROMPTS["intel_brief"])
        # Format the query placeholder if present in the prompt
        system = system.replace("{query}", query)

        site_lines = []
        for s in sites[:20]:
            content_preview = s.get("content", "")[:350].replace("\n", " ")
            line = (
                f"URL: {s.get('url','')}\n"
                f"  Title: {s.get('title','N/A')}\n"
                f"  Status: {s.get('status','unknown')}\n"
                f"  Tags: {', '.join(s.get('tags', []))}\n"
                f"  Content: {content_preview or 'N/A'}"
            )
            site_lines.append(line)

        user = f"Query: '{query}'\n\nDiscovered sites:\n\n" + "\n\n".join(site_lines)
        return self._call(system, user, max_tokens=800)

    def analyze_sites(self, prompt: str, sites: List[Dict],
                      preset: str = "threat_intel") -> str:
        """
        Custom analyst query over all tracked sites.
        preset controls which CTI framework to apply.
        """
        system = PROMPTS.get(preset, PROMPTS["threat_intel"])
        query  = prompt  # use the analyst's own prompt as the query context
        system = system.replace("{query}", query)

        site_lines = []
        for s in sites[:40]:
            content_preview = s.get("content", "")[:400].replace("\n", " ")
            line = (
                f"URL: {s.get('url','')}\n"
                f"  Title: {s.get('title','N/A')}\n"
                f"  Status: {s.get('status','unknown')}\n"
                f"  Tags: {', '.join(s.get('tags', []))}\n"
                f"  Content: {content_preview or 'N/A'}"
            )
            site_lines.append(line)

        user = f"Analyst request: {prompt}\n\nTracked sites:\n\n" + "\n\n".join(site_lines)
        return self._call(system, user, max_tokens=1200)

    def analyze_single_site(self, site: Dict, preset: str = "threat_intel") -> str:
        """Deep analysis of a single site using scraped content."""
        system = (
            "You are a dark web OSINT analyst. Given site metadata and scraped content, "
            "provide a detailed assessment: likely purpose, threat category, operational "
            "security posture, key artifacts, and recommended investigation steps. "
            "Use intelligence report style with clear section headings."
        )
        content_preview = site.get("content", "")[:1000].replace("\n", " ")
        user = (
            f"Site URL: {site.get('url','N/A')}\n"
            f"Title: {site.get('title','N/A')}\n"
            f"Tags: {', '.join(site.get('tags', []))}\n"
            f"Status: {site.get('status','unknown')}\n"
            f"HTTP Code: {site.get('status_code','N/A')}\n"
            f"Discovered: {site.get('discovered_at','N/A')}\n"
            f"\nScraped content:\n{content_preview or '[No content available]'}"
        )
        return self._call(system, user, max_tokens=900)

    def generate_report(self, query: str, sites: List[Dict],
                        preset: str = "threat_intel",
                        custom_instructions: str = "") -> str:
        """
        Full structured CTI report — mirrors llm.py generate_summary().
        preset: 'threat_intel' | 'ransomware_malware' | 'personal_identity' | 'corporate_espionage'
        custom_instructions: appended to the system prompt for focused analysis.
        """
        system = PROMPTS.get(preset, PROMPTS["threat_intel"])
        system = system.replace("{query}", query)
        if custom_instructions and custom_instructions.strip():
            system = system.rstrip() + f"\n\nAdditionally focus on: {custom_instructions.strip()}"

        # Build rich content block from scraped pages
        content_parts = []
        for s in sites[:30]:
            content_preview = s.get("content", "")[:500].replace("\n", " ")
            part = (
                f"[{s.get('status','?').upper()}] {s.get('url','')}\n"
                f"Title: {s.get('title','N/A')}\n"
                f"Content: {content_preview or 'N/A'}\n"
            )
            content_parts.append(part)

        content_block = "\n---\n".join(content_parts)
        user = f"Query: {query}\n\nOSINT Data:\n\n{content_block}"
        return self._call(system, user, max_tokens=1500)

    # ── Provider health check ──────────────────────────────────────────────
    def check_api_key(self) -> tuple[bool, str]:
        """Returns (is_configured: bool, message: str) for the active provider."""
        env_map = {
            "anthropic":   "ANTHROPIC_API_KEY",
            "openai":      "OPENAI_API_KEY",
            "google":      "GOOGLE_API_KEY",
            "groq":        "GROQ_API_KEY",
            "openrouter":  "OPENROUTER_API_KEY",
        }
        env_var = env_map.get(self.provider, "")
        is_set  = bool(os.getenv(env_var, ""))
        if is_set:
            return True, f"{self.model_name} — configured ✓"
        return False, f"{env_var} not set"