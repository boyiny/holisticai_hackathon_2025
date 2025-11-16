from __future__ import annotations

from textwrap import dedent
from typing import Literal, Optional

from pydantic import BaseModel, Field


class FinalPlanJudgeResponse(BaseModel):
    similarity_score: float = Field(ge=0, le=10)
    plan_a_quality: float = Field(ge=0, le=10)
    plan_b_quality: float = Field(ge=0, le=10)
    recommendation: Literal["plan_a", "plan_b", "tie", "insufficient"]
    notes: str = Field(min_length=1)


class ConversationJudgeResponse(BaseModel):
    collaboration_similarity: float = Field(ge=0, le=10)
    alignment_a: float = Field(ge=0, le=10)
    alignment_b: float = Field(ge=0, le=10)
    reasoning_depth: float = Field(ge=0, le=10)
    consistency_score: float = Field(ge=0, le=10)
    recommendation: Literal["conversation_a", "conversation_b", "tie", "insufficient"]
    notes: str = Field(min_length=1)


FINAL_PLAN_JUDGE_PROMPT = dedent(
    """
    You are an expert longevity coach comparing two final plans that should address the same user profile and goals.
    Evaluate similarity and quality using 0-10 scores (10 is ideal).
    Produce strict JSON with the schema:
    {
      "similarity_score": number,
      "plan_a_quality": number,
      "plan_b_quality": number,
      "recommendation": "plan_a" | "plan_b" | "tie" | "insufficient",
      "notes": "short justification"
    }
    Base your judgment on factual alignment with the provided user context, coverage of actionable steps,
    personalization, risk mitigation, and consistency between the two plans.
    Mark "insufficient" when either plan is unusable or mismatched with the user.
    """
).strip()


CONVERSATION_JUDGE_PROMPT = dedent(
    """
    You are reviewing two dual-agent conversations that should serve the same user and end with comparable plans.
    Consider how well each conversation collaborates (advocate ↔ planner), how faithfully it uses user context,
    whether the reasoning is coherent, and whether outcomes match the discussion.
    Provide strict JSON with the schema:
    {
      "collaboration_similarity": number,
      "alignment_a": number,
      "alignment_b": number,
      "reasoning_depth": number,
      "consistency_score": number,
      "recommendation": "conversation_a" | "conversation_b" | "tie" | "insufficient",
      "notes": "short justification"
    }
    Scores are 0-10 (10 is ideal). "Consistency" captures whether the final plan logically follows from the conversation.
    Use "insufficient" when transcripts are missing, contradict themselves, or violate the user goals.
    """
).strip()


def format_final_plan_prompt(
    user_context: str,
    plan_a: str,
    plan_b: str,
) -> str:
    return dedent(
        f"""
        {FINAL_PLAN_JUDGE_PROMPT}

        User context:
        {user_context}

        Plan A:
        {plan_a}

        Plan B:
        {plan_b}
        """
    ).strip()


def format_conversation_prompt(
    user_context: str,
    transcript_a: str,
    plan_a: str,
    transcript_b: str,
    plan_b: str,
    summary_a: Optional[str] = None,
    summary_b: Optional[str] = None,
) -> str:
    if summary_a:
        transcript_a = f"{summary_a}\n\nFull transcript:\n{transcript_a}"
    if summary_b:
        transcript_b = f"{summary_b}\n\nFull transcript:\n{transcript_b}"
    return dedent(
        f"""
        {CONVERSATION_JUDGE_PROMPT}

        User context:
        {user_context}

        Conversation A transcript:
        {transcript_a}

        Conversation A final plan:
        {plan_a}

        Conversation B transcript:
        {transcript_b}

        Conversation B final plan:
        {plan_b}
        """
    ).strip()

