"""Small in-memory inverted index for fast project search; O(tokens + matches)."""
from collections import defaultdict
import re
from threading import RLock

TOKEN_RE = re.compile(r"[a-z0-9+#.]+", re.IGNORECASE)


class ProjectSearchIndex:
    """Build once per dataset, then query an inverted index instead of scanning all text."""

    def __init__(self, projects=()):
        self._lock = RLock()
        self._documents = {}
        self._inverted = defaultdict(set)
        self.rebuild(projects)

    @staticmethod
    def tokens(text):
        return {token.casefold() for token in TOKEN_RE.findall(text or "")}

    def rebuild(self, projects):
        with self._lock:
            self._documents.clear()
            self._inverted.clear()
            for project in projects:
                document_id = str(project.get("id", project.get("slug", len(self._documents))))
                searchable = " ".join(str(project.get(key, "")) for key in ("title", "short_description", "description", "category", "tech_stack"))
                self._documents[document_id] = project
                for token in self.tokens(searchable):
                    self._inverted[token].add(document_id)

    def search(self, query, limit=20):
        terms = self.tokens(query)
        if not terms:
            return []
        with self._lock:
            matches = set().union(*(self._inverted.get(term, set()) for term in terms))
            scored = []
            for document_id in matches:
                item = self._documents[document_id]
                title_terms = self.tokens(item.get("title", ""))
                score = sum(3 if term in title_terms else 1 for term in terms if document_id in self._inverted.get(term, ()))
                scored.append((score, str(item.get("title", "")).casefold(), item))
            scored.sort(key=lambda row: (-row[0], row[1]))
            return [row[2] for row in scored[:max(1, min(int(limit), 100))]]
