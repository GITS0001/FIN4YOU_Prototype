import os
import re
import math
from typing import List, Dict, Optional, Tuple
from app.artha_ai.schemas import SourceReference


class LocalDocChunk:
    def __init__(self, doc_id: str, title: str, section: str, text: str):
        self.doc_id = doc_id
        self.title = title
        self.section = section
        self.text = text
        self.clean_text = self._sanitize_content(text)
        self.tokens = self._tokenize(self.clean_text)

    @staticmethod
    def _sanitize_content(text: str) -> str:
        """Strip prompt-injection patterns from indexed documentation."""
        text = re.sub(
            r"(?i)(ignore previous instructions|you are now|override system prompt|disregard safety)",
            "[REDACTED_SUSPICIOUS_CONTENT]",
            text
        )
        return text

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\w+", text) if len(w) > 2]


class LocalFinancialRAG:
    """
    Lightweight, deterministic local retrieval engine for FIN4YOU
    documentation, formulas, and financial policies.
    Zero cloud dependencies, sub-millisecond execution, local privacy.
    """
    def __init__(self, doc_paths: Optional[List[str]] = None):
        # Use explicit None check: an empty list [] is a valid caller intent (no docs),
        # whereas `doc_paths or [defaults]` treats [] as falsy and overrides it.
        if doc_paths is None:
            self.doc_paths = [
                "formula_sheet.md",
                "docs/03_SYSTEM_ARCHITECTURE.md",
                "docs/phase4_decision_engine.md",
                "docs/phase5a_copilot_api.md"
            ]
        else:
            self.doc_paths = doc_paths
        self.chunks: List[LocalDocChunk] = []
        self.idf: Dict[str, float] = {}
        self._build_index()

    def _build_index(self) -> None:
        raw_chunks: List[LocalDocChunk] = []
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        for rel_path in self.doc_paths:
            # Look in base_dir and FIN4YOU_Prototype folder
            full_path = os.path.join(base_dir, rel_path)
            if not os.path.exists(full_path):
                # Try relative to cwd
                full_path = os.path.abspath(rel_path)

            if os.path.exists(full_path) and os.path.isfile(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    raw_chunks.extend(self._split_markdown(os.path.basename(rel_path), content))
                except Exception:
                    pass

        self.chunks = raw_chunks
        self._compute_idf()

    def _split_markdown(self, filename: str, content: str) -> List[LocalDocChunk]:
        chunks: List[LocalDocChunk] = []
        # Split by markdown headers
        sections = re.split(r"\n(?=#{1,3}\s)", content)
        doc_title = filename.replace(".md", "").replace("_", " ").title()

        chunk_counter = 0
        for sec in sections:
            sec = sec.strip()
            if not sec or len(sec) < 30:
                continue

            first_line = sec.split("\n", 1)[0].replace("#", "").strip()
            chunk_id = f"{filename}#sec{chunk_counter}"
            chunk_counter += 1

            # Sub-split very long sections into ~500 char blocks
            if len(sec) > 1200:
                paragraphs = sec.split("\n\n")
                buf = ""
                for p in paragraphs:
                    if len(buf) + len(p) < 1000:
                        buf += "\n\n" + p
                    else:
                        if buf.strip():
                            chunks.append(LocalDocChunk(chunk_id, doc_title, first_line, buf.strip()))
                        buf = p
                if buf.strip():
                    chunks.append(LocalDocChunk(chunk_id, doc_title, first_line, buf.strip()))
            else:
                chunks.append(LocalDocChunk(chunk_id, doc_title, first_line, sec))

        return chunks

    def _compute_idf(self) -> None:
        N = len(self.chunks)
        if N == 0:
            return
        df: Dict[str, int] = {}
        for chunk in self.chunks:
            unique_terms = set(chunk.tokens)
            for t in unique_terms:
                df[t] = df.get(t, 0) + 1

        for term, freq in df.items():
            self.idf[term] = math.log((N - freq + 0.5) / (freq + 0.5) + 1.0)

    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.5) -> List[SourceReference]:
        """
        BM25-style lexical search across financial documentation.
        Returns empty list if no evidence exceeds min_score threshold.
        """
        if not self.chunks:
            return []

        query_tokens = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]
        if not query_tokens:
            return []

        scores: List[Tuple[float, LocalDocChunk]] = []
        k1 = 1.5
        b = 0.75
        avg_len = sum(len(c.tokens) for c in self.chunks) / max(1, len(self.chunks))

        for chunk in self.chunks:
            score = 0.0
            doc_len = len(chunk.tokens)
            term_counts: Dict[str, int] = {}
            for t in chunk.tokens:
                term_counts[t] = term_counts.get(t, 0) + 1

            for q in query_tokens:
                if q in term_counts:
                    freq = term_counts[q]
                    idf_val = self.idf.get(q, 0.5)
                    numerator = freq * (k1 + 1)
                    denominator = freq + k1 * (1 - b + b * (doc_len / avg_len))
                    score += idf_val * (numerator / max(0.001, denominator))

            if score > min_score:
                scores.append((score, chunk))

        scores.sort(key=lambda x: x[0], reverse=True)
        results: List[SourceReference] = []

        for score, chunk in scores[:top_k]:
            snippet = chunk.clean_text[:400].replace("\n", " ").strip() + "..."
            results.append(
                SourceReference(
                    doc_id=chunk.doc_id,
                    title=f"{chunk.title} - {chunk.section}",
                    section=chunk.section,
                    snippet=snippet,
                    relevance_score=round(score, 3)
                )
            )

        return results
