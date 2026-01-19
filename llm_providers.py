"""
================================================================================
LLM PROVIDERS - Multi-Model AI Integration for Sadie
================================================================================
Integrates multiple LLM providers for maximum accuracy and research capability:
- Google Gemini 2.5 Pro (Primary reasoning engine)
- Perplexity Sonar Pro (Real-time research and fact-checking)

For production use with real money decisions.
================================================================================
"""

import os
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime


class GeminiProvider:
    """
    Google Gemini 2.5 Pro integration for primary reasoning.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Gemini 2.5 Pro endpoint
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-2.5-pro-preview-05-06"  # Latest Gemini 2.5 Pro
    
    def generate(self, messages: List[Dict], max_tokens: int = 8192, temperature: float = 0.7) -> Dict:
        """
        Generate a response using Gemini 2.5 Pro.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Dict with response content and metadata
        """
        try:
            # Convert messages to Gemini format
            gemini_contents = []
            system_instruction = None
            
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                
                if role == 'system':
                    system_instruction = content
                elif role == 'user':
                    gemini_contents.append({
                        "role": "user",
                        "parts": [{"text": content}]
                    })
                elif role == 'assistant':
                    gemini_contents.append({
                        "role": "model",
                        "parts": [{"text": content}]
                    })
            
            # Build request payload
            payload = {
                "contents": gemini_contents,
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature,
                    "topP": 0.95,
                    "topK": 40
                }
            }
            
            # Add system instruction if present
            if system_instruction:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }
            
            # Make API call
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=120  # 2 minute timeout for complex reasoning
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "error": f"Gemini API error: {response.status_code} - {response.text}",
                    "content": None
                }
            
            result = response.json()
            
            # Extract response text
            candidates = result.get("candidates", [])
            if not candidates:
                return {
                    "status": "error",
                    "error": "No response candidates from Gemini",
                    "content": None
                }
            
            content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            return {
                "status": "success",
                "content": content,
                "model": self.model,
                "provider": "gemini",
                "usage": result.get("usageMetadata", {})
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "content": None
            }


class PerplexityProvider:
    """
    Perplexity Sonar Pro integration for real-time research and fact-checking.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-pro"  # Perplexity Sonar Pro for real-time research
    
    def research(self, query: str, context: str = "") -> Dict:
        """
        Perform real-time research using Perplexity Sonar Pro.
        
        Args:
            query: The research query
            context: Additional context for the research
            
        Returns:
            Dict with research findings and citations
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a financial research assistant. Your job is to:
1. Find the most current, real-time information about stocks, markets, and financial events
2. Verify facts and data points
3. Provide citations for all claims
4. Focus on actionable intelligence for trading decisions

Always include:
- Current prices and recent changes
- Breaking news and catalysts
- Analyst ratings and price targets
- Upcoming events (earnings, dividends, etc.)
- Any unusual market activity"""
                },
                {
                    "role": "user",
                    "content": f"{context}\n\nResearch Query: {query}"
                }
            ]
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.2,  # Lower temperature for factual research
                "return_citations": True,
                "return_related_questions": True
            }
            
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "error": f"Perplexity API error: {response.status_code} - {response.text}",
                    "content": None
                }
            
            result = response.json()
            
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = result.get("citations", [])
            
            return {
                "status": "success",
                "content": content,
                "citations": citations,
                "model": self.model,
                "provider": "perplexity",
                "related_questions": result.get("related_questions", [])
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "content": None
            }


class MultiModelOrchestrator:
    """
    Orchestrates multiple LLM providers for optimal results.
    
    Strategy:
    1. Use Perplexity Sonar Pro for real-time research and fact-checking
    2. Use Gemini 2.5 Pro for deep reasoning and analysis
    3. Combine insights for maximum accuracy
    """
    
    def __init__(self):
        self.gemini = GeminiProvider()
        self.perplexity = PerplexityProvider()
    
    def analyze(self, user_query: str, system_prompt: str, market_data: str) -> Dict:
        """
        Perform comprehensive analysis using multiple models.
        
        Args:
            user_query: The user's question
            system_prompt: The system prompt for the AI
            market_data: Pre-fetched market data context
            
        Returns:
            Dict with combined analysis
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "query": user_query
        }
        
        # Step 1: Use Perplexity for real-time research
        research_query = self._extract_research_needs(user_query)
        if research_query:
            perplexity_result = self.perplexity.research(
                research_query,
                context=f"User is asking about: {user_query}"
            )
            results["research"] = perplexity_result
        
        # Step 2: Combine all context for Gemini
        enhanced_context = self._build_enhanced_context(
            market_data,
            results.get("research", {}).get("content", "")
        )
        
        # Step 3: Use Gemini 2.5 Pro for deep analysis
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
REAL-TIME MARKET DATA:
{enhanced_context}

USER QUERY:
{user_query}

Analyze thoroughly and provide your highest-conviction recommendation with specific actionable guidance.
"""}
        ]
        
        gemini_result = self.gemini.generate(messages, max_tokens=8192, temperature=0.7)
        results["analysis"] = gemini_result
        
        # Combine results
        if gemini_result.get("status") == "success":
            results["status"] = "success"
            results["response"] = gemini_result.get("content", "")
            results["model"] = "gemini-2.5-pro + perplexity-sonar-pro"
        else:
            results["status"] = "error"
            results["error"] = gemini_result.get("error", "Unknown error")
        
        return results
    
    def _extract_research_needs(self, query: str) -> Optional[str]:
        """Extract what needs real-time research from the query."""
        # Keywords that indicate need for real-time research
        research_keywords = [
            "news", "latest", "today", "current", "recent", "breaking",
            "earnings", "announcement", "catalyst", "event", "update",
            "analyst", "upgrade", "downgrade", "target", "rating"
        ]
        
        query_lower = query.lower()
        needs_research = any(kw in query_lower for kw in research_keywords)
        
        # Also research if specific tickers mentioned
        import re
        tickers = re.findall(r'\$([A-Z]{1,5})', query.upper())
        if tickers:
            needs_research = True
        
        if needs_research:
            return query
        return None
    
    def _build_enhanced_context(self, market_data: str, research_findings: str) -> str:
        """Combine market data with research findings."""
        sections = []
        
        if market_data:
            sections.append(market_data)
        
        if research_findings:
            sections.append(f"""
=== REAL-TIME RESEARCH (Perplexity Sonar Pro) ===
{research_findings}
""")
        
        return "\n\n".join(sections)


# Test function
if __name__ == "__main__":
    print("Testing LLM Providers...")
    
    # Test Gemini
    try:
        gemini = GeminiProvider()
        result = gemini.generate([
            {"role": "user", "content": "What is 2+2?"}
        ])
        print(f"Gemini test: {result.get('status')}")
    except Exception as e:
        print(f"Gemini error: {e}")
    
    # Test Perplexity
    try:
        perplexity = PerplexityProvider()
        result = perplexity.research("What is the current price of AAPL?")
        print(f"Perplexity test: {result.get('status')}")
    except Exception as e:
        print(f"Perplexity error: {e}")
    
    print("LLM Providers module loaded successfully!")
