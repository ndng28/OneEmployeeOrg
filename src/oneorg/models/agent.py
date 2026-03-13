from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import re

class SkillDomain(str, Enum):
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    CREATIVE = "creative"
    SCIENCE = "science"
    LIFE_SKILLS = "life_skills"

CATEGORY_TO_DOMAIN = {
    "engineering": SkillDomain.TECHNOLOGY,
    "design": SkillDomain.CREATIVE,
    "marketing": SkillDomain.CREATIVE,
    "paid-media": SkillDomain.BUSINESS,
    "sales": SkillDomain.BUSINESS,
    "product": SkillDomain.BUSINESS,
    "project-management": SkillDomain.BUSINESS,
    "testing": SkillDomain.TECHNOLOGY,
    "support": SkillDomain.TECHNOLOGY,
    "spatial-computing": SkillDomain.TECHNOLOGY,
    "specialized": SkillDomain.LIFE_SKILLS,
    "strategy": SkillDomain.BUSINESS,
    "game-development": SkillDomain.TECHNOLOGY,
}

COLOR_MAP = {
    "red": "#FF0000", "green": "#00FF00", "blue": "#0000FF",
    "cyan": "#00FFFF", "magenta": "#FF00FF", "yellow": "#FFFF00",
    "orange": "#FFA500", "purple": "#800080", "teal": "#008080",
    "pink": "#FFC0CB", "white": "#FFFFFF", "black": "#000000",
}

class QuestMaster(BaseModel):
    slug: str = Field(..., description="URL-safe identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="One-line description")
    category: str = Field(..., description="Source category (engineering, design, etc.)")
    skill_domain: SkillDomain = Field(..., description="Educational domain")
    color: str = Field(..., description="Hex color code")
    emoji: Optional[str] = Field(None, description="Icon emoji")
    vibe: Optional[str] = Field(None, description="Personality hook")
    keywords: list[str] = Field(default_factory=list, description="Searchable keywords")
    file_path: str = Field(..., description="Path to agent definition")
    tools: list[str] = Field(default_factory=list)
    
    @classmethod
    def from_frontmatter(
        cls,
        frontmatter: dict,
        category: str,
        file_path: str,
    ) -> "QuestMaster":
        name = frontmatter.get("name", "Unknown")
        slug = cls._generate_slug(name)
        color = cls._normalize_color(frontmatter.get("color", "blue"))
        keywords = cls._extract_keywords(frontmatter)
        
        return cls(
            slug=slug,
            name=name,
            description=frontmatter.get("description", ""),
            category=category,
            skill_domain=CATEGORY_TO_DOMAIN.get(category, SkillDomain.LIFE_SKILLS),
            color=color,
            emoji=frontmatter.get("emoji"),
            vibe=frontmatter.get("vibe"),
            keywords=keywords,
            file_path=file_path,
            tools=frontmatter.get("tools", "").split(", ") if frontmatter.get("tools") else [],
        )
    
    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug
    
    @staticmethod
    def _normalize_color(color: str) -> str:
        if color.startswith("#"):
            return color.upper()
        return COLOR_MAP.get(color.lower(), "#0000FF")
    
    @staticmethod
    def _extract_keywords(frontmatter: dict) -> list[str]:
        keywords = []
        for field in ["description", "vibe", "name"]:
            text = frontmatter.get(field, "")
            words = re.findall(r"\b[A-Z][a-z]+\b|\b[A-Z]{2,}\b", text)
            keywords.extend(w.lower() for w in words)
        
        keywords.extend(frontmatter.get("name", "").lower().split())
        return list(set(keywords))[:10]
