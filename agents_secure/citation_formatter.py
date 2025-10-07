"""
Agent 5: Citation Formatting Agent
Formats citations and generates debate case summaries.
"""

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


class CitationFormatterAgent:
    """
    Agent responsible for formatting citations and creating debate case summaries.
    """

    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3, api_key=openai_api_key)

    def process(self, topic: str, analyzed_sources: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Format citations and generate debate case.

        Args:
            topic: Debate topic
            analyzed_sources: Dict with 'for_sources' and 'against_sources'

        Returns:
            Complete debate case with formatted citations and summaries
        """
        for_sources = analyzed_sources.get("for_sources", [])
        against_sources = analyzed_sources.get("against_sources", [])

        # Format citations for all sources
        formatted_for = self._format_sources(for_sources)
        formatted_against = self._format_sources(against_sources)

        # Generate summaries
        for_summary = self._generate_summary(topic, formatted_for, "FOR")
        against_summary = self._generate_summary(topic, formatted_against, "AGAINST")

        return {
            "topic": topic,
            "for_summary": for_summary,
            "against_summary": against_summary,
            "for_sources": formatted_for,
            "against_sources": formatted_against
        }

    def _format_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format citations for a list of sources.

        Returns list of dicts with: citation, argument, url
        """
        formatted = []

        for source in sources:
            citation_data = source.get("citation_data", {})
            citation = self._format_citation(citation_data)

            formatted.append({
                "citation": citation,
                "argument": source.get("argument", ""),
                "url": source.get("url", "")
            })

        return formatted

    def _format_citation(self, citation_data: Dict[str, str]) -> str:
        """
        Format citation in required format.

        Format: Author's Last Name, Year [Full Name, "Title", Date, Publisher, URL]
        """
        return (
            f"{citation_data.get('author_last_name', 'Unknown')}, "
            f"{citation_data.get('year', 'Unknown')} "
            f"[{citation_data.get('author_full_name', 'Unknown')}, "
            f"\"{citation_data.get('title', 'Unknown')}\", "
            f"{citation_data.get('date', 'Unknown')}, "
            f"{citation_data.get('publisher', 'Unknown')}, "
            f"{citation_data.get('url', '')}]"
        )

    def _generate_summary(self, topic: str, sources: List[Dict[str, Any]], stance: str) -> str:
        """
        Generate cohesive summary of arguments.

        Args:
            topic: Debate topic
            sources: List of formatted sources
            stance: "FOR" or "AGAINST"

        Returns:
            3-4 sentence summary
        """
        if not sources:
            return f"No sources found for {stance} position."

        arguments_text = "\n".join([f"- {s['argument']}" for s in sources])

        prompt = f"""
        Topic: {topic}
        Stance: {stance}

        Key arguments from sources:
        {arguments_text}

        Write a cohesive 3-4 sentence summary of the main arguments {stance} the topic.
        Synthesize the key themes and evidence into a clear, persuasive summary.

        Return ONLY the summary, nothing else.
        """

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            print(f"Summary generation error: {e}")
            return f"Multiple sources present arguments {stance} the topic."

    def format_output(self, debate_case: Dict[str, Any]) -> str:
        """
        Format debate case for display.

        Args:
            debate_case: Complete debate case from process()

        Returns:
            Formatted string for output
        """
        output = f"""
{'='*80}
DEBATE RESEARCH: {debate_case['topic']}
{'='*80}

ARGUMENTS FOR
{'-'*80}
Summary: {debate_case['for_summary']}

Sources ({len(debate_case['for_sources'])}):
"""

        for i, source in enumerate(debate_case['for_sources'], 1):
            output += f"\n{i}. {source['argument']}\n   {source['citation']}\n"

        output += f"""
{'='*80}

ARGUMENTS AGAINST
{'-'*80}
Summary: {debate_case['against_summary']}

Sources ({len(debate_case['against_sources'])}):
"""

        for i, source in enumerate(debate_case['against_sources'], 1):
            output += f"\n{i}. {source['argument']}\n   {source['citation']}\n"

        output += f"\n{'='*80}\n"

        return output


if __name__ == "__main__":
    # Test the agent
    agent = CitationFormatterAgent()

    print("=" * 80)
    print("Citation Formatting Agent Test")
    print("=" * 80)

    # Mock analyzed sources
    mock_analyzed = {
        "for_sources": [
            {
                "argument": "Nuclear energy provides reliable, carbon-free baseload power with proven safety record.",
                "citation_data": {
                    "author_last_name": "Smith",
                    "author_full_name": "John Smith",
                    "title": "The Case for Nuclear Energy",
                    "date": "January 15, 2024",
                    "year": "2024",
                    "publisher": "Brookings Institution",
                    "url": "https://www.brookings.edu/research/nuclear"
                },
                "url": "https://www.brookings.edu/research/nuclear"
            }
        ],
        "against_sources": [
            {
                "argument": "Nuclear waste storage remains an unsolved problem with risks lasting thousands of years.",
                "citation_data": {
                    "author_last_name": "Jones",
                    "author_full_name": "Sarah Jones",
                    "title": "Nuclear Waste Concerns",
                    "date": "February 1, 2024",
                    "year": "2024",
                    "publisher": "BBC News",
                    "url": "https://www.bbc.com/news/nuclear-waste"
                },
                "url": "https://www.bbc.com/news/nuclear-waste"
            }
        ]
    }

    topic = "Nuclear energy should replace fossil fuels"
    debate_case = agent.process(topic, mock_analyzed)

    print(agent.format_output(debate_case))
