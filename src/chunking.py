from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        
        sentences = [s.strip() for s in re.split(r'(?<=\.) |(?<=\!) |(?<=\?) |(?<=\.)\n', text) if s.strip()]
        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i:i + self.max_sentences_per_chunk])
            chunks.append(chunk)

        if not chunks and text:
            return [text.strip()]
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]

        if not remaining_separators:
            return [current_text[i:i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        sep = remaining_separators[0]
        next_separators = remaining_separators[1:]

        if sep == "":
            return self._split(current_text, next_separators)

        splits = current_text.split(sep)
        final_chunks = []
        current_chunk = ""

        for part in splits:
            to_add = part if not current_chunk else current_chunk + sep + part

            if len(to_add) <= self.chunk_size:
                current_chunk = to_add
            else:
                if current_chunk:
                    final_chunks.append(current_chunk)
                if len(part) > self.chunk_size:
                    final_chunks.extend(self._split(part, next_separators))
                    current_chunk = ""
                else:
                    current_chunk = part
                    
        if current_chunk:
            final_chunks.append(current_chunk)
            
        return final_chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    dot_prod = _dot(vec_a, vec_b)
    mag_a = math.sqrt(sum(x*x for x in vec_a))
    mag_b = math.sqrt(sum(y*y for y in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot_prod / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed = FixedSizeChunker(chunk_size=chunk_size).chunk(text)
        sentence = SentenceChunker().chunk(text)
        recursive = RecursiveChunker(chunk_size=chunk_size).chunk(text)

        def get_data(chunks):
            return {
                "count": len(chunks),
                "avg_length": sum(len(c) for c in chunks) / len(chunks) if chunks else 0,
                "chunks": chunks
            }

        return {
            "fixed_size": get_data(fixed),
            "by_sentences": get_data(sentence),
            "recursive": get_data(recursive),
        }


class CustomChunker:
    """
    Custom chunking strategy designed for FAQ and policy documents (like khachhang.txt, nhahang.txt).
    Chunks text by numbered headers (e.g., 1., 1.1., 2.1.3.).
    
    Design rationale:
    These documents are structured as a series of questions or policy points, each starting 
    with a hierarchical number. Splitting by these headers ensures each chunk contains 
    exactly one logical topic or Q&A pair.
    """

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
            
        # Pattern to match numbered headers at the start of a line: e.g., "1. ", "1.1. ", "2.1.3. "
        header_pattern = re.compile(r'^(\d+(\.\d+)*\.\s?.*)', re.MULTILINE)
        
        # Find all matches
        matches = list(header_pattern.finditer(text))
        
        if not matches:
            # Fallback to single chunk if no headers found
            return [text.strip()]
            
        chunks = []
        
        # 1. Add any text BEFORE the first header (preamble)
        preamble = text[:matches[0].start()].strip()
        if preamble:
            chunks.append(preamble)
            
        # 2. Extract chunks between headers
        for i in range(len(matches)):
            start = matches[i].start()
            # The next chunk starts where the next header is found, 
            # or at the end of the full text if it's the last header.
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append(chunk_content)
                
        return chunks
