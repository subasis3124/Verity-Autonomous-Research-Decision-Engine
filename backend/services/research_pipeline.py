"""
Research Pipeline — The core 4-step AI workflow.

Step 1: DECOMPOSE — Break query into sub-questions
Step 2: RESEARCH — Answer each sub-question in depth
Step 3: SYNTHESIZE — Generate structured final report
Step 4: UPDATE STATUS — Mark query as completed or failed
"""

import json
import re
import logging
import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

logger = logging.getLogger(__name__)

# Create a synchronous engine for background tasks
# (BackgroundTasks in FastAPI run in a threadpool, so sync is fine)
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# psycopg2 handles sslmode=require in the URL natively
sync_engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=3,
    max_overflow=5,
)
SyncSession = sessionmaker(bind=sync_engine)


def get_sync_db():
    """Get a synchronous database session for background tasks."""
    session = SyncSession()
    try:
        return session
    except Exception:
        session.close()
        raise


def run_research_pipeline(query_id: str):
    """
    Main background task — runs the full research pipeline for a query.
    This function is called by FastAPI BackgroundTasks and runs synchronously
    in a thread pool.
    """
    from models import Query, SubQuestion, ResearchStep, FinalReport, QueryStatus
    from services.groq_service import call_groq

    db = get_sync_db()

    try:
        # Fetch the query
        query = db.execute(select(Query).where(Query.id == query_id)).scalar_one_or_none()
        if not query:
            logger.error(f"Query {query_id} not found")
            return

        # Update status to processing
        query.status = QueryStatus.PROCESSING
        db.commit()

        logger.info(f"[Pipeline] Starting research for query: {query_id}")

        # ─────────────────────────────────────────────
        # Step 1: DECOMPOSE — Break into sub-questions
        # ─────────────────────────────────────────────
        logger.info("[Pipeline] Step 1: Decomposing query into sub-questions...")

        decompose_prompt = f"""Break the following research query into 3 to 5 focused, specific sub-questions that would help thoroughly investigate the topic. 

Return ONLY a JSON array of strings, with no additional text or explanation.

Example format: ["question 1", "question 2", "question 3"]

Research Query: {query.raw_query}"""

        decompose_response = call_groq(
            prompt=decompose_prompt,
            system="You are a research planning specialist. You break complex questions into focused sub-questions. Always respond with valid JSON only.",
            temperature=0.3,
        )

        # Parse sub-questions from the LLM response
        sub_questions_list = _parse_json_array(decompose_response)

        if not sub_questions_list or len(sub_questions_list) == 0:
            raise ValueError(f"Failed to parse sub-questions from LLM response: {decompose_response[:200]}")

        # Save sub-questions to database
        sub_question_objects = []
        for idx, question_text in enumerate(sub_questions_list):
            sq = SubQuestion(
                query_id=query_id,
                question_text=question_text.strip(),
                order_index=idx + 1,
            )
            db.add(sq)
            sub_question_objects.append(sq)

        db.flush()
        # Refresh to get IDs
        for sq in sub_question_objects:
            db.refresh(sq)

        logger.info(f"[Pipeline] Generated {len(sub_question_objects)} sub-questions")

        # ─────────────────────────────────────────────
        # Step 2: RESEARCH — Answer each sub-question
        # ─────────────────────────────────────────────
        logger.info("[Pipeline] Step 2: Researching each sub-question...")

        research_results = []

        for step_num, sq in enumerate(sub_question_objects, 1):
            research_prompt = f"""Analyze and answer the following research question in detail. 
Provide thorough reasoning, consider multiple perspectives, and include specific data points or examples where relevant.

Research Question: {sq.question_text}

Context: This is part of a larger investigation into: "{query.raw_query}"
"""

            research_response = call_groq(
                prompt=research_prompt,
                system="You are a senior research analyst with deep expertise across multiple domains. Provide detailed, well-reasoned analysis with specific examples and data points.",
                temperature=0.5,
                max_tokens=4096,
            )

            # Save research step
            step = ResearchStep(
                query_id=query_id,
                sub_question_id=str(sq.id),
                llm_prompt=research_prompt,
                llm_response=research_response,
                step_number=step_num,
            )
            db.add(step)
            db.flush()

            research_results.append({
                "question": sq.question_text,
                "answer": research_response,
            })

            logger.info(f"[Pipeline] Completed research step {step_num}/{len(sub_question_objects)}")

        # ─────────────────────────────────────────────
        # Step 3: SYNTHESIZE — Generate final report
        # ─────────────────────────────────────────────
        logger.info("[Pipeline] Step 3: Synthesizing final report...")

        findings_text = "\n\n".join([
            f"### Sub-Question {i+1}: {r['question']}\n{r['answer']}"
            for i, r in enumerate(research_results)
        ])

        synthesis_prompt = f"""Based on the following research findings, create a comprehensive structured report.

Original Research Query: {query.raw_query}

Research Findings:
{findings_text}

Create a structured report with the following sections. Return the report as a JSON object with these exact keys:
- "executive_summary": A concise overview of all findings (2-3 paragraphs)
- "key_findings": An array of the most important discoveries (each as a string)
- "risks": An array of identified risks or concerns (each as a string) 
- "recommendations": An array of actionable recommendations (each as a string)

Return ONLY the JSON object, no additional text."""

        synthesis_response = call_groq(
            prompt=synthesis_prompt,
            system="You are a senior analyst who creates executive-level research reports. Always respond with valid JSON only.",
            temperature=0.4,
            max_tokens=4096,
        )

        # Parse structured output
        structured_output = _parse_json_object(synthesis_response)

        if not structured_output:
            # Fallback: create structured output from raw response
            structured_output = {
                "executive_summary": synthesis_response,
                "key_findings": [],
                "risks": [],
                "recommendations": [],
            }

        # Generate a plain-text summary from the executive summary
        summary = structured_output.get("executive_summary", "Report generated successfully.")
        if isinstance(summary, list):
            summary = " ".join(summary)

        # Save final report
        report = FinalReport(
            query_id=query_id,
            summary=summary,
            structured_output=structured_output,
        )
        db.add(report)

        # ─────────────────────────────────────────────
        # Step 4: UPDATE STATUS — Mark as completed
        # ─────────────────────────────────────────────
        query.status = QueryStatus.COMPLETED
        db.commit()

        logger.info(f"[Pipeline] ✅ Research pipeline completed for query: {query_id}")

    except Exception as e:
        logger.error(f"[Pipeline] ❌ Pipeline failed for query {query_id}: {e}")
        db.rollback()

        try:
            query = db.execute(select(Query).where(Query.id == query_id)).scalar_one_or_none()
            if query:
                query.status = QueryStatus.FAILED
                query.error_message = str(e)[:500]
                db.commit()
        except Exception as inner_e:
            logger.error(f"[Pipeline] Failed to update status: {inner_e}")
            db.rollback()

    finally:
        db.close()


def _parse_json_array(text: str) -> list[str]:
    """
    Parse a JSON array from LLM output, handling markdown code blocks
    and other formatting artifacts.
    """
    # Try to extract JSON from markdown code blocks
    code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if code_block_match:
        text = code_block_match.group(1).strip()

    # Try to find a JSON array in the text
    bracket_match = re.search(r'\[[\s\S]*\]', text)
    if bracket_match:
        try:
            result = json.loads(bracket_match.group(0))
            if isinstance(result, list):
                return [str(item) for item in result]
        except json.JSONDecodeError:
            pass

    # Fallback: try to parse the whole text as JSON
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return [str(item) for item in result]
    except json.JSONDecodeError:
        pass

    # Last resort: split by newlines and clean up
    lines = [
        line.strip().strip("-").strip("•").strip("*").strip('"').strip()
        for line in text.split("\n")
        if line.strip() and not line.strip().startswith("{") and not line.strip().startswith("}")
    ]
    return [line for line in lines if len(line) > 10]


def _parse_json_object(text: str) -> dict | None:
    """
    Parse a JSON object from LLM output, handling markdown code blocks
    and other formatting artifacts.
    """
    # Try to extract JSON from markdown code blocks
    code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if code_block_match:
        text = code_block_match.group(1).strip()

    # Try to find a JSON object in the text
    brace_match = re.search(r'\{[\s\S]*\}', text)
    if brace_match:
        try:
            result = json.loads(brace_match.group(0))
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    # Fallback: try to parse the whole text
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    return None
