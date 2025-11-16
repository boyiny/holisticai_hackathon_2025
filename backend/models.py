from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class AgentRole(str, Enum):
    LEO = "LEO"  # user-facing
    LUNA = "LUNA"  # backend audit/scheduling


class StepId(str, Enum):
    START = "Start"
    INTAKE = "Intake"
    PLANDRAFT = "PlanDraft"
    PLANREVIEW = "PlanReview"
    AUDIT = "Audit"
    REVISION = "Revision"
    FINALPLAN = "FinalPlan"
    SCHEDULING = "Scheduling"
    FINALSUMMARY = "FinalSummary"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class WorkflowStepState(BaseModel):
    id: StepId
    title: str
    description: str
    responsible_agent: AgentRole
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error_message: Optional[str] = None


class UserProfile(BaseModel):
    user_id: str
    age: int
    primary_goals: List[str]
    constraints: List[str]
    lifestyle_summary: str
    sleep_pattern: Optional[str] = None
    activity_pattern: Optional[str] = None
    work_pattern: Optional[str] = None


class PlanAction(BaseModel):
    description: str
    category: str
    intensity: str  # low | moderate | high
    notes: Optional[str] = None


class PlanDraft(BaseModel):
    version: int
    focus_area: str
    primary_goals: List[str]
    actions: List[PlanAction]
    rationale: str


class AuditIssue(BaseModel):
    severity: str  # low | medium | high
    message: str
    suggested_change: Optional[str] = None


class AuditReport(BaseModel):
    status: str  # approved | approved_with_warnings | changes_required
    issues: List[AuditIssue]
    evidence_notes: List[str]


class ScheduleItem(BaseModel):
    label: str
    datetime_iso: str
    type: str  # e.g., check-in, assessment


class ScheduleResult(BaseModel):
    items: List[ScheduleItem]
    notes: str


class LongevityContext(BaseModel):
    user_profile: Optional[UserProfile] = None
    plan_draft: Optional[PlanDraft] = None
    plan_review_notes: List[str] = []
    audit_report: Optional[AuditReport] = None
    revision_history: List[PlanDraft] = []
    final_plan: Optional[PlanDraft] = None
    schedule: Optional[ScheduleResult] = None
    summary: Optional[str] = None

