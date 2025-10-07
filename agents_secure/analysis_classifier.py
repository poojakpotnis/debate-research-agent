"""
Agent 4: Analysis & Classification Agent
Classifies stance (FOR/AGAINST) and extracts key arguments and citation metadata.
"""

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from typing import List, Dict, Any
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class AnalysisClassifierAgent:
    """
    Agent responsible for analyzing sources, classifying stance,
    and extracting arguments and citation data.
    """

    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3, api_key=openai_api_key)

    def process(self, topic: str, validated_sources: List[Dict[str, Any]],
                sources_per_side: int = 15) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze sources and classify by stance.

        Args:
            topic: Debate topic
            validated_sources: List of validated sources
            sources_per_side: Target number of sources per side

        Returns:
            Dict with 'for_sources' and 'against_sources' lists
        """
        for_sources = []
        against_sources = []

        print(f"\nAnalyzing {len(validated_sources)} sources for topic: {topic}\n")

        for source in validated_sources:
            url = source.get("url", "")
            content = source.get("content", "")
            title = source.get("title", "Unknown")

            # Classify stance
            stance = self._classify_stance(topic, content)

            if stance == "NEUTRAL":
                print(f"⊘ Neutral (skipping): {title}")
                continue

            # Extract citation data
            citation_data = self._extract_citation_data(url, content, title)

            # Extract key argument
            argument = self._extract_argument(topic, content, stance)

            analyzed_source = {
                "url": url,
                "title": title,
                "content": content,
                "stance": stance,
                "argument": argument,
                "citation_data": citation_data
            }

            # Add to appropriate list
            if stance == "FOR" and len(for_sources) < sources_per_side:
                for_sources.append(analyzed_source)
                print(f"✓ FOR ({len(for_sources)}/{sources_per_side}): {title}")
            elif stance == "AGAINST" and len(against_sources) < sources_per_side:
                against_sources.append(analyzed_source)
                print(f"✓ AGAINST ({len(against_sources)}/{sources_per_side}): {title}")

            # Stop if we have enough
            if len(for_sources) >= sources_per_side and len(against_sources) >= sources_per_side:
                break

        return {
            "for_sources": for_sources,
            "against_sources": against_sources
        }

    def _classify_stance(self, topic: str, content: str) -> str:
        """
        Classify if content supports FOR or AGAINST the topic.

        Returns: "FOR", "AGAINST", or "NEUTRAL"
        """
        prompt = f"""
        Topic: {topic}

        Content: {content[:2000]}

        Does this content primarily support arguments FOR or AGAINST the topic?
        Consider the main thesis and evidence presented.

        Respond with ONLY one word: "FOR", "AGAINST", or "NEUTRAL"
        """

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = response.content.strip().upper()

            if "FOR" in result and "AGAINST" not in result:
                return "FOR"
            elif "AGAINST" in result:
                return "AGAINST"
            return "NEUTRAL"
        except Exception as e:
            print(f"Stance classification error: {e}")
            return "NEUTRAL"

    def _extract_citation_data(self, url: str, content: str, title: str) -> Dict[str, str]:
        """
        Extract citation information using LLM.

        Returns dict with: author_last_name, author_full_name, title, date, year, publisher, url
        """
        prompt = f"""
        Extract citation information from this article:

        URL: {url}
        Title: {title}
        Content: {content[:1500]}

        Return a JSON object with these fields:
        {{
            "author_last_name": "Last name of primary author or organization",
            "author_full_name": "Full name of primary author or organization name",
            "title": "Article title",
            "date": "Publication date (format: Month Day, Year)",
            "year": "Publication year",
            "publisher": "Publisher/Organization name"
        }}

        If any field cannot be determined from the content, use "Unknown".
        For organizational authors (like Brookings Institution), use the org name for both author fields.
        Return ONLY valid JSON, nothing else.
        """

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            citation_data = json.loads(response.content.strip())
            citation_data["url"] = url
            return citation_data
        except (json.JSONDecodeError, Exception) as e:
            print(f"Citation extraction error for {url}: {e}")
            return {
                "author_last_name": "Unknown",
                "author_full_name": "Unknown",
                "title": title,
                "date": "Unknown",
                "year": str(datetime.now().year),
                "publisher": "Unknown",
                "url": url
            }

    def _extract_argument(self, topic: str, content: str, stance: str) -> str:
        """
        Extract the primary argument from content.

        Returns: Concise 1-2 sentence summary of key argument
        """
        prompt = f"""
        Topic: {topic}
        Stance: {stance}

        Content: {content[:2000]}

        Extract the PRIMARY argument from this content that supports the {stance} position.
        Provide a concise 1-2 sentence summary that captures the main point and evidence.

        Return ONLY the argument summary, nothing else.
        """

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            print(f"Argument extraction error: {e}")
            return "Unable to extract argument summary."


if __name__ == "__main__":
    # Test the agent
    agent = AnalysisClassifierAgent()

    print("=" * 80)
    print("Analysis & Classification Agent Test")
    print("=" * 80)

    # Mock validated sources
    mock_sources = [
        {
            "url": "https://www.brookings.edu/research/nuclear-energy",
            "title": "The Case for Nuclear Energy",
            "content": "Nuclear energy provides reliable, carbon-free baseload power. Studies show it is one of the safest forms of energy production when modern safety protocols are followed. France generates 70% of its electricity from nuclear with excellent safety record."
        },
        {
            "url": "https://www.bbc.com/news/nuclear-concerns",
            "title": "Nuclear Waste Concerns Grow",
            "content": "Environmental groups raise concerns about nuclear waste storage. The Fukushima disaster highlighted risks of nuclear power. Renewable energy alternatives are becoming more cost-effective without the long-term waste issues."
        }
    ]

    topic = "Nuclear energy should replace fossil fuels"

    results = agent.process(topic, mock_sources, sources_per_side=10)

    print("\n" + "=" * 80)
    print(f"FOR sources: {len(results['for_sources'])}")
    print(f"AGAINST sources: {len(results['against_sources'])}")
    print("=" * 80)
