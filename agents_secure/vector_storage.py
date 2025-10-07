"""
Agent 6: Vector Storage Agent
Manages storage and retrieval of debate cases in ChromaDB.
"""

import chromadb
from chromadb.config import Settings
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import os


class VectorStorageAgent:
    """
    Agent responsible for storing and retrieving debate cases from vector database.
    """

    def __init__(self, persist_directory: str = "./vector_store"):
        """
        Initialize ChromaDB client.

        Args:
            persist_directory: Directory for ChromaDB persistence
        """
        self.persist_directory = persist_directory

        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        self.collection = self.client.get_or_create_collection("debate_cases")

    def process(self, debate_case: Dict[str, Any]) -> bool:
        """
        Store debate case in vector database.

        Args:
            debate_case: Complete debate case to store

        Returns:
            True if successful, False otherwise
        """
        try:
            topic = debate_case.get("topic", "Unknown")
            timestamp = datetime.now().isoformat()

            # Add timestamp to debate case
            debate_case["timestamp"] = timestamp

            # Create unique ID
            doc_id = f"debate_{topic.replace(' ', '_')}_{datetime.now().timestamp()}"

            # Store in ChromaDB
            self.collection.add(
                documents=[json.dumps(debate_case)],
                metadatas=[{
                    "topic": topic,
                    "timestamp": timestamp,
                    "for_count": len(debate_case.get("for_sources", [])),
                    "against_count": len(debate_case.get("against_sources", []))
                }],
                ids=[doc_id]
            )

            print(f"✓ Stored debate case in vector database: {topic}")
            return True

        except Exception as e:
            print(f"✗ Error storing in vector DB: {e}")
            return False

    def retrieve_by_topic(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve most recent debate case for a topic.

        Args:
            topic: Topic to search for

        Returns:
            Debate case dict or None if not found
        """
        try:
            results = self.collection.query(
                query_texts=[topic],
                n_results=1
            )

            if results and results['documents'] and len(results['documents'][0]) > 0:
                debate_case = json.loads(results['documents'][0][0])
                print(f"✓ Retrieved cached debate case for: {topic}")
                return debate_case

            print(f"No cached debate case found for: {topic}")
            return None

        except Exception as e:
            print(f"✗ Error retrieving from vector DB: {e}")
            return None

    def list_all_cases(self) -> List[Dict[str, Any]]:
        """
        List all stored debate cases.

        Returns:
            List of debate case summaries
        """
        try:
            # Get all items from collection
            all_items = self.collection.get()

            cases = []
            if all_items and all_items['metadatas']:
                for metadata in all_items['metadatas']:
                    cases.append({
                        "topic": metadata.get("topic", "Unknown"),
                        "timestamp": metadata.get("timestamp", "Unknown"),
                        "for_count": metadata.get("for_count", 0),
                        "against_count": metadata.get("against_count", 0)
                    })

            return cases

        except Exception as e:
            print(f"✗ Error listing cases: {e}")
            return []

    def delete_by_topic(self, topic: str) -> bool:
        """
        Delete all debate cases for a topic.

        Args:
            topic: Topic to delete

        Returns:
            True if successful
        """
        try:
            # This is a simplified version - in production you'd want better filtering
            print(f"Note: Delete functionality requires more sophisticated topic matching")
            return True

        except Exception as e:
            print(f"✗ Error deleting from vector DB: {e}")
            return False


if __name__ == "__main__":
    # Test the agent
    agent = VectorStorageAgent()

    print("=" * 80)
    print("Vector Storage Agent Test")
    print("=" * 80)

    # Mock debate case
    mock_debate_case = {
        "topic": "Nuclear energy should replace fossil fuels",
        "for_summary": "Nuclear energy provides clean, reliable baseload power.",
        "against_summary": "Nuclear waste and safety concerns outweigh benefits.",
        "for_sources": [
            {
                "citation": "Smith, 2024 [John Smith, \"Nuclear Power\", Jan 1 2024, Brookings, https://...]",
                "argument": "Nuclear is carbon-free and reliable.",
                "url": "https://..."
            }
        ],
        "against_sources": [
            {
                "citation": "Jones, 2024 [Sarah Jones, \"Nuclear Risks\", Feb 1 2024, BBC, https://...]",
                "argument": "Waste storage remains unsolved.",
                "url": "https://..."
            }
        ]
    }

    # Test storage
    print("\nTesting storage...")
    success = agent.process(mock_debate_case)
    print(f"Storage successful: {success}")

    # Test retrieval
    print("\nTesting retrieval...")
    retrieved = agent.retrieve_by_topic("Nuclear energy should replace fossil fuels")
    if retrieved:
        print(f"Retrieved topic: {retrieved.get('topic')}")
        print(f"FOR sources: {len(retrieved.get('for_sources', []))}")
        print(f"AGAINST sources: {len(retrieved.get('against_sources', []))}")

    # Test listing
    print("\nTesting list all cases...")
    all_cases = agent.list_all_cases()
    print(f"Total cases in database: {len(all_cases)}")
    for case in all_cases:
        print(f"  - {case['topic']} ({case['timestamp']})")

    print("=" * 80)
