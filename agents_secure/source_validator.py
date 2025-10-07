"""
Agent 3: Source Validation Agent
Validates sources against approved list and filters out blogs/opinions.
Includes user confirmation workflow.
"""

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from typing import List, Dict, Any, Tuple
import os
from dotenv import load_dotenv

load_dotenv()


# Approved sources for debate research
APPROVED_SOURCES = [
    "brookings.edu",
    "cfr.org",
    "gmfus.org",
    "csis.org",
    "bbc.com",
    "reuters.com",
    "apnews.com",
    "npr.org",
    "nature.com",
    "science.org",
    "scholar.google.com",
    "edu",  # Academic institutions
]

EXCLUDED_PATTERNS = [
    "blog",
    "opinion",
    "editorial",
    "/comment/",
    "/voices/",
]


class SourceValidatorAgent:
    """
    Agent responsible for validating sources and managing user confirmation workflow.
    """

    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3, api_key=openai_api_key)

    def process(self, search_results: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Validate sources and prepare for user confirmation.

        Args:
            search_results: List of search results with content

        Returns:
            Tuple of (validated_sources, validation_summary)
            - validated_sources: List of sources that passed validation
            - validation_summary: Summary info for user review
        """
        validated_sources = []

        for result in search_results:
            url = result.get("url", "")
            content = result.get("content", "")

            if not url or not content:
                continue

            # Check if source is valid
            is_valid, reason = self._validate_source(url, content)

            if is_valid:
                result["validation_reason"] = reason
                validated_sources.append(result)
                print(f"✓ Valid: {url}")
            else:
                print(f"✗ Rejected: {url} - {reason}")

        # Create summary for user
        validation_summary = self._create_summary(validated_sources)

        return validated_sources, validation_summary

    def _validate_source(self, url: str, content: str) -> Tuple[bool, str]:
        """
        Validate if source meets criteria.

        Args:
            url: Source URL
            content: Source content

        Returns:
            Tuple of (is_valid, reason)
        """
        # Check if URL contains approved source
        is_approved = any(source in url.lower() for source in APPROVED_SOURCES)

        if not is_approved:
            return False, "Not from approved source"

        # Check if URL contains excluded patterns
        is_excluded = any(pattern in url.lower() for pattern in EXCLUDED_PATTERNS)

        if is_excluded:
            return False, "Contains excluded pattern (blog/opinion)"

        # Use LLM to double-check content type
        llm_valid = self._llm_validate(url, content)

        if not llm_valid:
            return False, "LLM classified as blog/opinion piece"

        return True, "Passed all validation checks"

    def _llm_validate(self, url: str, content: str) -> bool:
        """Use LLM to validate content type."""
        prompt = f"""
        Analyze this URL and content. Determine if this is a credible research/news article
        or if it's a blog/opinion/editorial piece.

        URL: {url}
        Content preview: {content[:500]}

        Respond with ONLY "VALID" if it's credible research/news.
        Respond with ONLY "INVALID" if it's a blog/opinion/editorial.
        """

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return "VALID" in response.content.upper()
        except Exception as e:
            print(f"LLM validation error: {e}")
            return True  # Default to valid if LLM fails

    def _create_summary(self, validated_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create summary for user review."""
        # Group by domain
        domains = {}
        for source in validated_sources:
            url = source.get("url", "")
            # Extract domain
            domain = url.split("//")[-1].split("/")[0] if "//" in url else url.split("/")[0]

            if domain not in domains:
                domains[domain] = []
            domains[domain].append(source)

        return {
            "total_sources": len(validated_sources),
            "domains": domains,
            "domain_counts": {domain: len(sources) for domain, sources in domains.items()}
        }

    def format_for_user_review(self, validation_summary: Dict[str, Any],
                                validated_sources: List[Dict[str, Any]]) -> str:
        """
        Format validation results for user review.

        Args:
            validation_summary: Summary from _create_summary
            validated_sources: List of validated sources

        Returns:
            Formatted string for display
        """
        output = "\n" + "=" * 80 + "\n"
        output += "SOURCE VALIDATION RESULTS\n"
        output += "=" * 80 + "\n\n"

        output += f"Total validated sources: {validation_summary['total_sources']}\n\n"

        output += "Sources by domain:\n"
        for domain, count in validation_summary['domain_counts'].items():
            output += f"  • {domain}: {count} source(s)\n"

        output += "\n" + "-" * 80 + "\n"
        output += "DETAILED SOURCE LIST:\n"
        output += "-" * 80 + "\n\n"

        for i, source in enumerate(validated_sources, 1):
            output += f"{i}. {source.get('title', 'Unknown')}\n"
            output += f"   URL: {source.get('url', '')}\n"
            output += f"   Validation: {source.get('validation_reason', 'N/A')}\n\n"

        output += "=" * 80 + "\n"

        return output


if __name__ == "__main__":
    # Test the agent
    agent = SourceValidatorAgent()

    print("=" * 80)
    print("Source Validation Agent Test")
    print("=" * 80)

    # Mock search results
    mock_results = [
        {
            "url": "https://www.brookings.edu/research/climate-policy",
            "title": "Climate Policy Research",
            "content": "This research paper examines the economic impacts of climate policy..."
        },
        {
            "url": "https://www.example.com/blog/my-opinion",
            "title": "My Opinion on Climate",
            "content": "I think climate change is important..."
        },
        {
            "url": "https://www.bbc.com/news/world-climate",
            "title": "BBC Climate News",
            "content": "New climate report shows increasing temperatures..."
        }
    ]

    validated, summary = agent.process(mock_results)

    print(f"\n{agent.format_for_user_review(summary, validated)}")
    print(f"\nValidated {len(validated)} out of {len(mock_results)} sources")
