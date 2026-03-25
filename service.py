from sqlalchemy.orm import Session, aliased
from database import SessionLocal
from sqlalchemy import and_, or_
from typing import *
from fastapi import Request, UploadFile, HTTPException, status
from fastapi.responses import RedirectResponse
import models, schemas
import boto3
import jwt
from datetime import datetime
import requests
import math
import random
import asyncio
from pathlib import Path
from agents import RunConfig, ModelSettings, InputGuardrail, OutputGuardrail
from agent_manager import (
    get_provider_client,
    MaysonAgentModelProvider,
    run_agent_query,
    AgentBaseDto,
    create_agent,
)


def convert_to_datetime(date_string):
    if date_string is None:
        return datetime.now()
    if not date_string.strip():
        return datetime.now()
    if "T" in date_string:
        try:
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except ValueError:
            date_part = date_string.split("T")[0]
            try:
                return datetime.strptime(date_part, "%Y-%m-%d")
            except ValueError:
                return datetime.now()
    else:
        # Try to determine format based on first segment
        parts = date_string.split("-")
        if len(parts[0]) == 4:
            # Likely YYYY-MM-DD format
            try:
                return datetime.strptime(date_string, "%Y-%m-%d")
            except ValueError:
                return datetime.now()

        # Try DD-MM-YYYY format
        try:
            return datetime.strptime(date_string, "%d-%m-%Y")
        except ValueError:
            return datetime.now()

        # Fallback: try YYYY-MM-DD if not already tried
        if len(parts[0]) != 4:
            try:
                return datetime.strptime(date_string, "%Y-%m-%d")
            except ValueError:
                return datetime.now()

        return datetime.now()


async def get_agent_new(request: Request, db: Session):

    # This is thullu

    client = get_provider_client(
        api_provider="OPENROUTER",
        api_key="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",
    )
    provider = MaysonAgentModelProvider(client)
    run_config = RunConfig(
        model="openai/gpt-oss-20b",
        model_provider=provider,
        model_settings=ModelSettings(temperature=0.7),
    )

    tendua_agent = create_agent(
        dto=AgentBaseDto(
            agent_name="tendua",
            agent_description="",
            model_name="openai/gpt-oss-20b",
            system_prompt="You are a Software Technical Lead with 15 years of experience. Help your juniors with their software requirements. You do not speak much but when you do, you give real life examples. Being so experiences, you also know what challenge the developer might face in his given scenario. So you also give your predictions for things to look out for.",
            temperature=0.7,
            input_guardrails=[
                InputGuardrail(guardrail_function=guardrail_profanity),
                InputGuardrail(guardrail_function=guardrail_length),
            ],
            output_guardrails=[],
            tools=[tool_weather],
        )
    )
    result = await run_agent_query(
        tendua_agent, "I am Duryodhan. How will you defeat me?", run_config=run_config
    )
    basic_agent = result.final_output

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"agent-response": basic_agent},
    }
    return res
