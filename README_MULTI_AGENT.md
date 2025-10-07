# Multi-Agent Debate Research System

An intelligent multi-agent system for automated debate research with user-in-the-loop validation.

## Architecture

The system uses **6 specialized agents** coordinated by an orchestrator:

```
User Input
    ↓
[Agent 1: Query Generator] ← User can refine
    ↓
[Agent 2: Search & Retrieval]
    ↓
[Agent 3: Source Validator] ← User confirms/refines
    ↓
[Agent 4: Analysis & Classifier]
    ↓
[Agent 5: Citation Formatter]
    ↓
[Agent 6: Vector Storage]
    ↓
Debate Case Output
```

## Agents

### Agent 1: Query Generator
- **Input**: Natural language user input
- **Output**: Clean debate topic + formatted search query
- **Features**:
  - Extracts debate topic from conversational input
  - Formats query using your template
  - Supports refinement based on user feedback

### Agent 2: Search & Retrieval
- **Input**: Formatted search query
- **Output**: Raw search results with scraped content
- **Features**:
  - Tavily API integration for web search
  - Content scraping with BeautifulSoup
  - Retrieves up to 50 results

### Agent 3: Source Validator
- **Input**: Raw search results
- **Output**: Validated sources list
- **Features**:
  - Filters to approved sources only (Brookings, BBC, Reuters, etc.)
  - Excludes blogs/opinion pieces
  - **User confirmation workflow**
  - **Refinement loop** if user rejects sources

### Agent 4: Analysis & Classifier
- **Input**: Validated sources + topic
- **Output**: Analyzed sources with stance classification
- **Features**:
  - Classifies each source as FOR/AGAINST/NEUTRAL
  - Extracts key arguments
  - Extracts citation metadata

### Agent 5: Citation Formatter
- **Input**: Analyzed sources
- **Output**: Formatted debate case
- **Features**:
  - Formats citations: `Author, Year [Full Name, "Title", Date, Publisher, URL]`
  - Generates cohesive summaries for each side
  - Creates structured debate brief

### Agent 6: Vector Storage
- **Input**: Complete debate case
- **Output**: Storage confirmation
- **Features**:
  - Stores in ChromaDB for caching
  - Enables retrieval of past research
  - Semantic search capabilities

## Installation

Already installed! Dependencies are in `requirements.txt`.

## Usage

### Interactive Mode (Recommended)

```bash
python orchestrator.py
```

This launches an interactive CLI where you can:
1. Enter topics in natural language
2. Review and refine the generated query
3. **Approve or reject validated sources**
4. **Provide refinement feedback** if sources aren't satisfactory
5. View final formatted debate case

### Example Session

```
Enter your debate topic: I want to debate climate change policy

[Agent 1: Query Generator]
Topic: The United States should implement comprehensive climate change policy
Query: Resolved: climate change policy evidence file OR...

Would you like to refine the topic/query? (y/n): n

[Agent 2: Search & Retrieval]
Retrieved 45 results

[Agent 3: Source Validation]
✓ Valid: https://www.brookings.edu/research/climate-policy
✗ Rejected: https://example.com/blog - Not from approved source
...

SOURCE VALIDATION RESULTS
Total validated sources: 28

Sources by domain:
  • brookings.edu: 8 source(s)
  • bbc.com: 6 source(s)
  • reuters.com: 5 source(s)
  ...

Approve these 28 validated sources? (y/n): y

[Agent 4: Analysis & Classification]
✓ FOR (5/15): Climate Policy Economic Benefits
✓ AGAINST (3/15): Cost Concerns for Climate Regulation
...

[Research Complete - Formatted output displayed]
```

### Programmatic Usage

```python
from orchestrator import DebateResearchOrchestrator

orchestrator = DebateResearchOrchestrator()

debate_case = orchestrator.run(
    user_input="Should we implement universal basic income?",
    sources_per_side=15,
    auto_approve=False  # Enable user interaction
)

orchestrator.display_results(debate_case)
```

### Testing Individual Agents

Each agent can be tested independently:

```bash
# Test Query Generator
python agents/query_generator.py

# Test Search & Retrieval
python agents/search_retrieval.py

# Test Source Validator
python agents/source_validator.py

# etc.
```

## User Interaction Points

### 1. Query Refinement
After Agent 1 generates the query:
- **Approve**: Continue to search
- **Refine**: Provide feedback to adjust the topic/query

### 2. Source Validation (Key Interaction)
After Agent 3 validates sources:
- **Approve**: Continue to analysis
- **Reject**: Choose to:
  - `r` - Refine search query and re-run search
  - `s` - Skip and continue with current sources
  - `q` - Quit research

This creates a **feedback loop** back to Agent 1 if refinement is needed.

### 3. Cached Results
If research exists for the topic:
- **Use cached**: Skip research and return cached results
- **New search**: Perform fresh research

## Workflow Diagram

```
┌─────────────────┐
│   User Input    │
│ "debate climate"│
└────────┬────────┘
         ↓
┌─────────────────┐
│   Agent 1       │◄──── User Refine Loop
│ Query Generator │
└────────┬────────┘
         ↓
┌─────────────────┐
│   Agent 2       │
│ Search/Retrieval│
└────────┬────────┘
         ↓
┌─────────────────┐
│   Agent 3       │◄──┐
│ Source Validator│   │
└────────┬────────┘   │
         ↓             │
    User Review        │
         ↓             │
   Approved? ──No──────┘ (Refine & Re-search)
         Yes
         ↓
┌─────────────────┐
│   Agent 4       │
│  Classifier     │
└────────┬────────┘
         ↓
┌─────────────────┐
│   Agent 5       │
│Citation Formatter│
└────────┬────────┘
         ↓
┌─────────────────┐
│   Agent 6       │
│ Vector Storage  │
└────────┬────────┘
         ↓
    Final Output
```

## File Structure

```
LangChain/
├── agents/
│   ├── __init__.py
│   ├── query_generator.py        # Agent 1
│   ├── search_retrieval.py       # Agent 2
│   ├── source_validator.py       # Agent 3 (with user confirmation)
│   ├── analysis_classifier.py    # Agent 4
│   ├── citation_formatter.py     # Agent 5
│   └── vector_storage.py         # Agent 6
├── orchestrator.py               # Main orchestrator with user interaction
├── vector_store/                 # ChromaDB storage
└── debate_agent.py              # Legacy monolithic version
```

## Key Features

### User-in-the-Loop Validation
- View all validated sources before proceeding
- Reject and refine search if sources are inadequate
- Ensures high-quality, relevant research

### Modular Agent Design
- Each agent has single responsibility
- Easy to test and modify independently
- Clear data flow between agents

### Feedback Loops
- Query refinement at generation stage
- Source validation with re-search capability
- Cached results checking

### Citation Quality
- Proper debate format: `Author, Year [Details...]`
- LLM extraction of metadata
- Fallback handling for missing information

## Configuration

### Approved Sources
Edit `agents/source_validator.py`:

```python
APPROVED_SOURCES = [
    "brookings.edu",
    "cfr.org",
    # Add more...
]
```

### Excluded Patterns
Edit `agents/source_validator.py`:

```python
EXCLUDED_PATTERNS = [
    "blog",
    "opinion",
    # Add more...
]
```

## Advantages of Multi-Agent Architecture

1. **Separation of Concerns**: Each agent focuses on one task
2. **User Control**: Validation checkpoints prevent wasted processing
3. **Modularity**: Easy to swap/upgrade individual agents
4. **Testability**: Test each agent independently
5. **Transparency**: Clear workflow visibility for users
6. **Refinement**: Feedback loops improve results

## Example Output

```
================================================================================
DEBATE RESEARCH: Nuclear energy should replace fossil fuels
================================================================================

ARGUMENTS FOR
--------------------------------------------------------------------------------
Summary: Nuclear energy provides reliable, carbon-free baseload power with proven
safety records in modern facilities. Economic analyses show nuclear is cost-
competitive with renewables when factoring in grid reliability and land use.

Sources (15):
1. Modern nuclear facilities demonstrate exceptional safety records with advanced
   passive cooling systems and redundant safety mechanisms.
   Smith, 2024 [John Smith, "Nuclear Safety in the 21st Century", January 15, 2024,
   Brookings Institution, https://brookings.edu/...]

2. Nuclear power generates consistent baseload electricity unlike intermittent
   renewables, crucial for grid stability.
   Jones, 2024 [Sarah Jones, "Baseload Power Analysis", February 1, 2024,
   Council on Foreign Relations, https://cfr.org/...]

[... 13 more sources ...]

================================================================================

ARGUMENTS AGAINST
--------------------------------------------------------------------------------
Summary: Nuclear waste storage remains an unsolved problem with radioactive materials
requiring secure containment for thousands of years. High construction costs and long
build times make nuclear economically unfeasible compared to rapidly improving renewables.

Sources (15):
[... 15 sources with citations ...]
```

## API Requirements

- **OPENAI_API_KEY**: For LLM analysis (already configured)
- **TAVILY_API_KEY**: For web search (already configured)

## Next Steps

1. Run `python orchestrator.py` to start interactive mode
2. Test with your debate topic
3. Review and refine sources when prompted
4. Examine the formatted output

The system is fully functional and ready to use!
