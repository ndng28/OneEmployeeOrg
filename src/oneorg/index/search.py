import re
from pydantic import BaseModel
from typing import Optional
from oneorg.models.agent import QuestMaster, SkillDomain

class SearchQuery(BaseModel):
    keywords: Optional[list[str]] = None
    skill_domain: Optional[SkillDomain] = None
    category: Optional[str] = None
    vibe_contains: Optional[str] = None

class QuestIndex:
    def __init__(self, quest_masters: list[QuestMaster]):
        self.quest_masters = quest_masters
        self._keyword_index = self._build_keyword_index()
    
    def _build_keyword_index(self) -> dict[str, list[int]]:
        index = {}
        for i, master in enumerate(self.quest_masters):
            for keyword in master.keywords:
                keyword_lower = keyword.lower()
                if keyword_lower not in index:
                    index[keyword_lower] = []
                index[keyword_lower].append(i)
        return index
    
    def search(self, query: SearchQuery) -> list[QuestMaster]:
        results = []
        
        for master in self.quest_masters:
            if query.skill_domain and master.skill_domain != query.skill_domain:
                continue
            if query.category and master.category != query.category:
                continue
            if query.vibe_contains and query.vibe_contains.lower() not in (master.vibe or "").lower():
                continue
            if query.keywords:
                if not self._matches_keywords(master, query.keywords):
                    continue
            results.append(master)
        
        return results
    
    def _matches_keywords(self, master: QuestMaster, keywords: list[str]) -> bool:
        master_keywords = set(k.lower() for k in master.keywords)
        query_keywords = set(k.lower() for k in keywords)
        return bool(master_keywords & query_keywords)
    
    def search_fuzzy(self, text: str) -> list[tuple[QuestMaster, float]]:
        text_lower = text.lower()
        words = re.findall(r"\w+", text_lower)
        
        scored = []
        for master in self.quest_masters:
            score = self._fuzzy_score(master, words)
            if score > 0:
                scored.append((master, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [m for m, s in scored]
    
    def _fuzzy_score(self, master: QuestMaster, words: list[str]) -> float:
        score = 0.0
        
        searchable = " ".join([
            master.name,
            master.description,
            master.vibe or "",
            " ".join(master.keywords),
        ]).lower()
        
        for word in words:
            if word in searchable:
                score += 1.0
            if word in master.keywords:
                score += 2.0
        
        return score
    
    def get_by_slug(self, slug: str) -> Optional[QuestMaster]:
        for master in self.quest_masters:
            if master.slug == slug:
                return master
        return None
    
    @classmethod
    def from_dict(cls, data: list[dict]) -> "QuestIndex":
        masters = [QuestMaster.model_validate(m) for m in data]
        return cls(quest_masters=masters)
