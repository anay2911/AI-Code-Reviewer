from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field

class BugDetail(BaseModel):
    line_number: int = Field(description="The exact line number where the issue occurs.")
    category: str = Field(description="Security, Performance, Syntax, or Code-Smell.")
    issue: str = Field(description="Clear explanation of the problem found.")
    fix: str = Field(description="Proposed optimal code fix snippet.")

class ReviewReport(BaseModel):
    is_clean: bool = Field(description="Set to True only if absolutely NO critical bugs remain.")
    bugs: List[BugDetail] = Field(default=[], description="List of all bugs found.")

class ReviewState(TypedDict):
    original_code: str
    current_code: str
    critic_report: Optional[ReviewReport]
    iteration_count: int