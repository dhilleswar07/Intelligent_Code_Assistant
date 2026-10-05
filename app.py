import streamlit as st
from rag_pipeline import CodeRAG


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CodeMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown("""
<style>

    /* ---------- MAIN APP ---------- */

    .stApp {
        background-color: #080b12;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background-color: #0c1018;
        border-right: 1px solid #1e293b;
    }


    /* ---------- HEADINGS ---------- */

    h1, h2, h3 {
        color: #f8fafc !important;
    }

    p {
        color: #94a3b8;
    }


    /* ---------- METRIC CARDS ---------- */

    div[data-testid="metric-container"] {
        background-color: #111827;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 15px;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc;
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
    }


    /* ---------- BUTTONS ---------- */

    .stButton > button {
        width: 100%;
        min-height: 42px;

        border-radius: 10px;

        background-color: #111827;
        color: #e2e8f0;

        border: 1px solid #263244;

        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #1e293b;
        border-color: #6366f1;
        color: white;
    }


    /* ---------- CHAT ---------- */

    [data-testid="stChatMessage"] {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 14px;
        margin-bottom: 10px;
    }


    /* ---------- CHAT INPUT ---------- */

    [data-testid="stChatInput"] {
        border-color: #334155;
    }


    /* ---------- CODE ---------- */

    pre {
        border-radius: 10px !important;
    }


    /* ---------- EXPANDERS ---------- */

    details {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
    }


    /* ---------- DIVIDER ---------- */

    hr {
        border-color: #1e293b;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD RAG
# ============================================================

@st.cache_resource
def load_rag():
    return CodeRAG(data_folder="data")


try:

    rag = load_rag()

except Exception as e:

    st.error(f"Could not load CodeMind AI: {e}")
    st.stop()


# ============================================================
# STATISTICS
# ============================================================

indexed_chunks = len(rag.documents)

code_files = len(
    set(
        document["file_name"]
        for document in rag.documents
    )
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "Ask"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🧠 CodeMind AI")

    st.caption(
        "Intelligent Code Assistant"
    )

    st.divider()

    st.subheader("⚡ Assistant Mode")

    mode = st.radio(
        "Mode",
        [
            "Ask",
            "Explain",
            "Debug",
            "Optimize",
            "Generate Tests"
        ],
        index=[
            "Ask",
            "Explain",
            "Debug",
            "Optimize",
            "Generate Tests"
        ].index(st.session_state.mode),
        label_visibility="collapsed"
    )

    st.session_state.mode = mode

    st.divider()

    st.subheader("🧠 RAG Pipeline")

    st.success("Codebase indexed")
    st.success("Embeddings ready")
    st.success("FAISS ready")
    st.success("BM25 ready")
    st.success("FlashRank ready")
    st.success("Groq connected")

    st.divider()

    st.subheader("📊 Knowledge Base")

    st.metric(
        "Code Files",
        code_files
    )

    st.metric(
        "Indexed Chunks",
        indexed_chunks
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation"
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# HERO SECTION
# ============================================================

st.caption(
    "✦ RAG-POWERED DEVELOPER INTELLIGENCE"
)

st.title(
    "Understand Your Codebase."
)

st.write(
    """
    Ask questions, debug problems, explain functions,
    optimize code and generate tests using an
    intelligent retrieval-augmented AI assistant.
    """
)

st.success(
    "● AI Engine Online"
)


# ============================================================
# DASHBOARD
# ============================================================

st.subheader("📊 Codebase Overview")

m1, m2, m3, m4 = st.columns(4)

with m1:

    st.metric(
        "📁 Code Files",
        code_files
    )

with m2:

    st.metric(
        "🧩 Indexed Chunks",
        indexed_chunks
    )

with m3:

    st.metric(
        "🔎 Retrieval",
        "Hybrid"
    )

with m4:

    st.metric(
        "⚡ Reranking",
        "FlashRank"
    )


# ============================================================
# QUICK ACTIONS
# ============================================================

st.subheader(
    "🚀 Quick Actions"
)

st.caption(
    "Choose an action to start analyzing your code."
)

q1, q2, q3, q4 = st.columns(4)

quick_question = None


with q1:

    if st.button(
        "💡 Explain Code"
    ):

        quick_question = (
            "Explain the most important functions "
            "in this codebase."
        )


with q2:

    if st.button(
        "🐛 Find Bugs"
    ):

        quick_question = (
            "Find potential bugs, errors, and "
            "edge cases in this codebase."
        )


with q3:

    if st.button(
        "⚡ Optimize"
    ):

        quick_question = (
            "How can this codebase be optimized "
            "for performance and readability?"
        )


with q4:

    if st.button(
        "🧪 Generate Tests"
    ):

        quick_question = (
            "Generate unit tests for the important "
            "functions in this codebase."
        )


# ============================================================
# CHAT AREA
# ============================================================

st.divider()

st.subheader(
    "💬 CodeMind Chat"
)


# Display previous messages

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# Chat input

user_question = st.chat_input(
    "Ask something about your codebase..."
)


# Quick action overrides chat input

if quick_question:

    user_question = quick_question


# ============================================================
# PROCESS USER QUESTION
# ============================================================

if user_question:

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    with st.chat_message("user"):

        st.markdown(
            user_question
        )


    # --------------------------------------------------------
    # MODE INSTRUCTIONS
    # --------------------------------------------------------

    mode_instruction = ""

    if st.session_state.mode == "Explain":

        mode_instruction = """
        Explain the code step-by-step and
        use simple technical language.
        """

    elif st.session_state.mode == "Debug":

        mode_instruction = """
        Focus on bugs, exceptions,
        incorrect logic and edge cases.
        """

    elif st.session_state.mode == "Optimize":

        mode_instruction = """
        Focus on performance,
        efficiency and maintainability.
        """

    elif st.session_state.mode == "Generate Tests":

        mode_instruction = """
        Generate practical unit tests
        for relevant functions.
        """


    final_question = f"""
Assistant Mode:
{st.session_state.mode}

Instructions:
{mode_instruction}

User Question:
{user_question}
"""


    # --------------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "🧠 Searching codebase..."
            ):

                answer, sources = rag.ask(
                    final_question
                )


            # ------------------------------------------------
            # ANSWER
            # ------------------------------------------------

            st.markdown(
                answer
            )


            # ------------------------------------------------
            # SOURCES
            # ------------------------------------------------

            if sources:

                st.divider()

                st.subheader(
                    "📚 Retrieved Sources"
                )

                st.caption(
                    "Code chunks used to generate the answer."
                )


                for i, source in enumerate(
                    sources,
                    start=1
                ):

                    score = source.get(
                        "rerank_score",
                        0
                    )

                    title = (
                        f"#{i}  "
                        f"📄 {source['file_name']}  "
                        f"| Chunk {source['chunk_index']}  "
                        f"| Score {score:.4f}"
                    )

                    with st.expander(
                        title
                    ):

                        st.code(
                            source["content"],
                            language="python"
                        )

                        st.caption(
                            f"Path: {source['file_path']}"
                        )


            # ------------------------------------------------
            # SAVE RESPONSE
            # ------------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )


        except Exception as e:

            error_message = (
                f"Something went wrong: {e}"
            )

            st.error(
                error_message
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message
                }
            )


# ============================================================
# TECHNOLOGY SECTION
# ============================================================

st.divider()

st.subheader(
    "⚙️ How CodeMind Works"
)

st.caption(
    "A retrieval-augmented pipeline designed for code understanding."
)


t1, t2, t3 = st.columns(3)


with t1:

    with st.container(border=True):

        st.markdown(
            "### 🔎 Hybrid Retrieval"
        )

        st.write(
            """
            Combines semantic search using FAISS
            with keyword retrieval using BM25
            to find relevant code.
            """
        )


with t2:

    with st.container(border=True):

        st.markdown(
            "### 🎯 Intelligent Reranking"
        )

        st.write(
            """
            FlashRank reranks retrieved code
            chunks and prioritizes the most
            relevant context.
            """
        )


with t3:

    with st.container(border=True):

        st.markdown(
            "### 🤖 Grounded Generation"
        )

        st.write(
            """
            Groq generates answers using
            retrieved code context instead
            of relying only on general knowledge.
            """
        )


# ============================================================
# ARCHITECTURE
# ============================================================

st.divider()

st.subheader("🔄 RAG Architecture")

st.code("""
                         CODEBASE
                            │
                            ▼
                     CODE CHUNKING
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
           EMBEDDINGS              TOKENIZATION
                │                       │
                ▼                       ▼
              FAISS                   BM25
         Vector Retrieval        Keyword Retrieval
                │                       │
                └───────────┬───────────┘
                            ▼
                    HYBRID RETRIEVAL
                            │
                            ▼
                   FLASHRANK RERANKING
                            │
                            ▼
                  RELEVANT CODE CONTEXT
                            │
                            ▼
                       GROQ LLM
                    GPT-OSS-120B
                            │
                            ▼
                       AI RESPONSE
""", language="text")


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🧠 CodeMind AI  •  "
    "Python  •  RAG  •  FAISS  •  BM25  •  "
    "FlashRank  •  Groq  •  Streamlit"
)

st.caption(
    "Intelligent retrieval for modern developers."
)