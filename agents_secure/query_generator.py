"""
Agent 1: Query Generator Agent
Converts natural language user input into formatted search query.
"""

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()


class QueryGeneratorAgent:
    """
    Agent responsible for converting user's natural language input
    into a formatted debate research query.
    """

    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3, api_key=openai_api_key)

    def process(self, user_input: str) -> Dict[str, str]:
        """
        Convert user's natural language input into formatted search query.

        Args:
            user_input: Natural language description of debate topic

        Returns:
            Dict containing:
                - topic: Extracted clean topic
                - query: Formatted search query string
        """
        # Extract clean topic
        topic = self._extract_topic(user_input)

        # Generate formatted query
        query = self._generate_query(topic)

        return {
            "topic": topic,
            "query": query
        }

    def _extract_topic(self, user_input: str) -> str:
        """Extract clean topic statement from user input."""
        prompt = f"""
        Extract a clear, concise debate topic from this user input.
        Convert it into a debate resolution format (a statement that can be argued for or against).

        User input: {user_input}

        Return ONLY the debate topic statement, nothing else.
        Examples:
        - "The United States should substantially increase its military presence in the South China Sea"
        - "Nuclear energy should replace fossil fuels"
        - "Social media companies should be regulated as public utilities"
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()

    def _generate_query(self, topic: str) -> str:
        """Generate formatted search query from topic."""
        prompt = f"""
        Convert this debate topic into an optimized search query following this template:

        Resolved: <topic> evidence arguments policy analysis site:brookings.edu OR site:cfr.org OR site:gmfus.org OR site:csis.org OR site:bbc.com OR site:reuters.com OR site:apnews.com -blog -opinion

        Topic: {topic}

        IMPORTANT:
        - Keep the query simple and focused on the main topic
        - Include the site: operators for credible sources
        - Add keywords: evidence, arguments, policy, analysis
        - Include -blog -opinion to exclude unreliable sources
        - Do NOT use complex AND/OR logic that might confuse search
        - Keep it under 200 characters if possible

        Return ONLY the formatted search query, nothing else.
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()

    def refine_query(self, original_topic: str, user_feedback: str) -> Dict[str, str]:
        """
        Refine search query based on user feedback.

        Args:
            original_topic: Original topic
            user_feedback: User's refinement instructions

        Returns:
            Dict containing refined topic and query
        """
        prompt = f"""
        Original topic: {original_topic}
        User feedback: {user_feedback}

        Based on the user's feedback, create a refined debate topic.
        Apply the user's suggestions to make the topic more specific or adjusted.

        Return ONLY the refined debate topic statement, nothing else.
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        refined_topic = response.content.strip()

        # Generate new query with refined topic
        query = self._generate_query(refined_topic)

        return {
            "topic": refined_topic,
            "query": query
        }


if __name__ == "__main__":
    # Test the agent
    agent = QueryGeneratorAgent()

    print("=" * 80)
    print("Query Generator Agent Test")
    print("=" * 80)

    # Test 1: Simple input
    user_input = "I want to debate whether we should have universal basic income"
    result = agent.process(user_input)
    print(f"\nInput: {user_input}")
    print(f"\nTopic: {result['topic']}")
    print(f"\nQuery: {result['query']}")
    print("=" * 80)

    # Test 2: Refinement
    feedback = "Make it more specific to the United States and focus on economic feasibility"
    refined = agent.refine_query(result['topic'], feedback)
    print(f"\nRefinement feedback: {feedback}")
    print(f"\nRefined Topic: {refined['topic']}")
    print(f"\nRefined Query: {refined['query']}")
    print("=" * 80)
