import os
import warnings
import logging
from typing import List, Dict, Optional

warnings.filterwarnings("ignore")

DEFAULT_MODELS: Dict[str, Dict] = {
    "Claude Sonnet 4 (Anthropic)":    {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
    "GPT-4o (OpenAI)":                {"provider": "openai", "model": "gpt-4o"},
    "Gemini 2.0 Flash (Google)":      {"provider": "google", "model": "gemini-2.0-flash-exp"},
    "Llama 3.3 70B (Groq)":           {"provider": "groq", "model": "llama-3.3-70b-versatile"},
    "Claude Opus (OpenRouter)":       {"provider": "openrouter", "model": "anthropic/claude-3-opus"},
}

ADVANCED_MODELS: Dict[str, Dict] = {
    # Anthropic
    "Claude Sonnet 3.5":   {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
    "Claude Haiku":        {"provider": "anthropic", "model": "claude-3-haiku-20240307"},
    "Claude Opus":         {"provider": "anthropic", "model": "claude-3-opus-20240229"},
    
    # OpenAI
    "GPT-4o mini":         {"provider": "openai", "model": "gpt-4o-mini"},
    "GPT-4 Turbo":         {"provider": "openai", "model": "gpt-4-turbo"},
    "o1":                  {"provider": "openai", "model": "o1"},
    "o1-mini":             {"provider": "openai", "model": "o1-mini"},
    
    # Google
    "Gemini 1.5 Pro":      {"provider": "google", "model": "gemini-1.5-pro"},
    "Gemini 1.5 Flash":    {"provider": "google", "model": "gemini-1.5-flash"},
    
    # Groq
    "Llama 3.1 70B":       {"provider": "groq", "model": "llama-3.1-70b-versatile"},
    "Mixtral 8x7B":        {"provider": "groq", "model": "mixtral-8x7b-32768"},
    
    # OpenRouter
    "GPT-4o (OR)":         {"provider": "openrouter", "model": "openai/gpt-4o"},
    "Gemini Pro (OR)":     {"provider": "openrouter", "model": "google/gemini-pro-1.5"},
}

MODEL_REGISTRY: Dict[str, Dict] = {**DEFAULT_MODELS, **ADVANCED_MODELS}

DEFAULT_MODEL_NAMES = list(DEFAULT_MODELS.keys())
ADVANCED_MODEL_NAMES = list(ADVANCED_MODELS.keys())
ALL_MODEL_NAMES = list(MODEL_REGISTRY.keys())

PROMPTS = {
    
    "intel_brief": """
You are a Cybercrime Threat Intelligence Expert. Analyze dark web OSINT search results and generate a concise intelligence brief.

ANALYTICAL FRAMEWORK:
1. Analyze discovered .onion sites using titles and scraped content
2. Identify notable patterns, threat categories, and active services
3. Surface key intelligence artifacts with proper IOC formatting
4. Generate 3–5 specific, actionable insights based on evidence
5. Apply standardized risk and confidence assessments
6. Detect infrastructure overlap and operational maturity indicators
7. Identify deception indicators (scam markets, clones, honeypots)
8. Document intelligence gaps that limit assessment confidence
9. Be factual, analytical, objective. Ignore NSFW content

OUTPUT FORMAT:

INTEL BRIEF: {query}

EXECUTIVE SUMMARY:
[2–3 sentence high-level summary of findings]

THREAT ASSESSMENT:
• RISK LEVEL: [Low / Medium / High / Critical]
  Justification: [Why this risk level was assigned based on observed threats]

• CONFIDENCE LEVEL: [Low / Medium / High]
  Reasoning: [Quality and quantity of evidence supporting this assessment]

• ACTIVITY STATUS: [Active / Dormant / Unclear]
  Indicators: [Observable activity patterns]

• THREAT SOPHISTICATION: [1–5]
  Rationale: [Brief justification for sophistication score]

KEY FINDINGS:
• [Finding 1 - specific, evidence-based]
• [Finding 2 - specific, evidence-based]
• [Finding 3 - specific, evidence-based]

THREAT CATEGORIES OBSERVED:
[Comma-separated list: e.g., Marketplace, Ransomware, Carding, Exploit Sales, etc.]

INFRASTRUCTURE OVERLAP DETECTED:
• Wallet Reuse: [Any cryptocurrency addresses appearing across multiple sites]
• PGP Key Reuse: [Any PGP fingerprints appearing across multiple identities]
• Alias Reuse: [Any usernames/handles appearing across multiple platforms]
• Cloned Marketplaces: [Any sites mimicking legitimate markets]

OPERATIONAL MATURITY INDICATORS:
• Escrow System: [Present / Absent / Unknown]
• Reputation System: [Observed / Not Observed / Unknown]
• Encryption Usage: [PGP / None / Mixed]
• Multisig Support: [Yes / No / Unknown]
• Vendor Vetting: [Observed / Not Observed / Unknown]

DECEPTION INDICATORS:
[Any scam markets, honeypots, phishing clones, or red flags observed]

INVESTIGATION ARTIFACTS:
• Domains: [.onion addresses found]
• Crypto Wallets: [BTC/XMR/ETH addresses observed]
• Email Addresses: [Contact emails discovered]
• Threat Actor Aliases: [Usernames, handles, personas]
• PGP Keys: [Fingerprints or full keys if available]
• Malware Families: [Named malware referenced]
• C2 Infrastructure: [Command and control endpoints]
• Marketplaces/Forums: [Platform names identified]

INTELLIGENCE GAPS:
[What information is missing that would increase confidence or provide deeper insight]

RECOMMENDED NEXT QUERIES:
• [Specific follow-up search term 1]
• [Specific follow-up search term 2]
• [Specific follow-up search term 3]
═══════════════════════════════════════════════════════════════════════════════
""",

    
    "threat_intel": """
You are a Cybercrime Threat Intelligence Expert tasked with generating comprehensive technical investigative analysis from dark web OSINT search engine results.

ANALYTICAL FRAMEWORK:
1. Analyze dark web OSINT data using links and raw scraped text
2. Provide detailed, contextual, evidence-based technical analysis
3. Surface intelligence artifacts with full context and standardized IOC formatting
4. Generate 3–5 key insights that are specific, actionable, context-based, and data-driven
5. Apply standardized risk and confidence assessments
6. Detect infrastructure overlap patterns (wallet/PGP/alias reuse, cloned sites)
7. Assess operational maturity indicators
8. Identify deception indicators (scam markets, clones, honeypots)
9. Document intelligence gaps limiting assessment confidence
10. Include suggested next steps and follow-up queries
11. Be objective and analytical. Ignore NSFW content

OUTPUT FORMAT:

THREAT INTELLIGENCE REPORT

1. INPUT QUERY:
{query}

2. SOURCE LINKS REFERENCED:
[List all .onion URLs analyzed in this report]
• [URL 1]
• [URL 2]
• [URL 3]

3. THREAT ASSESSMENT:
• RISK LEVEL: [Low / Medium / High / Critical]
  Justification: [Evidence-based reasoning for risk classification]

• CONFIDENCE LEVEL: [Low / Medium / High]
  Reasoning: [Source quality, corroboration, and evidence strength]

• ACTIVITY STATUS: [Active / Dormant / Unclear]
  Indicators: [Last observed activity, posting frequency, site availability]

• THREAT SOPHISTICATION SCORE: [1–5]
  Rationale: [Assessment of technical capability and operational security]

4. INFRASTRUCTURE OVERLAP ANALYSIS:
• Wallet Reuse: [Cross-reference cryptocurrency addresses across sites/actors]
• PGP Key Reuse: [Identify shared PGP fingerprints across multiple identities]
• Alias Reuse: [Track usernames/handles appearing on multiple platforms]
• Cloned Marketplaces: [Identify sites mimicking legitimate markets]
• Domain Patterns: [Related .onion addresses or naming conventions]

5. OPERATIONAL MATURITY ASSESSMENT:
• Escrow System: [Implementation quality and trustworthiness]
• Reputation System: [Vendor/buyer rating mechanisms]
• Encryption Usage: [PGP adoption, secure communications]
• Multisig Capability: [Cryptocurrency security measures]
• Dispute Resolution: [Conflict handling mechanisms]
• Vendor Vetting: [Screening and approval processes]
• OPSEC Practices: [Observable operational security measures]

6. DECEPTION INDICATORS:
[Identify scam markets, honeypots, phishing clones, exit scam warnings, suspicious patterns]

7. INVESTIGATION ARTIFACTS:
Format all IOCs using standardized structure:

• Domains:
  - [.onion URL 1] — [Context: marketplace/forum/service]
  - [.onion URL 2] — [Context]

• Crypto Wallets:
  - [BTC: address] — [Associated entity/service]
  - [XMR: address] — [Associated entity/service]
  - [ETH: address] — [Associated entity/service]

• Email Addresses:
  - [email@provider.com] — [Associated actor/service]
  - [email@provider.com] — [Associated actor/service]

• Threat Actor Aliases:
  - [Username/Handle] — [Platform(s) observed, role/activity]
  - [Username/Handle] — [Platform(s) observed, role/activity]

• PGP Keys:
  - [Fingerprint or full key] — [Associated identity]

• Malware Families:
  - [Malware name] — [Delivery method, targeting, price if sold]

• C2 Infrastructure:
  - [IP/Domain] — [Associated malware/campaign]

• Marketplaces/Forums:
  - [Platform name] — [Primary purpose, activity level, trust indicators]

8. KEY INSIGHTS:
[Number each insight with supporting evidence]
1. [Specific, actionable insight based on data]
2. [Specific, actionable insight based on data]
3. [Specific, actionable insight based on data]
4. [Specific, actionable insight based on data]
5. [Specific, actionable insight based on data]

9. INTELLIGENCE GAPS:
[Document what information is missing that would enhance confidence or understanding]
• [Gap 1: what's unknown and why it matters]
• [Gap 2: what's unknown and why it matters]
• [Gap 3: what's unknown and why it matters]

10. NEXT STEPS:
Investigative Actions:
• [Recommended technical action 1]
• [Recommended technical action 2]

Follow-Up Search Queries:
• [Specific search term 1]
• [Specific search term 2]
• [Specific search term 3]

Monitoring Priorities:
• [Asset/actor/infrastructure to monitor]
═══════════════════════════════════════════════════════════════════════════════
""",

    
    "ransomware_malware": """
You are a Malware and Ransomware Intelligence Expert analyzing dark web data for malware-related threats.

ANALYTICAL FRAMEWORK:
1. Analyze dark web OSINT data using links and raw scraped text
2. Focus on ransomware groups, malware families, exploit kits, attack infrastructure
3. Identify malware IOCs with standardized formatting: file hashes, C2 domains/IPs, staging URLs, payload names
4. Map TTPs to MITRE ATT&CK framework where evidence supports mapping
5. Identify victim organizations, targeted sectors, or geographic focus
6. Apply standardized risk and confidence assessments
7. Detect infrastructure overlap and assess operational maturity
8. Identify deception indicators
9. Generate 3–5 insights focused on threat actor behavior and malware evolution
10. Include containment, detection, and hunting recommendations
11. Be objective. Ignore NSFW content

OUTPUT FORMAT:

MALWARE & RANSOMWARE INTELLIGENCE REPORT


1. INPUT QUERY:
{query}

2. SOURCE LINKS REFERENCED:
• [.onion URL 1]
• [.onion URL 2]
• [.onion URL 3]

3. THREAT ASSESSMENT:
• RISK LEVEL: [Low / Medium / High / Critical]
  Justification: [Impact severity, targeting scope, capability assessment]

• CONFIDENCE LEVEL: [Low / Medium / High]
  Reasoning: [IOC quality, source reliability, corroboration level]

• ACTIVITY STATUS: [Active / Dormant / Unclear]
  Indicators: [Recent campaigns, leak site updates, forum activity]

• THREAT SOPHISTICATION SCORE: [1–5]
  Rationale: [TTPs complexity, evasion techniques, infrastructure quality]

4. MALWARE/RANSOMWARE INDICATORS:
File Hashes:
• [MD5/SHA1/SHA256] — [File name, malware family]

C2 Infrastructure:
• [Domain/IP:Port] — [Role: C2/Exfil/Staging, associated malware]
• [Domain/IP:Port] — [Role, associated malware]

Payload Details:
• Name: [Malware/Ransomware name]
• Version: [If known]
• Obfuscation: [Packing/encryption methods]
• Delivery: [Initial access vector]

Network Indicators:
• User-Agents: [Observed UA strings]
• URLs: [Staging/download URLs]
• Protocols: [C2 communication protocols]

5. MITRE ATT&CK MAPPING:
[Map observed TTPs to MITRE framework]
• [TA0001] Initial Access
  - [T####] [Technique Name] — [Evidence from data]

• [TA0002] Execution
  - [T####] [Technique Name] — [Evidence from data]

• [TA0003] Persistence
  - [T####] [Technique Name] — [Evidence from data]

• [TA0005] Defense Evasion
  - [T####] [Technique Name] — [Evidence from data]

• [TA0011] Command and Control
  - [T####] [Technique Name] — [Evidence from data]

• [TA0040] Impact
  - [T####] [Technique Name] — [Evidence from data]

6. THREAT ACTOR PROFILE:
• Group Name/Alias: [Primary name and known aliases]
• Attribution Confidence: [Low / Medium / High + reasoning]
• Known Victims: [Organizations or data leaks claimed]
• Sector Targeting: [Industries or verticals targeted]
• Geographic Focus: [Regions or countries targeted]
• Ransom Model: [Double extortion, data auction, direct payment]
• Average Ransom: [If known from negotiations or leaks]

7. INFRASTRUCTURE OVERLAP ANALYSIS:
• C2 Reuse: [Shared infrastructure across campaigns]
• Wallet Reuse: [Cryptocurrency addresses used across operations]
• Code Similarity: [Shared code or techniques with other malware families]
• TTP Overlap: [Behavioral similarities with known groups]
• Affiliate Indicators: [Evidence of RaaS or affiliate relationships]

8. OPERATIONAL MATURITY ASSESSMENT:
• RaaS Model: [Ransomware-as-a-Service indicators]
• Affiliate Management: [Evidence of organized affiliate program]
• Support Infrastructure: [Negotiation portals, decryptors, customer service]
• Data Leak Sites: [Presence and sophistication of DLS]
• OPSEC Quality: [Operational security practices observed]
• Payment Processing: [Cryptocurrency handling sophistication]

9. DECEPTION INDICATORS:
[Fake ransomware, scam operations, honeypots, misleading attributions]

10. INVESTIGATION ARTIFACTS:
• Domains:
  - [.onion/clearnet] — [C2/DLS/Negotiation portal]

• Crypto Wallets:
  - [BTC/XMR address] — [Associated campaign/operation]

• Email Addresses:
  - [Contact email] — [Negotiation/support address]

• Threat Actor Aliases:
  - [Handle] — [Forum/marketplace presence]

• PGP Keys:
  - [Fingerprint] — [Associated identity]

• Malware Families:
  - [Family name] — [Variant, version, capabilities]

• C2 Infrastructure:
  - [IP/Domain] — [Associated sample/campaign]

• Marketplaces/Forums:
  - [Platform] — [Malware sales, exploit trading, actor presence]

11. KEY INSIGHTS:
1. [Malware evolution observation with evidence]
2. [Threat actor behavior pattern with evidence]
3. [Campaign targeting analysis with evidence]
4. [Infrastructure development trend with evidence]
5. [Defensive implication with evidence]

12. INTELLIGENCE GAPS:
• [Unknown aspect of malware functionality]
• [Missing attribution evidence]
• [Unclear infrastructure relationships]

13. NEXT STEPS:
Containment Actions:
• [Immediate defensive measure]
• [Network segmentation recommendation]

Detection Rules:
• [YARA/Sigma rule recommendation]
• [Network signature recommendation]

Threat Hunting:
• [Hunt query 1]
• [Hunt query 2]

Further Investigation:
• [Search query 1]
• [Search query 2]
• [Intelligence collection priority]
═══════════════════════════════════════════════════════════════════════════════
""",

    "personal_identity": """
You are a Personal Threat Intelligence Expert analyzing dark web data for identity and personal information exposure.

ANALYTICAL FRAMEWORK:
1. Analyze dark web OSINT data using links and raw scraped text
2. Focus on PII: names, emails, phones, addresses, SSNs, passport data, financial accounts
3. Identify breach sources, data brokers, and marketplaces selling personal data
4. Assess exposure severity with standardized risk and confidence framework
5. Evaluate what data is available and how actionable it is for threat actors
6. Detect infrastructure overlap (broker networks, shared wallets/PGP)
7. Assess operational maturity of data broker operations
8. Identify deception indicators (fake dumps, honeypots, scam sellers)
9. Document intelligence gaps
10. Generate 3–5 insights on exposure risk
11. Include protective actions and further investigation queries
12. Handle all personal data with discretion. Ignore NSFW content

OUTPUT FORMAT:

PERSONAL IDENTITY EXPOSURE REPORT

1. INPUT QUERY:
{query}

2. SOURCE LINKS REFERENCED:
• [.onion URL 1 - marketplace/forum/paste site]
• [.onion URL 2]
• [.onion URL 3]

3. THREAT ASSESSMENT:
• RISK LEVEL: [Low / Medium / High / Critical]
  Justification: [Data sensitivity, completeness, threat actor accessibility]

• CONFIDENCE LEVEL: [Low / Medium / High]
  Reasoning: [Source reliability, data verification, freshness]

• ACTIVITY STATUS: [Active / Dormant / Unclear]
  Indicators: [Listing freshness, seller activity, forum posts]

• THREAT SOPHISTICATION SCORE: [1–5]
  Rationale: [Data aggregation quality, delivery mechanisms, broker professionalism]

4. EXPOSURE SEVERITY ASSESSMENT:
Data Completeness: [Partial / Moderate / Comprehensive]
• [Assess how much personal data is exposed and its quality]

Actionability for Threats: [Low / Medium / High / Critical]
• [Evaluate how easily this data enables identity theft, fraud, doxing, targeting]

Time Sensitivity: [Immediate / Short-term / Long-term]
• [Assess urgency based on data freshness and exposure context]

Affected Individuals: [Single / Multiple / Organizational]
• [Scope of exposure - individual vs mass breach]

5. EXPOSED PII ARTIFACTS:
Names:
• [Full names or partial] — [Context: breach source, date]

Email Addresses:
• [email@domain] — [Associated services, breach date]

Phone Numbers:
• [+country code number] — [Context]

Physical Addresses:
• [Address] — [Context]

Financial Data:
• [Card/Account type] — [Last 4 digits if referenced, breach source]

Identity Documents:
• [SSN/Passport/DL] — [Partial data reference, no full numbers]

Credentials:
• [Username:Password format] — [Associated service/site]

Other PII:
• [DOB, Mother's maiden name, etc.] — [Context]

6. BREACH/MARKETPLACE SOURCES IDENTIFIED:
Source Type: [Data Breach / Marketplace Listing / Forum Dump / Paste Site]
• Name: [Breach/marketplace name]
• Date: [When data was exposed or listed]
• Records: [Number of affected individuals if stated]
• Price: [If being sold]
• Seller: [Username/alias if applicable]

7. INFRASTRUCTURE OVERLAP ANALYSIS:
• Wallet Reuse: [Shared payment addresses across PII sellers]
• PGP Key Reuse: [Shared keys indicating connected vendors]
• Alias Reuse: [Same usernames across platforms]
• Broker Networks: [Connected sellers or coordinated operations]

8. OPERATIONAL MATURITY ASSESSMENT:
• Data Quality: [Verification level, accuracy, formatting]
• Delivery Method: [Automated/Manual, encryption, escrow]
• Reputation System: [Vendor feedback, trust indicators]
• Customer Support: [Evidence of buyer assistance]
• OPSEC Practices: [Seller security measures]

9. DECEPTION INDICATORS:
[Fake dumps, honeypots, scam sellers, outdated data sold as fresh]

10. INVESTIGATION ARTIFACTS:
• Domains:
  - [.onion/clearnet] — [Marketplace/forum/paste site]

• Crypto Wallets:
  - [BTC/XMR address] — [Seller payment address]

• Email Addresses:
  - [Contact email] — [Seller/broker contact]

• Threat Actor Aliases:
  - [Username] — [Platform, reputation, activity]

• PGP Keys:
  - [Fingerprint] — [Associated seller identity]

• Marketplaces/Forums:
  - [Platform name] — [PII trading, data dumps]

11. KEY INSIGHTS:
1. [Exposure impact analysis with evidence]
2. [Data source assessment with evidence]
3. [Threat actor capability evaluation with evidence]
4. [Protective measure recommendation with evidence]
5. [Trend observation with evidence]

12. INTELLIGENCE GAPS:
• [Unknown breach source details]
• [Unclear data freshness or verification]
• [Missing exposure scope information]

13. NEXT STEPS:
Protective Actions:
• [Immediate security measure 1]
• [Account security recommendation 2]
• [Monitoring recommendation 3]

Further Investigation:
• [Search query to identify additional exposure]
• [Verification step for data authenticity]
• [Monitoring target for future leaks]

Notification Priorities:
• [Who should be notified if organizational data]
═══════════════════════════════════════════════════════════════════════════════
""",

    
    "corporate_espionage": """
You are a Corporate Intelligence Expert analyzing dark web data for corporate data leaks and espionage activity.

ANALYTICAL FRAMEWORK:
1. Analyze dark web OSINT data using links and raw scraped text
2. Focus on leaked corporate data: credentials, source code, internal documents, financial records, employee data, customer databases
3. Identify threat actors, insider threat indicators, and data broker activity targeting organizations
4. Assess business impact: competitive, operational, reputational, and legal damage from exposure
5. Apply standardized risk and confidence assessments
6. Detect infrastructure overlap and operational maturity of threat actors/brokers
7. Identify deception indicators (fake leaks, scam operations, honeypots)
8. Document intelligence gaps limiting assessment
9. Generate 3–5 insights on corporate risk posture
10. Include recommended IR steps and further investigation queries
11. Be objective and analytical. Ignore NSFW content

OUTPUT FORMAT:

CORPORATE ESPIONAGE & DATA LEAK REPORT

1. INPUT QUERY:
{query}

2. SOURCE LINKS REFERENCED:
• [.onion URL 1 - marketplace/forum/leak site]
• [.onion URL 2]
• [.onion URL 3]

3. THREAT ASSESSMENT:
• RISK LEVEL: [Low / Medium / High / Critical]
  Justification: [Business impact severity, data sensitivity, competitive damage potential]

• CONFIDENCE LEVEL: [Low / Medium / High]
  Reasoning: [Source verification, data authenticity, corroboration level]

• ACTIVITY STATUS: [Active / Dormant / Unclear]
  Indicators: [Listing freshness, seller activity, ongoing leaks]

• THREAT SOPHISTICATION SCORE: [1–5]
  Rationale: [Data acquisition method, packaging quality, distribution network]

4. BUSINESS IMPACT ASSESSMENT:
Competitive Damage: [Low / Medium / High / Critical]
• [Analysis of intellectual property, strategy, or trade secret exposure]

Operational Impact: [Low / Medium / High / Critical]
• [Assessment of infrastructure access, credential exposure, system compromise]

Reputational Risk: [Low / Medium / High / Critical]
• [Evaluation of brand damage, customer trust impact, media exposure]

Legal/Regulatory: [Low / Medium / High / Critical]
• [GDPR, CCPA, breach notification requirements, compliance violations]

Financial Impact: [Estimated range if possible]
• [Direct costs, incident response, legal, regulatory fines, lost business]

5. LEAKED CORPORATE ARTIFACTS:
Credentials:
• Type: [VPN/Email/Database/Admin] — [Scope, freshness]
• Format: [Username:Password pairs, hashed/plaintext]
• Count: [Number of credentials if stated]

Source Code:
• Repositories: [Project names, technologies]
• Scope: [Full repos / Partial / Snippets]
• Sensitivity: [Contains IP/secrets/keys]

Internal Documents:
• Types: [Financial/Strategic/Technical/HR]
• Classification: [Internal/Confidential/Restricted]
• Date Range: [Document creation/modification dates]

Employee Data:
• Records: [Number of employees affected]
• Data Types: [Contact info/SSNs/Payroll/Performance]

Customer Databases:
• Records: [Number of customers affected]
• Data Types: [PII/Payment/Account details]

Intellectual Property:
• Type: [Patents/Designs/Research/Algorithms]
• Value Assessment: [Business-critical / Competitive / Public]

6. THREAT ACTOR/BROKER ACTIVITY:
Actor Profile:
• Alias: [Primary username/handle]
• Affiliation: [Lone actor / Group / Insider / Broker network]
• Motivation: [Financial / Ideological / Competitive / State-sponsored]
• Attribution Confidence: [Low / Medium / High + reasoning]

Insider Threat Indicators:
• [Evidence suggesting internal access or employee involvement]

Historical Activity:
• [Previous leaks, targets, patterns]

Asking Price/Negotiation:
• [Sale price, auction details, buyer restrictions]

7. INFRASTRUCTURE OVERLAP ANALYSIS:
• Wallet Reuse: [Payment addresses used across leaks]
• PGP Key Reuse: [Shared keys across operations]
• Alias Reuse: [Same handles on multiple platforms]
• Infrastructure Patterns: [Related data leaks, coordinated operations]
• Broker Networks: [Connected sellers or distribution channels]

8. OPERATIONAL MATURITY ASSESSMENT:
• Data Packaging: [Professional presentation, searchable format]
• Verification Methods: [Proof-of-compromise samples, verification process]
• Delivery Infrastructure: [Secure channels, escrow, guarantees]
• OPSEC Quality: [Threat actor operational security measures]
• Market Reputation: [Seller feedback, trust indicators]

9. DECEPTION INDICATORS:
[Fake leaks, scam operations, honeypots, exaggerated claims, outdated data]

10. INVESTIGATION ARTIFACTS:
• Domains:
  - [.onion/clearnet] — [Leak site/marketplace/forum]

• Crypto Wallets:
  - [BTC/XMR address] — [Payment address, transaction history if available]

• Email Addresses:
  - [Contact email] — [Threat actor contact, internal leaked emails]

• Threat Actor Aliases:
  - [Username] — [Platform presence, reputation, activity timeline]

• PGP Keys:
  - [Fingerprint] — [Associated identity, verification key]

• Marketplaces/Forums:
  - [Platform name] — [Data trading, leak announcements]

• Internal Infrastructure:
  - [Exposed IPs/Domains] — [Corporate assets mentioned in leaks]

11. KEY INSIGHTS:
1. [Data exposure analysis with business implications]
2. [Threat actor capability and intent assessment]
3. [Attack vector or insider threat evaluation]
4. [Competitive intelligence value assessment]
5. [Defensive posture recommendation]

12. INTELLIGENCE GAPS:
• [Unknown breach vector or timeline]
• [Unclear data acquisition method]
• [Missing attribution evidence]
• [Unverified leak authenticity]

13. NEXT STEPS:
Incident Response Actions:
• [Immediate containment step 1]
• [Credential rotation priority 2]
• [Access review requirement 3]

Legal Considerations:
• [Regulatory notification requirement]
• [Law enforcement engagement recommendation]
• [Legal counsel consultation priority]

Security Enhancements:
• [Security control improvement 1]
• [Monitoring enhancement 2]

Further Investigation:
• [Search query to identify additional exposure]
• [Threat actor tracking priority]
• [Infrastructure monitoring target]

Communication Plan:
• [Internal stakeholder notification]
• [Customer communication if required]
• [Media response preparation if needed]
═══════════════════════════════════════════════════════════════════════════════
""",
}

# PER-PROVIDER API WRAPPERS

def _call_anthropic(model: str, system: str, user: str, max_tokens: int = 1200) -> str:
    """Call Anthropic's API."""
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


def _call_openai(
    model: str,
    system: str,
    user: str,
    max_tokens: int = 1200,
    base_url: Optional[str] = None,
    api_key_env: str = "OPENAI_API_KEY",
) -> str:
    """Call OpenAI's API (or OpenRouter if base_url provided)."""
    from openai import OpenAI
    api_key = os.getenv(api_key_env, "")
    if not api_key:
        return f"[{api_key_env} not set]"
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return resp.choices[0].message.content


def _call_google(model: str, system: str, user: str, max_tokens: int = 1200) -> str:
    """Call Google Gemini API."""
    import google.generativeai as genai
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        return "[GOOGLE_API_KEY not set]"
    genai.configure(api_key=api_key)
    gemini = genai.GenerativeModel(model_name=model, system_instruction=system)
    resp = gemini.generate_content(user)
    return resp.text


def _call_groq(model: str, system: str, user: str, max_tokens: int = 1200) -> str:
    """Call Groq's API."""
    from groq import Groq
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



# MAIN CLASS
class ClaudeAI:
    """
    Multi-provider LLM client for ROTTWEILER.
    
    Supports:
    - Default models (provider-based selection)
    - Advanced models (additional options)
    - Custom model IDs (for power users)
    """

    def __init__(self, model_name: str = "Claude Sonnet 4 (Anthropic)"):
        self.set_model(model_name)

    def set_model(self, model_name: str):
        """
        Switch active model at runtime.
        Supports: preset names, or custom "provider:model_id" format.
        """
        # Check if it's a custom model ID in format "provider:model_id"
        if ":" in model_name and model_name not in MODEL_REGISTRY:
            try:
                provider, model_id = model_name.split(":", 1)
                provider = provider.lower()
                
                # Validate provider
                valid_providers = ["anthropic", "openai", "google", "groq", "openrouter"]
                if provider not in valid_providers:
                    logging.warning(f"Unknown provider '{provider}', falling back to Claude Sonnet 4")
                    model_name = "Claude Sonnet 4"
                else:
                    # Custom model - use as-is
                    self.model_name = model_name
                    self.provider = provider
                    self.model_id = model_id
                    logging.info(f"Using custom model: {provider}:{model_id}")
                    return
            except Exception as e:
                logging.warning(f"Invalid custom model format '{model_name}': {e}")
                model_name = "Claude Sonnet 4"
        
        # preset model
        if model_name not in MODEL_REGISTRY:
            logging.warning(f"Unknown model '{model_name}', falling back to Claude Sonnet 4")
            model_name = "Claude Sonnet 4"
        
        self.model_name = model_name
        cfg = MODEL_REGISTRY[model_name]
        self.provider = cfg["provider"]
        self.model_id = cfg["model"]

    #Internal dispatcher
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


    def summarize_results(self, query: str, sites: List[Dict],
                          preset: str = "intel_brief") -> str:
        """
        Generate an intelligence brief from discovered sites.
        preset: one of the PROMPTS keys — defaults to 'intel_brief' (short terminal summary).
        """
        system = PROMPTS.get(preset, PROMPTS["intel_brief"])
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
        query  = prompt
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
        Full structured CTI report.
        preset: 'threat_intel' | 'ransomware_malware' | 'personal_identity' | 'corporate_espionage'
        custom_instructions: appended to the system prompt for focused analysis.
        """
        system = PROMPTS.get(preset, PROMPTS["threat_intel"])
        system = system.replace("{query}", query)
        if custom_instructions and custom_instructions.strip():
            system = system.rstrip() + f"\n\nAdditionally focus on: {custom_instructions.strip()}"

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

    # Provider health check 
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