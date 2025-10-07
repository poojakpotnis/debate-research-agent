"""
Secure Debate Research Orchestrator
Coordinates all agents with user-provided API keys (no .env dependency)
"""

from agents_secure import (
    QueryGeneratorAgent,
    SearchRetrievalAgent,
    SourceValidatorAgent,
    AnalysisClassifierAgent,
    CitationFormatterAgent,
    VectorStorageAgent
)
from typing import Dict, Any, Optional


class DebateResearchOrchestrator:
    """
    Orchestrates the multi-agent debate research workflow with user-provided API keys.
    """

    def __init__(self, openai_api_key: str, tavily_api_key: str):
        """
        Initialize orchestrator with user API keys.

        Args:
            openai_api_key: User's OpenAI API key
            tavily_api_key: User's Tavily API key
        """
        self.query_generator = QueryGeneratorAgent(openai_api_key)
        self.search_retrieval = SearchRetrievalAgent(tavily_api_key)
        self.source_validator = SourceValidatorAgent(openai_api_key)
        self.analysis_classifier = AnalysisClassifierAgent(openai_api_key)
        self.citation_formatter = CitationFormatterAgent(openai_api_key)
        self.vector_storage = VectorStorageAgent()

    def run(self, user_input: str, sources_per_side: int = 15,
            max_search_results: int = 50, auto_approve: bool = False) -> Dict[str, Any]:
        """
        Run the complete debate research workflow.

        Args:
            user_input: Natural language topic from user
            sources_per_side: Target number of sources per side
            max_search_results: Maximum search results to retrieve
            auto_approve: If True, skip user confirmation (for testing)

        Returns:
            Complete debate case
        """
        print("\n" + "="*80)
        print("DEBATE RESEARCH ORCHESTRATOR")
        print("="*80 + "\n")

        # Check if we have cached results
        print("Checking for cached results...")
        cached = self._check_cache(user_input)
        if cached:
            use_cached = self._ask_user_yes_no(
                "Found cached research for this topic. Use cached results? (y/n): "
            ) if not auto_approve else False

            if use_cached:
                print("\nUsing cached results!")
                return cached

        # Agent 1: Query Generation
        print("\n[Agent 1: Query Generator]")
        print("-" * 80)
        query_result = self.query_generator.process(user_input)
        topic = query_result["topic"]
        query = query_result["query"]

        print(f"Topic: {topic}")
        print(f"Query: {query}\n")

        # Refinement loop
        if not auto_approve:
            while True:
                refine = self._ask_user_yes_no(
                    "Would you like to refine the topic/query? (y/n): "
                )
                if not refine:
                    break

                feedback = input("Enter refinement instructions: ")
                query_result = self.query_generator.refine_query(topic, feedback)
                topic = query_result["topic"]
                query = query_result["query"]

                print(f"\nRefined Topic: {topic}")
                print(f"Refined Query: {query}\n")

        # Agent 2: Search & Retrieval
        print("\n[Agent 2: Search & Retrieval]")
        print("-" * 80)
        search_results = self.search_retrieval.process(query, max_search_results)
        print(f"\nRetrieved {len(search_results)} results\n")

        # Agent 3: Source Validation (with user confirmation loop)
        print("\n[Agent 3: Source Validation]")
        print("-" * 80)

        while True:
            validated_sources, validation_summary = self.source_validator.process(search_results)

            # Display validation results to user
            print(self.source_validator.format_for_user_review(
                validation_summary, validated_sources
            ))

            if not auto_approve:
                approved = self._ask_user_yes_no(
                    f"\nApprove these {len(validated_sources)} validated sources? (y/n): "
                )

                if approved:
                    break
                else:
                    # Ask for refinement
                    print("\nSource validation not approved.")
                    refine_choice = input(
                        "Enter 'r' to refine search query, 's' to skip and continue, or 'q' to quit: "
                    ).lower()

                    if refine_choice == 'q':
                        print("Research cancelled by user.")
                        return {}
                    elif refine_choice == 's':
                        print("Continuing with current sources...")
                        break
                    elif refine_choice == 'r':
                        feedback = input("Enter search refinement instructions: ")
                        query_result = self.query_generator.refine_query(topic, feedback)
                        topic = query_result["topic"]
                        query = query_result["query"]

                        print(f"\nRefined Query: {query}")
                        print("Re-running search...\n")

                        # Re-run search with refined query
                        search_results = self.search_retrieval.process(query, max_search_results)
                        print(f"Retrieved {len(search_results)} new results\n")
                        continue
            else:
                break

        # Agent 4: Analysis & Classification
        print("\n[Agent 4: Analysis & Classification]")
        print("-" * 80)
        analyzed_sources = self.analysis_classifier.process(
            topic, validated_sources, sources_per_side
        )

        print(f"\nClassified {len(analyzed_sources['for_sources'])} FOR sources")
        print(f"Classified {len(analyzed_sources['against_sources'])} AGAINST sources\n")

        # Agent 5: Citation Formatting
        print("\n[Agent 5: Citation Formatting]")
        print("-" * 80)
        debate_case = self.citation_formatter.process(topic, analyzed_sources)
        print("Citations formatted and summaries generated\n")

        # Agent 6: Vector Storage
        print("\n[Agent 6: Vector Storage]")
        print("-" * 80)
        self.vector_storage.process(debate_case)

        print("\n" + "="*80)
        print("RESEARCH COMPLETE")
        print("="*80 + "\n")

        return debate_case

    def _check_cache(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Check if we have cached results for this topic."""
        # First convert to topic
        try:
            query_result = self.query_generator.process(user_input)
            topic = query_result["topic"]
            return self.vector_storage.retrieve_by_topic(topic)
        except Exception:
            return None

    def _ask_user_yes_no(self, prompt: str) -> bool:
        """Ask user a yes/no question."""
        while True:
            response = input(prompt).lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")

    def display_results(self, debate_case: Dict[str, Any]):
        """Display formatted debate case."""
        if not debate_case:
            print("No results to display.")
            return

        print(self.citation_formatter.format_output(debate_case))
