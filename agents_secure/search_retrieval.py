"""
Agent 2: Search & Retrieval Agent
Executes web search and retrieves content from URLs.
"""

from tavily import TavilyClient
from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


class SearchRetrievalAgent:
    """
    Agent responsible for executing web search and retrieving content.
    """

    def __init__(self, tavily_api_key: str):
        self.tavily_client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None

    def process(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Execute search and retrieve content from results.

        Args:
            query: Formatted search query string
            max_results: Maximum number of results to retrieve

        Returns:
            List of dicts containing:
                - url: Source URL
                - title: Page title
                - content: Scraped text content
                - raw_result: Original search result metadata
        """
        if not self.tavily_client:
            print("Warning: TAVILY_API_KEY not configured")
            return []

        # Execute search
        search_results = self._search(query, max_results)

        # Retrieve and scrape content
        enriched_results = []
        for result in search_results:
            url = result.get("url", "")
            if not url:
                continue

            # Try to use Tavily's content first (more reliable)
            content = result.get("content", "")

            # If no content from Tavily, scrape the URL
            if not content or len(content) < 100:
                content = self._scrape_content(url)

            # If still no content, use Tavily's snippet/description
            if not content or len(content) < 50:
                content = result.get("snippet", "") or result.get("description", "")

            # Only include if we have some content
            if content and len(content) > 20:
                enriched_results.append({
                    "url": url,
                    "title": result.get("title", "Unknown"),
                    "content": content,
                    "raw_result": result
                })
                print(f"✓ Retrieved: {result.get('title', 'Unknown')[:60]}... ({len(content)} chars)")
            else:
                print(f"✗ Skipped (no content): {url}")

        print(f"\n✓ Total results with content: {len(enriched_results)}")
        return enriched_results

    def _search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Execute Tavily search with optimized query."""
        try:
            # Simplify query for Tavily - extract just the topic keywords
            # Tavily doesn't handle complex Google operators well
            simplified_query = self._simplify_query(query)

            print(f"Original query: {query[:100]}...")
            print(f"Simplified query: {simplified_query}")

            # Use Tavily's domain filtering instead of site: operators
            include_domains = self._extract_domains(query)

            # Execute search with multiple strategies
            all_results = []

            # Strategy 1: Search with domain filters
            if include_domains:
                try:
                    results = self.tavily_client.search(
                        query=simplified_query,
                        max_results=max_results // 2,
                        search_depth="advanced",
                        include_domains=include_domains
                    )
                    all_results.extend(results.get("results", []))
                    print(f"Strategy 1 (with domains): Found {len(results.get('results', []))} results")
                except Exception as e:
                    print(f"Domain-filtered search failed: {e}")

            # Strategy 2: Broader search without domain restrictions
            try:
                results = self.tavily_client.search(
                    query=simplified_query,
                    max_results=max_results,
                    search_depth="advanced"
                )
                all_results.extend(results.get("results", []))
                print(f"Strategy 2 (no domain filter): Found {len(results.get('results', []))} results")
            except Exception as e:
                print(f"Broad search failed: {e}")

            # Remove duplicates by URL
            seen_urls = set()
            unique_results = []
            for result in all_results:
                url = result.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)

            print(f"Total unique results: {len(unique_results)}")
            return unique_results[:max_results]

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def _simplify_query(self, query: str) -> str:
        """
        Simplify complex query to work better with Tavily.
        Extract main topic and key terms, remove operators.
        """
        import re

        # Remove common operators and patterns that don't work with Tavily
        simplified = query

        # Remove "Resolved:" prefix
        simplified = re.sub(r'Resolved:\s*', '', simplified, flags=re.IGNORECASE)

        # Remove site: operators (we'll handle with include_domains)
        simplified = re.sub(r'site:\S+', '', simplified)

        # Remove filetype: operators
        simplified = re.sub(r'filetype:\S+', '', simplified)

        # Remove exclusion operators
        simplified = re.sub(r'-\w+', '', simplified)

        # Remove standalone OR, AND
        simplified = re.sub(r'\s+(OR|AND)\s+', ' ', simplified, flags=re.IGNORECASE)

        # Remove parentheses
        simplified = re.sub(r'[()]', ' ', simplified)

        # Remove "evidence file" and other meta terms
        meta_terms = ['evidence file', 'Key arguments for', 'Key arguments against']
        for term in meta_terms:
            simplified = re.sub(term, '', simplified, flags=re.IGNORECASE)

        # Clean up extra whitespace
        simplified = ' '.join(simplified.split())

        # Add context keywords for better results
        simplified = f"{simplified} research policy analysis evidence"

        return simplified.strip()

    def _extract_domains(self, query: str) -> List[str]:
        """Extract domain names from site: operators."""
        import re

        # Find all site: patterns
        domains = re.findall(r'site:([^\s]+)', query)

        # Clean up domains (remove any OR, commas, etc.)
        cleaned_domains = []
        for domain in domains:
            domain = domain.strip().lower()
            # Remove trailing punctuation
            domain = re.sub(r'[,;]$', '', domain)
            if domain:
                cleaned_domains.append(domain)

        return cleaned_domains

    def _scrape_content(self, url: str) -> str:
        """
        Scrape content from URL.

        Args:
            url: URL to scrape

        Returns:
            Cleaned text content (max 5000 chars)
        """
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove non-content elements
            for element in soup(["script", "style", "nav", "footer", "aside", "header"]):
                element.decompose()

            # Extract text
            text = soup.get_text(separator=' ', strip=True)

            # Limit to first 5000 characters
            return text[:5000]

        except Exception as e:
            print(f"Scraping error for {url}: {e}")
            return ""


if __name__ == "__main__":
    # Test the agent
    agent = SearchRetrievalAgent()

    print("=" * 80)
    print("Search & Retrieval Agent Test")
    print("=" * 80)

    # Test query
    query = 'Resolved: nuclear energy evidence file OR Key arguments for AND Key arguments against site:brookings.edu OR site:cfr.org OR site:bbc.com OR filetype:pdf (policy OR economic impact) -blog -opinion'

    print(f"\nQuery: {query}\n")
    results = agent.process(query, max_results=5)

    print(f"\nRetrieved {len(results)} results")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Content length: {len(result['content'])} chars")

    print("=" * 80)
