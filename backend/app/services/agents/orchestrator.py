"""
Task orchestrator.

Today: a lightweight explicit router (each API endpoint calls the right
agent directly — see api/v1/endpoints/). This module exists so that when
you're ready to let one endpoint accept a free-form instruction like
"Generate a proposal for AWS migration for ABC Corp", you swap this stub
for a LangGraph graph that picks tools (rag / proposal / email / meeting)
based on the instruction, without changing any endpoint code.
"""
from enum import Enum

from app.services.agents import email_agent, meeting_agent, proposal_agent
from app.services.rag.retriever import answer_question


class TaskType(str, Enum):
    QA = "qa"
    PROPOSAL = "proposal"
    EMAIL = "email"
    MEETING_SUMMARY = "meeting_summary"


async def run_task(task_type: TaskType, payload: dict) -> str:
    if task_type == TaskType.QA:
        result = await answer_question(payload["question"])
        return result.answer

    if task_type == TaskType.PROPOSAL:
        return await proposal_agent.generate_proposal(payload["client_name"], payload["requirement"])

    if task_type == TaskType.EMAIL:
        return await email_agent.draft_email(
            payload["email_type"], payload["context"], payload.get("incoming_email")
        )

    if task_type == TaskType.MEETING_SUMMARY:
        return await meeting_agent.summarize_meeting(payload["transcript"])

    raise ValueError(f"Unknown task type: {task_type}")
