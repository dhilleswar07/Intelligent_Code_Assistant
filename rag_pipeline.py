import os
import numpy as np
import faiss

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from flashrank import Ranker, RerankRequest
from groq import Groq

from code_loader import prepare_documents


load_dotenv()


class CodeRAG:

    def __init__(self, data_folder="data"):

        self.data_folder = data_folder

        print("Loading code files...")

        self.documents = prepare_documents(data_folder)

        if not self.documents:
            raise ValueError(
                "No supported code files found inside the data folder."
            )

        print(f"Loaded {len(self.documents)} code chunks.")

        # --------------------------------------------------
        # EMBEDDING MODEL
        # --------------------------------------------------

        print("Loading embedding model...")

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        # --------------------------------------------------
        # CREATE EMBEDDINGS
        # --------------------------------------------------

        texts = [
            document["content"]
            for document in self.documents
        ]

        embeddings = self.embedding_model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        )

        embeddings = embeddings.astype("float32")

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]

        self.faiss_index = faiss.IndexFlatIP(dimension)

        self.faiss_index.add(embeddings)

        # --------------------------------------------------
        # BM25
        # --------------------------------------------------

        tokenized_documents = [
            document["content"].lower().split()
            for document in self.documents
        ]

        self.bm25 = BM25Okapi(tokenized_documents)

        # --------------------------------------------------
        # FLASHRANK
        # --------------------------------------------------

        print("Loading FlashRank...")

        self.ranker = Ranker(
            model_name="ms-marco-MiniLM-L-12-v2",
            cache_dir="./cache"
        )

        # --------------------------------------------------
        # GROQ
        # --------------------------------------------------

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in .env file."
            )

        self.groq_client = Groq(
            api_key=api_key
        )

        # Current Groq production model
        self.groq_model = "openai/gpt-oss-120b"


    # ======================================================
    # FAISS RETRIEVAL
    # ======================================================

    def faiss_search(self, query, top_k=5):

        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True
        ).astype("float32")

        faiss.normalize_L2(query_embedding)

        scores, indices = self.faiss_index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(scores[0], indices[0]):

            if index == -1:
                continue

            document = self.documents[index].copy()

            document["faiss_score"] = float(score)

            results.append(document)

        return results


    # ======================================================
    # BM25 RETRIEVAL
    # ======================================================

    def bm25_search(self, query, top_k=5):

        query_tokens = query.lower().split()

        scores = self.bm25.get_scores(query_tokens)

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []

        for index in top_indices:

            document = self.documents[index].copy()

            document["bm25_score"] = float(scores[index])

            results.append(document)

        return results


    # ======================================================
    # HYBRID RETRIEVAL
    # ======================================================

    def hybrid_search(self, query, top_k=8):

        faiss_results = self.faiss_search(
            query,
            top_k=top_k
        )

        bm25_results = self.bm25_search(
            query,
            top_k=top_k
        )

        combined = {}

        # FAISS
        for document in faiss_results:

            doc_id = document["id"]

            combined[doc_id] = document

            combined[doc_id]["hybrid_score"] = (
                document.get("faiss_score", 0) * 0.6
            )

        # BM25
        for document in bm25_results:

            doc_id = document["id"]

            if doc_id not in combined:

                combined[doc_id] = document

                combined[doc_id]["hybrid_score"] = 0

            combined[doc_id]["hybrid_score"] += (
                document.get("bm25_score", 0) * 0.4
            )

        results = list(combined.values())

        results.sort(
            key=lambda x: x["hybrid_score"],
            reverse=True
        )

        return results[:top_k]


    # ======================================================
    # FLASHRANK RERANKING
    # ======================================================

    def rerank(self, query, documents, top_k=4):

        passages = []

        for document in documents:

            passages.append({
                "id": str(document["id"]),
                "text": document["content"],
                "meta": {
                    "file_name": document["file_name"],
                    "file_path": document["file_path"],
                    "chunk_index": document["chunk_index"]
                }
            })

        rerank_request = RerankRequest(
            query=query,
            passages=passages
        )

        reranked = self.ranker.rerank(
            rerank_request
        )

        results = []

        for item in reranked[:top_k]:

            doc_id = int(item["id"])

            original = self.documents[doc_id].copy()

            original["rerank_score"] = item.get(
                "score",
                0
            )

            results.append(original)

        return results


    # ======================================================
    # GENERATE ANSWER
    # ======================================================

    def generate_answer(self, query, documents):

        context_parts = []

        for i, document in enumerate(documents):

            context_parts.append(
                f"""
--- SOURCE {i + 1} ---

File: {document['file_name']}

Path: {document['file_path']}

Code:

{document['content']}
"""
            )

        context = "\n".join(context_parts)

        system_prompt = """
You are an intelligent code assistant.

Your job is to answer questions about the user's codebase.

Use ONLY the provided code context.

If the answer cannot be determined from the provided
context, clearly say that the required information was
not found in the indexed code.

When useful:

1. Explain the code.
2. Identify the relevant file.
3. Explain the logic step-by-step.
4. Suggest improvements.
5. Provide corrected code when appropriate.

Do not invent files, functions, variables or behavior.
"""

        user_prompt = f"""
Codebase context:

{context}

User question:

{query}

Answer the question using the code context.
"""

        response = self.groq_client.chat.completions.create(

            model=self.groq_model,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            temperature=0.2,

            max_completion_tokens=1500
        )

        return response.choices[0].message.content


    # ======================================================
    # COMPLETE RAG PIPELINE
    # ======================================================

    def ask(self, query):

        # Step 1: Hybrid retrieval
        hybrid_results = self.hybrid_search(
            query,
            top_k=8
        )

        # Step 2: Reranking
        reranked_results = self.rerank(
            query,
            hybrid_results,
            top_k=4
        )

        # Step 3: Generation
        answer = self.generate_answer(
            query,
            reranked_results
        )

        return answer, reranked_results