"""
Streamlit Web App for Multi-Agent Debate Research System
With User Authentication and Configurable API Keys
"""

import streamlit as st
from orchestrator_secure import DebateResearchOrchestrator
from agents import SourceValidatorAgent
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables (only for Supabase config)
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Debate Research Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .citation {
        font-family: monospace;
        font-size: 0.9rem;
        color: #333;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase (optional - only if you want authentication)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = not bool(SUPABASE_URL)  # Auto-auth if no Supabase configured
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""
if 'tavily_api_key' not in st.session_state:
    st.session_state.tavily_api_key = ""
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'stage' not in st.session_state:
    st.session_state.stage = 'input'
if 'topic' not in st.session_state:
    st.session_state.topic = ""
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'validated_sources' not in st.session_state:
    st.session_state.validated_sources = []
if 'validation_summary' not in st.session_state:
    st.session_state.validation_summary = {}
if 'debate_case' not in st.session_state:
    st.session_state.debate_case = {}
if 'processing' not in st.session_state:
    st.session_state.processing = False


def authenticate_user(email: str, password: str) -> bool:
    """Authenticate user with Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return True  # Skip auth if not configured

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            st.session_state.authenticated = True
            st.session_state.user_email = email
            return True
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
    return False


def register_user(email: str, password: str) -> bool:
    """Register new user with Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.warning("Authentication not configured")
        return False

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if response.user:
            st.success("Registration successful! Please check your email to verify your account.")
            return True
    except Exception as e:
        st.error(f"Registration failed: {str(e)}")
    return False


def logout():
    """Logout user."""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.openai_api_key = ""
    st.session_state.tavily_api_key = ""
    st.session_state.orchestrator = None
    st.session_state.stage = 'input'


# Authentication UI
if not st.session_state.authenticated:
    st.markdown('<div class="main-header">🎯 Debate Research Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-powered debate case construction with credible sources</div>', unsafe_allow_html=True)

    if SUPABASE_URL and SUPABASE_KEY:
        # Show authentication form
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.subheader("Login to Your Account")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login", type="primary"):
                if authenticate_user(email, password):
                    st.success("Login successful!")
                    st.rerun()

        with tab2:
            st.subheader("Create New Account")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")

            if st.button("Register", type="primary"):
                if reg_password != reg_password_confirm:
                    st.error("Passwords do not match")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    register_user(reg_email, reg_password)
    else:
        # No auth configured, just proceed
        st.info("Authentication is not configured. Proceeding to API key setup.")
        st.session_state.authenticated = True
        st.rerun()

    st.stop()


# API Key Configuration UI
if not st.session_state.openai_api_key or not st.session_state.tavily_api_key:
    st.markdown('<div class="main-header">🎯 Debate Research Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Configure Your API Keys</div>', unsafe_allow_html=True)

    if st.session_state.user_email:
        st.info(f"Logged in as: {st.session_state.user_email}")

    st.warning("⚠️ Your API keys are stored only in your browser session and are never saved on our servers.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("OpenAI API Key")
        st.markdown("""
        **Required for:**
        - Query generation
        - Source analysis
        - Argument extraction
        - Citation formatting

        [Get your API key here](https://platform.openai.com/api-keys)
        """)
        openai_key = st.text_input(
            "Enter your OpenAI API Key",
            type="password",
            value=st.session_state.openai_api_key,
            key="openai_input"
        )

    with col2:
        st.subheader("Tavily API Key")
        st.markdown("""
        **Required for:**
        - Web search
        - Source retrieval

        [Get your API key here](https://tavily.com)

        Free tier: 1,000 searches/month
        """)
        tavily_key = st.text_input(
            "Enter your Tavily API Key",
            type="password",
            value=st.session_state.tavily_api_key,
            key="tavily_input"
        )

    st.markdown("---")

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

    with col_btn2:
        if st.button("Start Research", type="primary", disabled=not (openai_key and tavily_key)):
            st.session_state.openai_api_key = openai_key
            st.session_state.tavily_api_key = tavily_key

            # Initialize orchestrator with user's API keys
            st.session_state.orchestrator = DebateResearchOrchestrator(
                openai_api_key=openai_key,
                tavily_api_key=tavily_key
            )
            st.rerun()

    if SUPABASE_URL and SUPABASE_KEY:
        with col_btn3:
            if st.button("Logout"):
                logout()
                st.rerun()

    if not openai_key or not tavily_key:
        st.info("👆 Please enter both API keys to continue")

    st.stop()


# Main Application UI (after authentication and API key setup)
st.markdown('<div class="main-header">🎯 Debate Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered debate case construction with credible sources</div>', unsafe_allow_html=True)

# Sidebar - User Info and Settings
with st.sidebar:
    st.header("👤 User Info")

    if st.session_state.user_email:
        st.success(f"Logged in as:\n{st.session_state.user_email}")

    st.success("✅ OpenAI API: Configured")
    st.success("✅ Tavily API: Configured")

    if st.button("Update API Keys"):
        st.session_state.openai_api_key = ""
        st.session_state.tavily_api_key = ""
        st.session_state.orchestrator = None
        st.rerun()

    if SUPABASE_URL and SUPABASE_KEY:
        if st.button("Logout"):
            logout()
            st.rerun()

    st.markdown("---")

    st.header("📊 Workflow")
    stages = [
        ("1️⃣ Topic Input", "input"),
        ("2️⃣ Query Review", "query_review"),
        ("3️⃣ Search", "search"),
        ("4️⃣ Source Validation", "validation"),
        ("5️⃣ Results", "results")
    ]

    for stage_name, stage_id in stages:
        if st.session_state.stage == stage_id:
            st.markdown(f"**→ {stage_name}**")
        else:
            st.markdown(f"{stage_name}")

    st.markdown("---")

    st.header("⚙️ Settings")
    sources_per_side = st.slider("Sources per side", 5, 20, 15)
    max_results = st.slider("Max search results", 20, 100, 50)

    st.markdown("---")

    if st.button("🔄 Reset Workflow"):
        st.session_state.stage = 'input'
        st.session_state.topic = ""
        st.session_state.query = ""
        st.session_state.search_results = []
        st.session_state.validated_sources = []
        st.session_state.validation_summary = {}
        st.session_state.debate_case = {}
        st.session_state.processing = False
        st.rerun()

# Main content (workflow stages - same as before)
if st.session_state.stage == 'input':
    st.header("Step 1: Enter Your Debate Topic")

    user_input = st.text_area(
        "Enter your debate topic in natural language:",
        placeholder="Example: I want to debate whether nuclear energy should replace fossil fuels",
        height=100,
        key="user_input_field"
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("🚀 Generate Query", type="primary", disabled=st.session_state.processing):
            if user_input.strip():
                with st.spinner("Generating search query..."):
                    try:
                        query_result = st.session_state.orchestrator.query_generator.process(user_input)
                        st.session_state.topic = query_result["topic"]
                        st.session_state.query = query_result["query"]
                        st.session_state.stage = 'query_review'
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a topic first!")

elif st.session_state.stage == 'query_review':
    st.header("Step 2: Review Generated Query")

    st.subheader("📋 Extracted Topic")
    topic_edited = st.text_input(
        "Topic (editable):",
        value=st.session_state.topic,
        key="topic_edit_field"
    )

    if topic_edited != st.session_state.topic:
        st.session_state.topic = topic_edited

    st.subheader("🔍 Generated Search Query")

    query_edited = st.text_area(
        "Search Query (editable):",
        value=st.session_state.query,
        height=150,
        key="query_edit_field",
        help="You can directly edit the search query here"
    )

    if query_edited != st.session_state.query:
        st.session_state.query = query_edited
        st.info("✏️ Query manually edited")

    st.markdown("---")

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        if st.button("✏️ AI Refine"):
            st.session_state.stage = 'refine'
            st.rerun()

    with col2:
        if st.button("🔄 Regenerate"):
            with st.spinner("Regenerating query..."):
                try:
                    query_result = st.session_state.orchestrator.query_generator.process(st.session_state.topic)
                    st.session_state.query = query_result["query"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    with col3:
        if st.button("✅ Use Query", type="primary", disabled=st.session_state.processing):
            st.session_state.stage = 'search'
            st.session_state.processing = True
            st.rerun()

    with col4:
        if st.button("← Back"):
            st.session_state.stage = 'input'
            st.rerun()

elif st.session_state.stage == 'refine':
    st.header("Refine Your Query")

    st.subheader("Current Topic")
    st.info(st.session_state.topic)

    refinement_input = st.text_area(
        "Enter refinement instructions:",
        placeholder="Example: Make it more specific to the United States and focus on economic feasibility",
        height=100
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("← Back to Review"):
            st.session_state.stage = 'query_review'
            st.rerun()

    with col2:
        if st.button("🔄 Apply Refinement", type="primary"):
            if refinement_input.strip():
                with st.spinner("Refining query..."):
                    try:
                        refined = st.session_state.orchestrator.query_generator.refine_query(
                            st.session_state.topic,
                            refinement_input
                        )
                        st.session_state.topic = refined["topic"]
                        st.session_state.query = refined["query"]
                        st.session_state.stage = 'query_review'
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter refinement instructions!")

elif st.session_state.stage == 'search':
    st.header("Step 3: Searching & Validating Sources")

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("🔍 Searching for sources...")
        progress_bar.progress(20)
        search_results = st.session_state.orchestrator.search_retrieval.process(
            st.session_state.query,
            max_results
        )
        st.session_state.search_results = search_results

        status_text.text("✅ Validating sources...")
        progress_bar.progress(60)
        validated_sources, validation_summary = st.session_state.orchestrator.source_validator.process(
            search_results
        )
        st.session_state.validated_sources = validated_sources
        st.session_state.validation_summary = validation_summary

        progress_bar.progress(100)
        status_text.text("✓ Complete!")

        st.session_state.stage = 'validation'
        st.session_state.processing = False
        st.rerun()

    except Exception as e:
        st.error(f"Error during search: {str(e)}")
        st.session_state.processing = False

elif st.session_state.stage == 'validation':
    st.header("Step 4: Review Validated Sources")

    st.subheader(f"📊 Found {st.session_state.validation_summary.get('total_sources', 0)} Validated Sources")

    if st.session_state.validation_summary.get('domain_counts'):
        st.markdown("**Sources by Domain:**")
        cols = st.columns(3)
        domain_items = list(st.session_state.validation_summary['domain_counts'].items())

        for idx, (domain, count) in enumerate(domain_items):
            with cols[idx % 3]:
                st.metric(domain, count)

    st.markdown("---")

    with st.expander("📋 View Detailed Source List", expanded=True):
        for i, source in enumerate(st.session_state.validated_sources, 1):
            st.markdown(f"**{i}. {source.get('title', 'Unknown')}**")
            st.markdown(f"🔗 URL: {source.get('url', '')}")
            st.markdown(f"✓ {source.get('validation_reason', 'Validated')}")
            st.markdown("---")

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("❌ Reject & Refine"):
            st.session_state.stage = 'refine'
            st.rerun()

    with col2:
        if st.button("✅ Approve & Analyze", type="primary", disabled=st.session_state.processing):
            st.session_state.stage = 'analyze'
            st.session_state.processing = True
            st.rerun()

    with col3:
        if st.button("← Back to Search"):
            st.session_state.stage = 'query_review'
            st.rerun()

elif st.session_state.stage == 'analyze':
    st.header("Step 5: Analyzing Sources")

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("🔬 Analyzing and classifying sources...")
        progress_bar.progress(25)
        analyzed_sources = st.session_state.orchestrator.analysis_classifier.process(
            st.session_state.topic,
            st.session_state.validated_sources,
            sources_per_side
        )

        status_text.text("📝 Formatting citations...")
        progress_bar.progress(60)
        debate_case = st.session_state.orchestrator.citation_formatter.process(
            st.session_state.topic,
            analyzed_sources
        )
        st.session_state.debate_case = debate_case

        status_text.text("💾 Saving to database...")
        progress_bar.progress(90)
        st.session_state.orchestrator.vector_storage.process(debate_case)

        progress_bar.progress(100)
        status_text.text("✓ Analysis Complete!")

        st.session_state.stage = 'results'
        st.session_state.processing = False
        st.rerun()

    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        st.session_state.processing = False

elif st.session_state.stage == 'results':
    st.header("📊 Debate Research Results")

    debate_case = st.session_state.debate_case

    st.subheader("📋 Topic")
    st.info(debate_case.get('topic', 'Unknown'))

    st.markdown("---")

    col_for, col_against = st.columns(2)

    with col_for:
        st.subheader("✅ Arguments FOR")
        st.markdown(f"**Summary:**")
        st.write(debate_case.get('for_summary', 'No summary available'))

        st.markdown(f"**Sources ({len(debate_case.get('for_sources', []))}):**")
        for i, source in enumerate(debate_case.get('for_sources', []), 1):
            with st.expander(f"Source {i}", expanded=(i <= 3)):
                st.markdown(f"**Argument:** {source.get('argument', '')}")
                st.markdown(f"**Citation:**")
                st.code(source.get('citation', ''), language=None)

    with col_against:
        st.subheader("❌ Arguments AGAINST")
        st.markdown(f"**Summary:**")
        st.write(debate_case.get('against_summary', 'No summary available'))

        st.markdown(f"**Sources ({len(debate_case.get('against_sources', []))}):**")
        for i, source in enumerate(debate_case.get('against_sources', []), 1):
            with st.expander(f"Source {i}", expanded=(i <= 3)):
                st.markdown(f"**Argument:** {source.get('argument', '')}")
                st.markdown(f"**Citation:**")
                st.code(source.get('citation', ''), language=None)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        formatted_output = st.session_state.orchestrator.citation_formatter.format_output(debate_case)
        st.download_button(
            label="📥 Download as Text",
            data=formatted_output,
            file_name=f"debate_{debate_case.get('topic', 'research').replace(' ', '_')[:30]}.txt",
            mime="text/plain"
        )

    with col2:
        json_output = json.dumps(debate_case, indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json_output,
            file_name=f"debate_{debate_case.get('topic', 'research').replace(' ', '_')[:30]}.json",
            mime="application/json"
        )

    with col3:
        if st.button("🔄 New Research"):
            st.session_state.stage = 'input'
            st.session_state.topic = ""
            st.session_state.query = ""
            st.session_state.search_results = []
            st.session_state.validated_sources = []
            st.session_state.validation_summary = {}
            st.session_state.debate_case = {}
            st.session_state.processing = False
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Powered by LangChain, OpenAI GPT-4, and Tavily Search | "
    "🔒 Your API keys are stored only in your browser session"
    "</div>",
    unsafe_allow_html=True
)
