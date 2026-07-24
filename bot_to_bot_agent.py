"""
Bot-to-Bot Agent System v3.7.0
Multi-agent orchestration with specialized AI agents
Implements: Sequential, Parallel, Hierarchical, Crew, Debate, Handoff, Swarm, Flow
Source: Telegram Bot API 10.0 + GitHub patterns + CrewAI + Multi-Agent Debate research
"""

import os
import json
import asyncio
import logging
import hashlib
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ============================================================
# CONSTANTS
# ============================================================
AGENTS_CONFIG_FILE = "agents_config.json"
MAX_MESSAGE_DEPTH = 10
LOOP_TIMEOUT_SECONDS = 30
DEFAULT_AGENT_TIMEOUT = 60
MAX_CONCURRENT_AGENTS = 5

# ============================================================
# ENUMS
# ============================================================
class AgentType(Enum):
    TRIAGE = "triage"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    WRITING = "writing"
    CODING = "coding"
    CYBERDECK = "cyberdeck"
    MODERATION = "moderation"
    SUPPORT = "support"
    CUSTOM = "custom"

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class OrchestrationPattern(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    ROUND_ROBIN = "round_robin"
    CREW = "crew"
    DEBATE = "debate"
    HANDOFF = "handoff"
    SWARM = "swarm"
    FLOW = "flow"

class DebateRole(Enum):
    PROPONENT = "proponent"
    OPPONENT = "opponent"
    NEUTRAL = "neutral"
    MODERATOR = "moderator"
    JUDGE = "judge"

class HandoffStrategy(Enum):
    DIRECT = "direct"          # Specialist answers directly
    WITH_CONTEXT = "context"   # Pass full context to specialist
    SUMMARIZED = "summarized"  # Summarize before handoff

class FlowNodeType(Enum):
    START = "start"
    AGENT = "agent"
    CONDITION = "condition"
    MERGE = "merge"
    END = "end"

# ============================================================
# DATA CLASSES
# ============================================================
@dataclass
class AgentConfig:
    id: str
    name: str
    agent_type: AgentType
    capabilities: List[str] = field(default_factory=list)
    prompt: str = ""
    model: str = "groq"
    enabled: bool = True
    priority: int = 0
    max_concurrent: int = 3
    timeout: int = DEFAULT_AGENT_TIMEOUT

@dataclass
class AgentMessage:
    id: str
    from_agent: str
    to_agent: str
    type: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: str = ""
    depth: int = 0

@dataclass
class TaskState:
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    current_agent: str = ""
    progress: float = 0.0
    data: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    error: str = ""

@dataclass
class AgentStatus:
    id: str
    name: str
    active_tasks: int = 0
    total_completed: int = 0
    total_failed: int = 0
    last_active: Optional[datetime] = None
    healthy: bool = True

# --- Crew Pattern ---
@dataclass
class CrewMember:
    agent_id: str
    role: str
    goal: str
    backstory: str = ""
    allow_delegation: bool = True

@dataclass
class CrewConfig:
    name: str
    members: List[CrewMember]
    process: str = "sequential"  # sequential or hierarchical
    verbose: bool = True

# --- Debate Pattern ---
@dataclass
class DebateConfig:
    topic: str
    max_rounds: int = 3
    participants: Dict[DebateRole, str] = field(default_factory=dict)
    require_judgment: bool = True

@dataclass
class DebateRound:
    round_num: int
    role: DebateRole
    agent_id: str
    argument: str
    timestamp: datetime = field(default_factory=datetime.now)

# --- Handoff Pattern ---
@dataclass
class HandoffRule:
    from_agent: str
    to_agent: str
    trigger_keywords: List[str] = field(default_factory=list)
    strategy: HandoffStrategy = HandoffStrategy.WITH_CONTEXT
    max_hops: int = 3

# --- Swarm Pattern ---
@dataclass
class SwarmAgent:
    agent_id: str
    capabilities: List[str] = field(default_factory=list)
    neighbors: List[str] = field(default_factory=list)
    load: float = 0.0

# --- Flow Pattern ---
@dataclass
class FlowNode:
    id: str
    node_type: FlowNodeType
    agent_id: str = ""
    condition: str = ""
    next_nodes: List[str] = field(default_factory=list)

@dataclass
class FlowDefinition:
    name: str
    nodes: Dict[str, FlowNode]
    start_node: str = "start"

# ============================================================
# MESSAGE BUS
# ============================================================
class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, Dict[str, Callable]] = {}
        self.message_log: List[AgentMessage] = []
        self.max_log_size = 1000

    def subscribe(self, agent_id: str, msg_type: str, handler: Callable):
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = {}
        self.subscribers[agent_id][msg_type] = handler

    def unsubscribe(self, agent_id: str, msg_type: str = None):
        if agent_id in self.subscribers:
            if msg_type:
                self.subscribers[agent_id].pop(msg_type, None)
            else:
                del self.subscribers[agent_id]

    async def publish(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        self.message_log.append(message)
        if len(self.message_log) > self.max_log_size:
            self.message_log = self.message_log[-self.max_log_size:]

        if message.depth >= MAX_MESSAGE_DEPTH:
            logger.warning(f"Message depth limit reached: {message.depth}")
            return {"error": "Maximum message depth exceeded"}

        if message.to_agent in self.subscribers:
            handler = self.subscribers[message.to_agent].get(message.type)
            if handler:
                try:
                    result = await handler(message)
                    return result
                except Exception as e:
                    logger.error(f"Handler error for {message.to_agent}: {e}")
                    return {"error": str(e)}

        return {"error": f"No handler for agent {message.to_agent}, type {message.type}"}

    def get_conversation_history(self, agent1: str, agent2: str, limit: int = 50) -> List[AgentMessage]:
        history = []
        for msg in self.message_log:
            if (msg.from_agent == agent1 and msg.to_agent == agent2) or \
               (msg.from_agent == agent2 and msg.to_agent == agent1):
                history.append(msg)
        return history[-limit:]

# ============================================================
# STATE MANAGER
# ============================================================
class StateManager:
    def __init__(self):
        self.states: Dict[str, TaskState] = {}

    def create_task(self, task_id: str, initial_data: Dict = None) -> TaskState:
        state = TaskState(task_id=task_id, data=initial_data or {})
        self.states[task_id] = state
        return state

    def get_task(self, task_id: str) -> Optional[TaskState]:
        return self.states.get(task_id)

    def update_task(self, task_id: str, **kwargs) -> bool:
        if task_id in self.states:
            state = self.states[task_id]
            for key, value in kwargs.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            state.updated_at = datetime.now()
            return True
        return False

    def add_result(self, task_id: str, agent_id: str, result: Any) -> bool:
        if task_id in self.states:
            self.states[task_id].results[agent_id] = result
            return True
        return False

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        to_delete = [tid for tid, state in self.states.items() if state.created_at < cutoff]
        for tid in to_delete:
            del self.states[tid]

# ============================================================
# BUILT-IN AGENTS
# ============================================================
class BaseAgent:
    def __init__(self, config: AgentConfig, message_bus: MessageBus, state_manager: StateManager):
        self.config = config
        self.bus = message_bus
        self.state = state_manager
        self.status = AgentStatus(id=config.id, name=config.name)
        self.bus.subscribe(config.id, "request", self.handle_request)
        self.bus.subscribe(config.id, "event", self.handle_event)

    async def handle_request(self, message: AgentMessage) -> Dict[str, Any]:
        self.status.last_active = datetime.now()
        self.status.active_tasks += 1
        try:
            result = await self.process(message.payload)
            self.status.total_completed += 1
            return result
        except Exception as e:
            self.status.total_failed += 1
            return {"error": str(e), "agent": self.config.id}
        finally:
            self.status.active_tasks -= 1

    async def handle_event(self, message: AgentMessage) -> Dict[str, Any]:
        return {"status": "received", "agent": self.config.id}

    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def can_handle(self, task: str) -> bool:
        return self.config.enabled

    def get_status(self) -> Dict[str, Any]:
        return {
            "id": self.config.id,
            "name": self.config.name,
            "type": self.config.agent_type.value,
            "enabled": self.config.enabled,
            "active_tasks": self.status.active_tasks,
            "completed": self.status.total_completed,
            "failed": self.status.total_failed,
            "healthy": self.status.healthy
        }


class TriageAgent(BaseAgent):
    ROUTING_RULES = {
        "research": ["search", "find", "lookup", "discover", "what is", "how to"],
        "analysis": ["analyze", "compare", "evaluate", "measure", "data", "statistics"],
        "writing": ["write", "create", "draft", "compose", "content", "blog"],
        "coding": ["code", "program", "function", "bug", "debug", "implement", "api"],
        "cyberdeck": ["cyberdeck", "deck", "sbc", "raspberry", "pi zero", "orange pi", "enclosure", "3d print", "soldering", "solder", "bom", "bill of materials", "screen", "display", "keyboard", "power bank", "ups hat", "pisugar", "writerdeck", "security deck", "gaming deck", "build list"],
        "moderation": ["moderate", "ban", "mute", "spam", "report", "violation"],
        "support": ["help", "support", "issue", "problem", "error", "fix"]
    }

    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        message = payload.get("message", "").lower()
        scores = {}
        for agent_type, keywords in self.ROUTING_RULES.items():
            score = sum(1 for kw in keywords if kw in message)
            if score > 0:
                scores[agent_type] = score
        if not scores:
            return {"routing": "support", "confidence": 0.5, "reason": "No specific match, defaulting to support"}
        best_match = max(scores, key=scores.get)
        confidence = min(scores[best_match] / 3.0, 1.0)
        return {"routing": best_match, "confidence": confidence, "reason": f"Matched {scores[best_match]} keywords for {best_match}"}


class ResearchAgent(BaseAgent):
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = payload.get("query", payload.get("message", ""))
        research_result = {"query": query, "summary": f"Research results for: {query}", "sources": [], "confidence": 0.7}
        try:
            from ai_providers import get_provider
            provider = get_provider("groq")
            if provider:
                prompt = f"Research and summarize: {query}\nProvide key findings in 2-3 sentences."
                response = provider.generate(prompt)
                research_result["summary"] = response
                research_result["confidence"] = 0.85
        except Exception as e:
            logger.debug(f"Research AI fallback: {e}")
        return research_result


class AnalysisAgent(BaseAgent):
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload.get("data", payload.get("message", ""))
        analysis = {"input": str(data)[:200], "analysis": "Data analyzed", "metrics": {}, "recommendations": []}
        if isinstance(data, str):
            words = data.split()
            analysis["metrics"] = {
                "word_count": len(words),
                "char_count": len(data),
                "sentence_count": data.count('.') + data.count('!') + data.count('?')
            }
        return analysis


class WritingAgent(BaseAgent):
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        topic = payload.get("topic", payload.get("message", ""))
        style = payload.get("style", "professional")
        content = {"topic": topic, "style": style, "draft": f"Content about: {topic}", "word_count": 0}
        try:
            from ai_providers import get_provider
            provider = get_provider("groq")
            if provider:
                prompt = f"Write a {style} piece about: {topic}"
                response = provider.generate(prompt)
                content["draft"] = response
                content["word_count"] = len(response.split())
        except Exception as e:
            logger.debug(f"Writing AI fallback: {e}")
        return content


class CodingAgent(BaseAgent):
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        task = payload.get("task", payload.get("message", ""))
        language = payload.get("language", "python")
        result = {"task": task, "language": language, "code": "", "explanation": ""}
        try:
            from ai_providers import get_provider
            provider = get_provider("groq")
            if provider:
                prompt = f"Write {language} code for: {task}\nProvide code and brief explanation."
                response = provider.generate(prompt)
                result["code"] = response
                result["explanation"] = "Generated by AI coding agent"
        except Exception as e:
            logger.debug(f"Coding AI fallback: {e}")
        return result


class CyberdeckAgent(BaseAgent):
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        message = payload.get("message", "").lower()
        result = {"agent": "cyberdeck", "input": message[:200]}
        try:
            from cyberdeck_agent import get_cyberdeck_agent
            agent = get_cyberdeck_agent()
            if any(kw in message for kw in ["build", "make me", "design me", "create", "generate"]):
                prompt_text = payload.get("message", "")
                build = await agent.build_from_prompt(prompt_text)
                result["build"] = build.get("build", build)
            elif any(kw in message for kw in ["bom", "bill", "parts list", "shopping"]):
                build = await agent.build_from_prompt(message)
                result["bom"] = build.get("build", {}).get("bom", {})
            elif any(kw in message for kw in ["tutorial", "how to", "assembly", "guide"]):
                build = await agent.build_from_prompt(message)
                result["tutorial"] = build.get("build", {}).get("tutorial", "")
            elif any(kw in message for kw in ["compat", "compatible", "check", "will it work"]):
                compat = await agent.check_compatibility({}, {}, {})
                result["compatibility"] = compat
            elif any(kw in message for kw in ["upgrade", "improve", "better"]):
                build = await agent.build_from_prompt(message)
                result["upgrades"] = await agent.suggest_upgrades(build.get("build", {}))
            elif any(kw in message for kw in ["idea", "suggest", "what should"]):
                result["ideas"] = await agent.generate_ideas()
            elif any(kw in message for kw in ["code", "script", "python", "arduino"]):
                code = await agent.generate_code(message)
                result["code"] = code
            else:
                build = await agent.build_from_prompt(message)
                result["build"] = build.get("build", build)
        except Exception as e:
            logger.debug(f"Cyberdeck AI fallback: {e}")
            result["error"] = str(e)
        return result


# ============================================================
# ORCHESTRATOR (Base)
# ============================================================
class Orchestrator:
    def __init__(self, message_bus: MessageBus, state_manager: StateManager):
        self.bus = message_bus
        self.state = state_manager
        self.agents: Dict[str, BaseAgent] = {}
        self.active_patterns: Dict[str, OrchestrationPattern] = {}

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.config.id] = agent
        logger.info(f"Registered agent: {agent.config.id} ({agent.config.name})")

    def unregister_agent(self, agent_id: str):
        if agent_id in self.agents:
            self.bus.unsubscribe(agent_id)
            del self.agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_id)

    def list_agents(self) -> List[Dict[str, Any]]:
        return [agent.get_status() for agent in self.agents.values()]

    async def route_request(self, message: str, user_id: int = None) -> Dict[str, Any]:
        task_id = hashlib.md5(f"{message}{time.time()}".encode()).hexdigest()[:12]
        self.state.create_task(task_id, {"message": message, "user_id": user_id})

        if "triage" in self.agents:
            triage_result = await self._send_to_agent("triage", {"message": message}, task_id)
            routing = triage_result.get("routing", "support")
        else:
            routing = "support"

        specialist_result = await self._send_to_agent(routing, {"message": message, "task_id": task_id}, task_id)
        return {"task_id": task_id, "routing": routing, "result": specialist_result, "status": "completed"}

    async def sequential_pipeline(self, message: str, agent_chain: List[str]) -> Dict[str, Any]:
        task_id = hashlib.md5(f"{message}{time.time()}".encode()).hexdigest()[:12]
        current_input = {"message": message}
        for agent_id in agent_chain:
            result = await self._send_to_agent(agent_id, current_input, task_id)
            current_input["previous_result"] = result
            current_input["message"] = result.get("output", result.get("summary", str(result)))
        return {"task_id": task_id, "pattern": "sequential", "chain": agent_chain, "final_result": current_input.get("previous_result")}

    async def parallel_execution(self, message: str, agent_ids: List[str]) -> Dict[str, Any]:
        task_id = hashlib.md5(f"{message}{time.time()}".encode()).hexdigest()[:12]
        tasks = [self._send_to_agent(aid, {"message": message}, task_id) for aid in agent_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        combined = {}
        for agent_id, result in zip(agent_ids, results):
            combined[agent_id] = {"error": str(result)} if isinstance(result, Exception) else result
        return {"task_id": task_id, "pattern": "parallel", "agents": agent_ids, "results": combined}

    async def hierarchical_execution(self, message: str, supervisor_id: str, worker_ids: List[str]) -> Dict[str, Any]:
        task_id = hashlib.md5(f"{message}{time.time()}".encode()).hexdigest()[:12]
        supervisor_result = await self._send_to_agent(supervisor_id, {"message": message, "worker_ids": worker_ids, "decompose": True}, task_id)
        worker_results = {}
        for worker_id in worker_ids:
            result = await self._send_to_agent(worker_id, {"message": message, "from_supervisor": supervisor_id}, task_id)
            worker_results[worker_id] = result
        final_result = await self._send_to_agent(supervisor_id, {"message": message, "worker_results": worker_results, "coordinate": True}, task_id)
        return {"task_id": task_id, "pattern": "hierarchical", "supervisor": supervisor_id, "workers": worker_ids, "result": final_result}

    async def _send_to_agent(self, agent_id: str, payload: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        message = AgentMessage(
            id=hashlib.md5(f"{agent_id}{time.time()}".encode()).hexdigest()[:8],
            from_agent="orchestrator",
            to_agent=agent_id,
            type="request",
            payload=payload,
            depth=0
        )
        result = await self.bus.publish(message)
        if result:
            self.state.add_result(task_id, agent_id, result)
        return result or {}


# ============================================================
# CREW ORCHESTRATOR (CrewAI pattern)
# ============================================================
class CrewOrchestrator:
    """Multi-agent crew with roles, goals, backstories, and delegation."""

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self.crews: Dict[str, CrewConfig] = {}

    def create_crew(self, config: CrewConfig) -> str:
        crew_id = hashlib.md5(f"{config.name}{time.time()}".encode()).hexdigest()[:8]
        self.crews[crew_id] = config
        logger.info(f"Crew created: {config.name} ({len(config.members)} members)")
        return crew_id

    def get_crew(self, crew_id: str) -> Optional[CrewConfig]:
        return self.crews.get(crew_id)

    def list_crews(self) -> List[Dict[str, Any]]:
        result = []
        for cid, config in self.crews.items():
            result.append({
                "id": cid,
                "name": config.name,
                "members": len(config.members),
                "process": config.process,
                "member_roles": [{"agent_id": m.agent_id, "role": m.role, "goal": m.goal} for m in config.members]
            })
        return result

    async def execute(self, crew_id: str, task: str, user_id: int = None) -> Dict[str, Any]:
        config = self.crews.get(crew_id)
        if not config:
            return {"error": f"Crew '{crew_id}' not found"}

        task_id = hashlib.md5(f"{crew_id}{task}{time.time()}".encode()).hexdigest()[:12]
        self.orchestrator.state.create_task(task_id, {"task": task, "crew": crew_id, "user_id": user_id})

        if config.process == "hierarchical":
            return await self._execute_hierarchical(config, task, task_id)
        else:
            return await self._execute_sequential(config, task, task_id)

    async def _execute_sequential(self, config: CrewConfig, task: str, task_id: str) -> Dict[str, Any]:
        context = {"task": task, "crew_name": config.name}
        results = []
        delegation_log = []

        for member in config.members:
            if member.agent_id not in self.orchestrator.agents:
                results.append({"agent_id": member.agent_id, "error": "Agent not found"})
                continue

            agent = self.orchestrator.agents[member.agent_id]
            enriched_payload = {
                "message": task,
                "role": member.role,
                "goal": member.goal,
                "backstory": member.backstory,
                "context": context,
                "task_id": task_id,
                "allow_delegation": member.allow_delegation,
                "previous_results": results[-1] if results else None
            }

            result = await self.orchestrator._send_to_agent(member.agent_id, enriched_payload, task_id)
            results.append({"agent_id": member.agent_id, "role": member.role, "result": result})

            if member.allow_delegation and isinstance(result, dict):
                delegated_to = result.get("delegate_to")
                if delegated_to and delegated_to in self.orchestrator.agents:
                    delegated_result = await self.orchestrator._send_to_agent(delegated_to, {"message": result.get("delegate_task", task), "delegated_from": member.agent_id}, task_id)
                    delegation_log.append({"from": member.agent_id, "to": delegated_to, "result": delegated_result})
                    context["delegation_result"] = delegated_result

            context["last_output"] = result.get("output", result.get("summary", str(result)))

        return {
            "task_id": task_id,
            "pattern": "crew_sequential",
            "crew_name": config.name,
            "results": results,
            "delegations": delegation_log,
            "final_output": context.get("last_output", "")
        }

    async def _execute_hierarchical(self, config: CrewConfig, task: str, task_id: str) -> Dict[str, Any]:
        if not config.members:
            return {"error": "No crew members"}

        leader = config.members[0]
        workers = [m for m in config.members[1:] if m.agent_id in self.orchestrator.agents]

        leader_payload = {
            "message": task,
            "role": leader.role,
            "goal": leader.goal,
            "backstory": leader.backstory,
            "task_id": task_id,
            "is_leader": True,
            "worker_count": len(workers)
        }
        leader_result = await self.orchestrator._send_to_agent(leader.agent_id, leader_payload, task_id)

        worker_results = []
        for worker in workers:
            wp = {
                "message": task,
                "role": worker.role,
                "goal": worker.goal,
                "backstory": worker.backstory,
                "task_id": task_id,
                "from_leader": leader.agent_id
            }
            wr = await self.orchestrator._send_to_agent(worker.agent_id, wp, task_id)
            worker_results.append({"agent_id": worker.agent_id, "role": worker.role, "result": wr})

        coordinator_payload = {
            "message": task,
            "role": leader.role,
            "task_id": task_id,
            "is_coordinating": True,
            "worker_results": worker_results
        }
        final = await self.orchestrator._send_to_agent(leader.agent_id, coordinator_payload, task_id)

        return {
            "task_id": task_id,
            "pattern": "crew_hierarchical",
            "crew_name": config.name,
            "leader": leader.agent_id,
            "worker_results": worker_results,
            "final_output": final
        }


# ============================================================
# DEBATE ORCHESTRATOR (Multi-Agent Debate pattern)
# ============================================================
class DebateOrchestrator:
    """Structured debate between agents with proponent/opponent/neutral roles."""

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self.active_debates: Dict[str, Dict[str, Any]] = {}

    async def run_debate(self, config: DebateConfig, user_id: int = None) -> Dict[str, Any]:
        debate_id = hashlib.md5(f"{config.topic}{time.time()}".encode()).hexdigest()[:12]
        self.orchestrator.state.create_task(debate_id, {"topic": config.topic, "debate": True, "user_id": user_id})

        rounds: List[DebateRound] = []
        arguments: Dict[str, List[str]] = {role.value: [] for role in DebateRole}

        proponent_id = config.participants.get(DebateRole.PROPONENT)
        opponent_id = config.participants.get(DebateRole.OPPONENT)
        neutral_id = config.participants.get(DebateRole.NEUTRAL)
        judge_id = config.participants.get(DebateRole.JUDGE)

        for round_num in range(1, config.max_rounds + 1):
            if proponent_id and proponent_id in self.orchestrator.agents:
                pro_payload = {
                    "message": f"Debate topic: {config.topic}",
                    "debate_role": "proponent",
                    "round": round_num,
                    "opponent_arguments": arguments.get("opponent", []),
                    "task_id": debate_id
                }
                pro_result = await self.orchestrator._send_to_agent(proponent_id, pro_payload, debate_id)
                pro_arg = pro_result.get("argument", pro_result.get("output", pro_result.get("summary", str(pro_result))))
                rounds.append(DebateRound(round_num=round_num, role=DebateRole.PROPONENT, agent_id=proponent_id, argument=pro_arg))
                arguments["proponent"].append(pro_arg)

            if opponent_id and opponent_id in self.orchestrator.agents:
                opp_payload = {
                    "message": f"Debate topic: {config.topic}",
                    "debate_role": "opponent",
                    "round": round_num,
                    "proponent_arguments": arguments.get("proponent", []),
                    "task_id": debate_id
                }
                opp_result = await self.orchestrator._send_to_agent(opponent_id, opp_payload, debate_id)
                opp_arg = opp_result.get("argument", opp_result.get("output", opp_result.get("summary", str(opp_result))))
                rounds.append(DebateRound(round_num=round_num, role=DebateRole.OPPONENT, agent_id=opponent_id, argument=opp_arg))
                arguments["opponent"].append(opp_arg)

            if neutral_id and neutral_id in self.orchestrator.agents:
                neu_payload = {
                    "message": f"Debate topic: {config.topic}",
                    "debate_role": "neutral",
                    "round": round_num,
                    "all_arguments": arguments,
                    "task_id": debate_id
                }
                neu_result = await self.orchestrator._send_to_agent(neutral_id, neu_payload, debate_id)
                neu_arg = neu_result.get("argument", neu_result.get("output", neu_result.get("summary", str(neu_result))))
                rounds.append(DebateRound(round_num=round_num, role=DebateRole.NEUTRAL, agent_id=neutral_id, argument=neu_arg))
                arguments["neutral"].append(neu_arg)

        judgment = None
        if config.require_judgment and judge_id and judge_id in self.orchestrator.agents:
            judge_payload = {
                "message": f"Judge debate: {config.topic}",
                "debate_role": "judge",
                "all_rounds": [{"round": r.round_num, "role": r.role.value, "argument": r.argument} for r in rounds],
                "arguments": arguments,
                "task_id": debate_id
            }
            judgment = await self.orchestrator._send_to_agent(judge_id, judge_payload, debate_id)

        self.active_debates[debate_id] = {
            "config": config,
            "rounds": rounds,
            "judgment": judgment,
            "completed_at": datetime.now().isoformat()
        }

        return {
            "debate_id": debate_id,
            "topic": config.topic,
            "total_rounds": config.max_rounds,
            "rounds": [{"round": r.round_num, "role": r.role.value, "agent": r.agent_id, "argument": r.argument[:300]} for r in rounds],
            "judgment": judgment,
            "argument_summary": {k: len(v) for k, v in arguments.items()}
        }

    def get_debate(self, debate_id: str) -> Optional[Dict[str, Any]]:
        return self.active_debates.get(debate_id)

    def list_debates(self) -> List[Dict[str, Any]]:
        return [{"id": did, "topic": d["config"].topic, "rounds": len(d["rounds"]), "completed": d.get("completed_at")} for did, d in self.active_debates.items()]


# ============================================================
# HANDOFF MANAGER (Direct specialist routing)
# ============================================================
class HandoffManager:
    """Direct agent-to-agent handoff without manager intermediary."""

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self.handoff_rules: List[HandoffRule] = []
        self.handoff_log: List[Dict[str, Any]] = []

    def add_rule(self, rule: HandoffRule):
        self.handoff_rules.append(rule)
        logger.info(f"Handoff rule: {rule.from_agent} -> {rule.to_agent} ({rule.strategy.value})")

    def remove_rule(self, from_agent: str, to_agent: str):
        self.handoff_rules = [r for r in self.handoff_rules if not (r.from_agent == from_agent and r.to_agent == to_agent)]

    def get_rules_for(self, agent_id: str) -> List[HandoffRule]:
        return [r for r in self.handoff_rules if r.from_agent == agent_id]

    async def handoff(self, from_agent: str, to_agent: str, task: str, context: Dict[str, Any] = None, hop_count: int = 0) -> Dict[str, Any]:
        rule = None
        for r in self.handoff_rules:
            if r.from_agent == from_agent and r.to_agent == to_agent:
                rule = r
                break

        if rule and hop_count >= rule.max_hops:
            return {"error": f"Max hops ({rule.max_hops}) exceeded for handoff {from_agent} -> {to_agent}"}

        payload = {"message": task, "handed_off_from": from_agent, "hop_count": hop_count + 1}
        if context:
            if rule and rule.strategy == HandoffStrategy.WITH_CONTEXT:
                payload["full_context"] = context
            elif rule and rule.strategy == HandoffStrategy.SUMMARIZED:
                payload["context_summary"] = {k: str(v)[:200] for k, v in context.items()}
            else:
                payload["context"] = context

        result = await self.orchestrator._send_to_agent(to_agent, payload, hashlib.md5(f"{task}{time.time()}".encode()).hexdigest()[:12])

        self.handoff_log.append({
            "from": from_agent,
            "to": to_agent,
            "task": task[:100],
            "strategy": rule.strategy.value if rule else "direct",
            "timestamp": datetime.now().isoformat(),
            "success": "error" not in (result or {})
        })

        return result or {}

    async def smart_handoff(self, from_agent: str, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        candidates = self.get_rules_for(from_agent)
        if not candidates:
            return {"error": f"No handoff rules for agent {from_agent}"}

        best = candidates[0]
        for rule in candidates:
            if task.lower().startswith(tuple(kw.lower() for kw in rule.trigger_keywords)):
                best = rule
                break

        return await self.handoff(from_agent, best.to_agent, task, context)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_rules": len(self.handoff_rules),
            "total_handoffs": len(self.handoff_log),
            "success_rate": sum(1 for h in self.handoff_log if h["success"]) / max(len(self.handoff_log), 1),
            "recent": self.handoff_log[-5:] if self.handoff_log else []
        }


# ============================================================
# SWARM ORCHESTRATOR (Peer-to-peer collaboration)
# ============================================================
class SwarmOrchestrator:
    """Peer-to-peer agent swarm with capability-based routing."""

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self.swarm_agents: Dict[str, SwarmAgent] = {}
        self.active_swarms: Dict[str, Dict[str, Any]] = {}

    def register_swarm_agent(self, agent_id: str, capabilities: List[str], neighbors: List[str] = None):
        self.swarm_agents[agent_id] = SwarmAgent(
            agent_id=agent_id,
            capabilities=capabilities,
            neighbors=neighbors or []
        )

    def find_capable_agents(self, required_capabilities: List[str]) -> List[str]:
        capable = []
        for aid, sa in self.swarm_agents.items():
            if aid in self.orchestrator.agents and self.orchestrator.agents[aid].config.enabled:
                if any(cap in sa.capabilities for cap in required_capabilities):
                    capable.append(aid)
        return capable

    def get_lightest_agent(self, candidates: List[str]) -> Optional[str]:
        if not candidates:
            return None
        loads = {aid: self.swarm_agents.get(aid, SwarmAgent(agent_id=aid)).load for aid in candidates}
        return min(loads, key=loads.get)

    async def swarm_execute(self, task: str, required_capabilities: List[str], user_id: int = None, max_agents: int = 3) -> Dict[str, Any]:
        task_id = hashlib.md5(f"{task}{time.time()}".encode()).hexdigest()[:12]
        self.orchestrator.state.create_task(task_id, {"task": task, "swarm": True, "user_id": user_id})

        candidates = self.find_capable_agents(required_capabilities)
        if not candidates:
            candidates = list(self.swarm_agents.keys())[:max_agents]
        selected = candidates[:max_agents]

        for aid in selected:
            if aid in self.swarm_agents:
                self.swarm_agents[aid].load += 1.0

        peer_results = []
        for aid in selected:
            payload = {
                "message": task,
                "swarm_mode": True,
                "peers": [a for a in selected if a != aid],
                "task_id": task_id
            }
            result = await self.orchestrator._send_to_agent(aid, payload, task_id)
            peer_results.append({"agent_id": aid, "result": result})

        consensus = await self._build_consensus(peer_results, task)

        for aid in selected:
            if aid in self.swarm_agents:
                self.swarm_agents[aid].load = max(0, self.swarm_agents[aid].load - 1.0)

        self.active_swarms[task_id] = {
            "task": task,
            "agents": selected,
            "results": peer_results,
            "consensus": consensus,
            "completed_at": datetime.now().isoformat()
        }

        return {
            "task_id": task_id,
            "pattern": "swarm",
            "selected_agents": selected,
            "peer_results": peer_results,
            "consensus": consensus
        }

    async def _build_consensus(self, peer_results: List[Dict[str, Any]], task: str) -> Dict[str, Any]:
        if not peer_results:
            return {"strategy": "none", "result": None}

        successful = [r for r in peer_results if r.get("result") and "error" not in r["result"]]
        if not successful:
            return {"strategy": "none", "result": None, "error": "All agents failed"}

        if len(successful) == 1:
            return {"strategy": "single", "result": successful[0]["result"]}

        outputs = []
        for r in successful:
            res = r["result"]
            output = res.get("output", res.get("summary", res.get("draft", str(res))))
            outputs.append(output)

        if len(set(str(o)[:50] for o in outputs)) == 1:
            return {"strategy": "unanimous", "result": successful[0]["result"]}

        return {"strategy": "majority", "result": successful[0]["result"], "alternatives": len(successful) - 1}

    def get_status(self) -> Dict[str, Any]:
        return {
            "swarm_agents": len(self.swarm_agents),
            "active_swarms": len(self.active_swarms),
            "agent_loads": {aid: sa.load for aid, sa in self.swarm_agents.items()}
        }


# ============================================================
# FLOW ORCHESTRATOR (Event-driven workflows)
# ============================================================
class FlowOrchestrator:
    """Event-driven workflow orchestration with state persistence."""

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self.flows: Dict[str, FlowDefinition] = {}
        self.flow_states: Dict[str, Dict[str, Any]] = {}

    def define_flow(self, flow_def: FlowDefinition) -> str:
        flow_id = hashlib.md5(f"{flow_def.name}{time.time()}".encode()).hexdigest()[:8]
        self.flows[flow_id] = flow_def
        logger.info(f"Flow defined: {flow_def.name} ({len(flow_def.nodes)} nodes)")
        return flow_id

    def get_flow(self, flow_id: str) -> Optional[FlowDefinition]:
        return self.flows.get(flow_id)

    def list_flows(self) -> List[Dict[str, Any]]:
        return [{"id": fid, "name": fd.name, "nodes": len(fd.nodes), "start": fd.start_node} for fid, fd in self.flows.items()]

    async def execute_flow(self, flow_id: str, initial_data: Dict[str, Any] = None, user_id: int = None) -> Dict[str, Any]:
        flow = self.flows.get(flow_id)
        if not flow:
            return {"error": f"Flow '{flow_id}' not found"}

        exec_id = hashlib.md5(f"{flow_id}{time.time()}".encode()).hexdigest()[:12]
        self.orchestrator.state.create_task(exec_id, {"flow_id": flow_id, "flow_execution": True, "user_id": user_id})

        flow_state = {
            "flow_id": flow_id,
            "exec_id": exec_id,
            "current_node": flow.start_node,
            "data": initial_data or {},
            "node_results": {},
            "path": [],
            "started_at": datetime.now().isoformat()
        }
        self.flow_states[exec_id] = flow_state

        max_iterations = 20
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            current_id = flow_state["current_node"]
            node = flow.nodes.get(current_id)

            if not node:
                flow_state["error"] = f"Node '{current_id}' not found"
                break

            flow_state["path"].append(current_id)

            if node.node_type == FlowNodeType.START:
                if node.next_nodes:
                    flow_state["current_node"] = node.next_nodes[0]
                    continue
                else:
                    break

            elif node.node_type == FlowNodeType.AGENT:
                if node.agent_id and node.agent_id in self.orchestrator.agents:
                    payload = {
                        "message": flow_state["data"].get("message", flow_state["data"].get("task", "")),
                        "flow_exec_id": exec_id,
                        "flow_data": flow_state["data"],
                        "node_id": current_id
                    }
                    result = await self.orchestrator._send_to_agent(node.agent_id, payload, exec_id)
                    flow_state["node_results"][current_id] = result
                    flow_state["data"]["last_result"] = result

                    next_node = node.next_nodes[0] if node.next_nodes else None
                    if next_node:
                        flow_state["current_node"] = next_node
                        continue
                    else:
                        break
                else:
                    flow_state["error"] = f"Agent '{node.agent_id}' not found for node '{current_id}'"
                    break

            elif node.node_type == FlowNodeType.CONDITION:
                condition_met = self._evaluate_condition(node.condition, flow_state["data"])
                idx = 0 if condition_met else (1 if len(node.next_nodes) > 1 else 0)
                if idx < len(node.next_nodes):
                    flow_state["current_node"] = node.next_nodes[idx]
                    continue
                else:
                    break

            elif node.node_type == FlowNodeType.MERGE:
                if node.next_nodes:
                    flow_state["current_node"] = node.next_nodes[0]
                    continue
                else:
                    break

            elif node.node_type == FlowNodeType.END:
                break

        flow_state["completed_at"] = datetime.now().isoformat()
        flow_state["status"] = "completed" if "error" not in flow_state else "failed"

        return {
            "exec_id": exec_id,
            "flow_name": flow.name,
            "status": flow_state["status"],
            "path": flow_state["path"],
            "node_results": flow_state["node_results"],
            "final_data": flow_state["data"],
            "error": flow_state.get("error")
        }

    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        if not condition:
            return True
        try:
            last_result = data.get("last_result", {})
            if isinstance(last_result, dict):
                if "==" in condition:
                    key, val = condition.split("==", 1)
                    key, val = key.strip(), val.strip().strip('"').strip("'")
                    return str(last_result.get(key, "")) == val
                if "contains" in condition:
                    key, val = condition.split("contains", 1)
                    key, val = key.strip(), val.strip().strip('"').strip("'")
                    return val in str(last_result.get(key, ""))
                if "error" in last_result:
                    return False
                if last_result.get("confidence", 0) > 0.5:
                    return True
            return bool(last_result)
        except Exception:
            return True

    def get_flow_state(self, exec_id: str) -> Optional[Dict[str, Any]]:
        return self.flow_states.get(exec_id)


# ============================================================
# MAIN MANAGER
# ============================================================
class BotToBotManager:
    def __init__(self):
        self.message_bus = MessageBus()
        self.state_manager = StateManager()
        self.orchestrator = Orchestrator(self.message_bus, self.state_manager)
        self.crew = CrewOrchestrator(self.orchestrator)
        self.debate = DebateOrchestrator(self.orchestrator)
        self.handoff = HandoffManager(self.orchestrator)
        self.swarm = SwarmOrchestrator(self.orchestrator)
        self.flow = FlowOrchestrator(self.orchestrator)
        self._setup_default_agents()
        self._setup_default_flows()
        self._load_config()

    def _setup_default_agents(self):
        configs = [
            AgentConfig(id="triage", name="Triage Router", agent_type=AgentType.TRIAGE, capabilities=["routing", "classification"], priority=10),
            AgentConfig(id="research", name="Research Specialist", agent_type=AgentType.RESEARCH, capabilities=["search", "information gathering", "fact checking"], prompt="You are a research specialist. Search and gather information."),
            AgentConfig(id="analysis", name="Data Analyzer", agent_type=AgentType.ANALYSIS, capabilities=["data analysis", "statistics", "comparison"], prompt="You are a data analysis specialist."),
            AgentConfig(id="writing", name="Content Writer", agent_type=AgentType.WRITING, capabilities=["content creation", "copywriting", "editing"], prompt="You are a professional content writer."),
            AgentConfig(id="coding", name="Code Specialist", agent_type=AgentType.CODING, capabilities=["programming", "debugging", "code review"], prompt="You are a coding specialist."),
            AgentConfig(id="cyberdeck", name="Cyberdeck Builder", agent_type=AgentType.CYBERDECK, capabilities=["electronics picking", "3d printing", "enclosure design", "bom generation", "compatibility checking", "soldering guidance", "component selection", "image analysis"], prompt="You are a cyberdeck and electronics expert. Help users design, pick components, build, and troubleshoot cyberdecks and portable computing projects."),
        ]
        agent_classes = {"triage": TriageAgent, "research": ResearchAgent, "analysis": AnalysisAgent, "writing": WritingAgent, "coding": CodingAgent, "cyberdeck": CyberdeckAgent}
        for cfg in configs:
            cls = agent_classes.get(cfg.id, BaseAgent)
            self.orchestrator.register_agent(cls(cfg, self.message_bus, self.state_manager))
            self.swarm.register_swarm_agent(cfg.id, cfg.capabilities)

        self.handoff.add_rule(HandoffRule(from_agent="research", to_agent="analysis", trigger_keywords=["analyze", "compare", "evaluate"], strategy=HandoffStrategy.WITH_CONTEXT))
        self.handoff.add_rule(HandoffRule(from_agent="research", to_agent="writing", trigger_keywords=["write", "draft", "compose"], strategy=HandoffStrategy.SUMMARIZED))
        self.handoff.add_rule(HandoffRule(from_agent="analysis", to_agent="writing", trigger_keywords=["report", "summary", "draft"], strategy=HandoffStrategy.WITH_CONTEXT))
        self.handoff.add_rule(HandoffRule(from_agent="coding", to_agent="research", trigger_keywords=["documentation", "reference", "lookup"], strategy=HandoffStrategy.DIRECT))
        self.handoff.add_rule(HandoffRule(from_agent="coding", to_agent="cyberdeck", trigger_keywords=["cyberdeck", "sbc", "raspberry pi", "enclosure", "3d print", "electronics", "soldering", "hardware"], strategy=HandoffStrategy.WITH_CONTEXT))
        self.handoff.add_rule(HandoffRule(from_agent="research", to_agent="cyberdeck", trigger_keywords=["cyberdeck", "sbc", "build list", "components", "electronics picking", "portable computer"], strategy=HandoffStrategy.WITH_CONTEXT))
        self.handoff.add_rule(HandoffRule(from_agent="cyberdeck", to_agent="coding", trigger_keywords=["code", "script", "arduino", "python", "firmware", "programming"], strategy=HandoffStrategy.WITH_CONTEXT))

    def _setup_default_flows(self):
        research_flow = FlowDefinition(
            name="Research Pipeline",
            nodes={
                "start": FlowNode(id="start", node_type=FlowNodeType.START, next_nodes=["triage"]),
                "triage": FlowNode(id="triage", node_type=FlowNodeType.AGENT, agent_id="triage", next_nodes=["branch"]),
                "branch": FlowNode(id="branch", node_type=FlowNodeType.CONDITION, condition="confidence > 0.7", next_nodes=["research", "analysis"]),
                "research": FlowNode(id="research", node_type=FlowNodeType.AGENT, agent_id="research", next_nodes=["write"]),
                "analysis": FlowNode(id="analysis", node_type=FlowNodeType.AGENT, agent_id="analysis", next_nodes=["write"]),
                "write": FlowNode(id="write", node_type=FlowNodeType.AGENT, agent_id="writing", next_nodes=["end"]),
                "end": FlowNode(id="end", node_type=FlowNodeType.END)
            }
        )
        self.flow.define_flow(research_flow)

    def _load_config(self):
        if os.path.exists(AGENTS_CONFIG_FILE):
            try:
                with open(AGENTS_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded {len(config.get('agents', []))} custom agents")
            except Exception as e:
                logger.error(f"Failed to load agents config: {e}")

    def _save_config(self):
        config = {
            "agents": [{"id": a.config.id, "name": a.config.name, "type": a.config.agent_type.value, "enabled": a.config.enabled} for a in self.orchestrator.agents.values()],
            "updated_at": datetime.now().isoformat()
        }
        with open(AGENTS_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

    async def process_request(self, message: str, user_id: int = None) -> Dict[str, Any]:
        return await self.orchestrator.route_request(message, user_id)

    async def run_pipeline(self, message: str, agents: List[str]) -> Dict[str, Any]:
        return await self.orchestrator.sequential_pipeline(message, agents)

    async def run_parallel(self, message: str, agents: List[str]) -> Dict[str, Any]:
        return await self.orchestrator.parallel_execution(message, agents)

    async def run_hierarchical(self, message: str, supervisor: str, workers: List[str]) -> Dict[str, Any]:
        return await self.orchestrator.hierarchical_execution(message, supervisor, workers)

    async def run_crew(self, crew_id: str, task: str, user_id: int = None) -> Dict[str, Any]:
        return await self.crew.execute(crew_id, task, user_id)

    async def run_debate(self, topic: str, proponent: str, opponent: str, neutral: str = None, judge: str = None, rounds: int = 3, user_id: int = None) -> Dict[str, Any]:
        config = DebateConfig(topic=topic, max_rounds=rounds, participants={DebateRole.PROPONENT: proponent, DebateRole.OPPONENT: opponent})
        if neutral and neutral in self.orchestrator.agents:
            config.participants[DebateRole.NEUTRAL] = neutral
        if judge and judge in self.orchestrator.agents:
            config.participants[DebateRole.JUDGE] = judge
        return await self.debate.run_debate(config, user_id)

    async def run_handoff(self, from_agent: str, to_agent: str, task: str, context: Dict = None) -> Dict[str, Any]:
        return await self.handoff.handoff(from_agent, to_agent, task, context)

    async def run_swarm(self, task: str, capabilities: List[str], max_agents: int = 3, user_id: int = None) -> Dict[str, Any]:
        return await self.swarm.swarm_execute(task, capabilities, user_id, max_agents)

    async def run_flow(self, flow_id: str, data: Dict = None, user_id: int = None) -> Dict[str, Any]:
        return await self.flow.execute_flow(flow_id, data, user_id)

    def get_status(self) -> Dict[str, Any]:
        return {
            "version": "3.7.1",
            "agents": self.orchestrator.list_agents(),
            "active_tasks": len([s for s in self.state_manager.states.values() if s.status == TaskStatus.PROCESSING]),
            "total_messages": len(self.message_bus.message_log),
            "crews": len(self.crew.crews),
            "debates": len(self.debate.active_debates),
            "handoff_rules": len(self.handoff.handoff_rules),
            "swarm_agents": len(self.swarm.swarm_agents),
            "flows": len(self.flow.flows)
        }

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        agent = self.orchestrator.get_agent(agent_id)
        return agent.get_status() if agent else None

    def list_available_agents(self) -> List[str]:
        return list(self.orchestrator.agents.keys())


# ============================================================
# HELPER FUNCTIONS
# ============================================================
_manager_instance = None

def get_manager() -> BotToBotManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = BotToBotManager()
    return _manager_instance

def format_agent_status(status: Dict[str, Any]) -> str:
    lines = [
        f"🤖 **{status['name']}** ({status['type']})",
        f"   ID: `{status['id']}`",
        f"   Status: {'✅ Enabled' if status['enabled'] else '❌ Disabled'}",
        f"   Active: {status['active_tasks']} tasks",
        f"   Completed: {status['completed']}",
        f"   Failed: {status['failed']}"
    ]
    return "\n".join(lines)

def format_system_status(status: Dict[str, Any]) -> str:
    lines = [
        "🤖 **Bot-to-Bot Agent System v" + status['version'] + "**",
        f"   Agents: {len(status['agents'])}",
        f"   Active Tasks: {status['active_tasks']}",
        f"   Total Messages: {status['total_messages']}",
        "",
        "**Advanced Patterns:**",
        f"   👥 Crews: {status['crews']}",
        f"   🗣️ Debates: {status['debates']}",
        f"   🔄 Handoff Rules: {status['handoff_rules']}",
        f"   🐝 Swarm Agents: {status['swarm_agents']}",
        f"   📊 Flows: {status['flows']}",
        "",
        "**Available Agents:**"
    ]
    for agent in status['agents']:
        emoji = "✅" if agent['enabled'] else "❌"
        lines.append(f"   {emoji} `{agent['id']}` - {agent['name']}")
    return "\n".join(lines)
