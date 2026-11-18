"""Граф знань: теми та залежності між ними."""
import json
from pathlib import Path


class KnowledgeGraph:
    def __init__(self, topics: dict):
        # topics: {id: {"title": str, "prerequisites": [id, ...]}}
        self.topics = topics

    @classmethod
    def from_json(cls, path):
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def prerequisites(self, topic_id):
        return self.topics[topic_id].get("prerequisites", [])

    def title(self, topic_id):
        return self.topics[topic_id]["title"]
