import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from oneorg.models.student import StudentProgress, QuestCompletion, Badge

class StateTracker:
    def __init__(self, state_dir: Path):
        self.state_dir = Path(state_dir)
        self.students_dir = self.state_dir / "students"
        self.students_dir.mkdir(parents=True, exist_ok=True)
    
    def _student_path(self, student_id: str) -> Path:
        return self.students_dir / f"{student_id}.json"
    
    def save(self, student: StudentProgress) -> None:
        student.updated_at = datetime.now()
        path = self._student_path(student.student_id)
        
        with open(path, "w") as f:
            f.write(student.model_dump_json(indent=2))
    
    def load(self, student_id: str) -> Optional[StudentProgress]:
        path = self._student_path(student_id)
        if not path.exists():
            return None
        
        with open(path) as f:
            data = json.load(f)
        
        return StudentProgress.model_validate(data)
    
    def exists(self, student_id: str) -> bool:
        return self._student_path(student_id).exists()
    
    def delete(self, student_id: str) -> bool:
        path = self._student_path(student_id)
        if path.exists():
            path.unlink()
            return True
        return False
    
    def list_all(self) -> list[str]:
        if not self.students_dir.exists():
            return []
        
        return [
            f.stem
            for f in self.students_dir.glob("*.json")
            if f.stem.startswith("stu_")
        ]
    
    def add_quest_completion(
        self,
        student_id: str,
        completion: QuestCompletion,
    ) -> Optional[StudentProgress]:
        student = self.load(student_id)
        if not student:
            return None
        
        student.add_quest_completion(completion)
        self.save(student)
        return student
    
    def award_badge(
        self,
        student_id: str,
        badge: Badge,
    ) -> Optional[StudentProgress]:
        student = self.load(student_id)
        if not student:
            return None
        
        student.award_badge(badge)
        self.save(student)
        return student
