"""
Bot-to-Bot Agent System v3.5.0
Multi-agent orchestration with specialized AI agents
Implements: Sequential, Parallel, Hierarchical patterns
Source: Telegram Bot API 10.0 Bot-to-Bot Communication + GitHub patterns
"""

import os
import json
import asyncio
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ============================================================
# CONSTANTS
# ============================================================
AGENTS_CONFIG_FILE = "agents_config.json"
MAX_MESSAGE_DEPTH = 10  # Prevent infinite loops
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
    SEQUENTIAL = "sequential"      # A -> B -> C -> Result
    PARALLEL = "parallel"          # A + B + C -> Combined
    HIERARCHICAL = "hierarchical"  # Supervisor -> Workers
    ROUND_ROBIN = "round_robin"    # Distribute across agents

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
    type: str  # request, response, event, error
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: str = ""
    depth: int = 0  # For loop prevention

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

# ============================================================
# MESSAGE BUS (Agent-to-Agent Communication)
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
        # Log message
        self.message_log.append(message)
        if len(self.message_log) > self.max_log_size:
            self.message_log = self.message_log[-self.max_log_size:]
        
        # Check depth for loop prevention
        if message.depth >= MAX_MESSAGE_DEPTH:
            logger.warning(f"Message depth limit reached: {message.depth}")
            return {"error": "Maximum message depth exceeded"}
        
        # Route to subscriber
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
        to_delete = [
            tid for tid, state in self.states.items()
            if state.created_at < cutoff
        ]
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
        
        # Register message handlers
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
    """Routes requests to appropriate specialist agents"""
    
    ROUTING_RULES = {
        "research": ["search", "find", "lookup", "discover", "what is", "how to"],
        "analysis": ["analyze", "compare", "evaluate", "measure", "data", "statistics"],
        "writing": ["write", "create", "draft", "compose", "content", "blog"],
        "coding": ["code", "program", "function", "bug", "debug", "implement", "api"],
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
            return {
                "routing": "support",
                "confidence": 0.5,
                "reason": "No specific match, defaulting to support"
            }
        
        best_match = max(scores, key=scores.get)
        confidence = min(scores[best_match] / 3.0, 1.0)
        
        return {
            "routing": best_match,
            "confidence": confidence,
            "reason": f"Matched {scores[best_match]} keywords for {best_match}"
        }


class ResearchAgent(BaseAgent):
    """Searches and gathers information"""
    
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = payload.get("query", payload.get("message", ""))
        
        # Use available AI providers for research
        research_result = {
            "query": query,
            "summary": f"Research results for: {query}",
            "sources": [],
            "confidence": 0.7
        }
        
        # Try to use AI for research summary
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
    """Processes and analyzes data"""
    
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload.get("data", payload.get("message", ""))
        
        analysis = {
            "input": str(data)[:200],
            "analysis": "Data analyzed",
            "metrics": {},
            "recommendations": []
        }
        
        # Basic text analysis
        if isinstance(data, str):
            words = data.split()
            analysis["metrics"] = {
                "word_count": len(words),
                "char_count": len(data),
                "sentence_count": data.count('.') + data.count('!') + data.count('?')
            }
        
        return analysis


class WritingAgent(BaseAgent):
    """Creates content"""
    
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        topic = payload.get("topic", payload.get("message", ""))
        style = payload.get("style", "professional")
        
        content = {
            "topic": topic,
            "style": style,
            "draft": f"Content about: {topic}",
            "word_count": 0
        }
        
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
    """Handles code-related tasks"""
    
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        task = payload.get("task", payload.get("message", ""))
        language = payload.get("language", "python")
        
        result = {
            "task": task,
            "language": language,
            "code": "",
            "explanation": ""
        }
        
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


# ============================================================
# ORCHESTRATOR
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
        """Route a user request to appropriate agents"""
        task_id = hashlib.md5(f"{message}{time.time()}".encode()).hexdigest()[:12]
        
        # Create task state
        task_state = self.state.create_task(task_id, {
            "message": message,
            "user_id": user_id
        })
        
        # Step 1: Triage
        if "triage" in self.agents:
            triage_result = await self._send_to_agent(
                "triage",
                {"message": message},
                task_id
            )
            routing = triage_result.get("routing", "support")
        else:
            routing = "support"
        
        # Step 2: Route to specialist
        specialist_result = await self._send_to_agent(
            routing,
            {"message": message, "task_id": task_id},
            task_id
        )
        
        return {
            "task_id": task_id,
            "routing": routing,
            "result": specialist_result,
            "status": "completed"
        }
    
    async def sequential_pipeline(self, message: str, agent_chain: List[str]) -> Dict[str, Any]:
        """Execute agents in sequence: A -> B -> C -> Result"""
        task_id = hashlib.md5(f"{message}{time.time()}".encode()).hexdigest()[:12]
        current_input = {"message": message}
        
        for agent_id in agent_chain:
            result = await self._send_to_agent(agent_id, current_input, task_id)
            current_input["previous_result"] = result
            current_input["message"] = result.get("output", result.get("summary", str(result)))
        
        return {
            "task_id": task_id,
            "pattern": "sequential",
            "chain": agent_chain,
            "final_result": current_input.get("previous_result")
        }
    
    async def parallel_execution(self, message: str, agent_ids: List[str]) -> Dict[str, Any]:
        """Execute multiple agents in parallel"""
        task_id = hashlib.md5(f"{message}{time.time()}".encode()).hexdigest()[:12]
        
        tasks = []
        for agent_id in agent_ids:
            tasks.append(self._send_to_agent(agent_id, {"message": message}, task_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        combined = {}
        for agent_id, result in zip(agent_ids, results):
            if isinstance(result, Exception):
                combined[agent_id] = {"error": str(result)}
            else:
                combined[agent_id] = result
        
        return {
            "task_id": task_id,
            "pattern": "parallel",
            "agents": agent_ids,
            "results": combined
        }
    
    async def hierarchical_execution(self, message: str, supervisor_id: str, worker_ids: List[str]) -> Dict[str, Any]:
        """Supervisor delegates to workers"""
        task_id = hashlib.md5(f"{message}{time.time()}".encode()).hexdigest()[:12]
        
        # Supervisor decomposes task
        supervisor_result = await self._send_to_agent(
            supervisor_id,
            {"message": message, "worker_ids": worker_ids, "decompose": True},
            task_id
        )
        
        # Workers execute subtasks
        worker_results = {}
        for worker_id in worker_ids:
            result = await self._send_to_agent(
                worker_id,
                {"message": message, "from_supervisor": supervisor_id},
                task_id
            )
            worker_results[worker_id] = result
        
        # Supervisor coordinates results
        final_result = await self._send_to_agent(
            supervisor_id,
            {"message": message, "worker_results": worker_results, "coordinate": True},
            task_id
        )
        
        return {
            "task_id": task_id,
            "pattern": "hierarchical",
            "supervisor": supervisor_id,
            "workers": worker_ids,
            "result": final_result
        }
    
    async def _send_to_agent(self, agent_id: str, payload: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """Send message to agent with loop prevention"""
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
# MAIN MANAGER
# ============================================================
class BotToBotManager:
    """Main manager for the Bot-to-Bot Agent System"""
    
    def __init__(self):
        self.message_bus = MessageBus()
        self.state_manager = StateManager()
        self.orchestrator = Orchestrator(self.message_bus, self.state_manager)
        self._setup_default_agents()
        self._load_config()
    
    def _setup_default_agents(self):
        """Register built-in agents"""
        # Triage Agent
        triage_config = AgentConfig(
            id="triage",
            name="Triage Router",
            agent_type=AgentType.TRIAGE,
            capabilities=["routing", "classification"],
            priority=10
        )
        self.orchestrator.register_agent(TriageAgent(triage_config, self.message_bus, self.state_manager))
        
        # Research Agent
        research_config = AgentConfig(
            id="research",
            name="Research Specialist",
            agent_type=AgentType.RESEARCH,
            capabilities=["search", "information gathering", "fact checking"],
            prompt="You are a research specialist. Search and gather information."
        )
        self.orchestrator.register_agent(ResearchAgent(research_config, self.message_bus, self.state_manager))
        
        # Analysis Agent
        analysis_config = AgentConfig(
            id="analysis",
            name="Data Analyzer",
            agent_type=AgentType.ANALYSIS,
            capabilities=["data analysis", "statistics", "comparison"],
            prompt="You are a data analysis specialist."
        )
        self.orchestrator.register_agent(AnalysisAgent(analysis_config, self.message_bus, self.state_manager))
        
        # Writing Agent
        writing_config = AgentConfig(
            id="writing",
            name="Content Writer",
            agent_type=AgentType.WRITING,
            capabilities=["content creation", "copywriting", "editing"],
            prompt="You are a professional content writer."
        )
        self.orchestrator.register_agent(WritingAgent(writing_config, self.message_bus, self.state_manager))
        
        # Coding Agent
        coding_config = AgentConfig(
            id="coding",
            name="Code Specialist",
            agent_type=AgentType.CODING,
            capabilities=["programming", "debugging", "code review"],
            prompt="You are a coding specialist."
        )
        self.orchestrator.register_agent(CodingAgent(coding_config, self.message_bus, self.state_manager))
    
    def _load_config(self):
        """Load custom agent configuration"""
        if os.path.exists(AGENTS_CONFIG_FILE):
            try:
                with open(AGENTS_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded {len(config.get('agents', []))} custom agents")
            except Exception as e:
                logger.error(f"Failed to load agents config: {e}")
    
    def _save_config(self):
        """Save agent configuration"""
        config = {
            "agents": [
                {
                    "id": agent.config.id,
                    "name": agent.config.name,
                    "type": agent.config.agent_type.value,
                    "enabled": agent.config.enabled
                }
                for agent in self.orchestrator.agents.values()
            ],
            "updated_at": datetime.now().isoformat()
        }
        with open(AGENTS_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    async def process_request(self, message: str, user_id: int = None) -> Dict[str, Any]:
        """Process a user request through the agent system"""
        return await self.orchestrator.route_request(message, user_id)
    
    async def run_pipeline(self, message: str, agents: List[str]) -> Dict[str, Any]:
        """Run a sequential pipeline"""
        return await self.orchestrator.sequential_pipeline(message, agents)
    
    async def run_parallel(self, message: str, agents: List[str]) -> Dict[str, Any]:
        """Run parallel agent execution"""
        return await self.orchestrator.parallel_execution(message, agents)
    
    async def run_hierarchical(self, message: str, supervisor: str, workers: List[str]) -> Dict[str, Any]:
        """Run hierarchical execution"""
        return await self.orchestrator.hierarchical_execution(message, supervisor, workers)
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "version": "3.5.0",
            "agents": self.orchestrator.list_agents(),
            "active_tasks": len([
                s for s in self.state_manager.states.values()
                if s.status == TaskStatus.PROCESSING
            ]),
            "total_messages": len(self.message_bus.message_log)
        }
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get specific agent status"""
        agent = self.orchestrator.get_agent(agent_id)
        return agent.get_status() if agent else None
    
    def list_available_agents(self) -> List[str]:
        """List all available agent IDs"""
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
    """Format agent status for display"""
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
    """Format system status for display"""
    lines = [
        "🤖 **Bot-to-Bot Agent System**",
        f"   Version: {status['version']}",
        f"   Agents: {len(status['agents'])}",
        f"   Active Tasks: {status['active_tasks']}",
        f"   Total Messages: {status['total_messages']}",
        "",
        "**Available Agents:**"
    ]
    for agent in status['agents']:
        emoji = "✅" if agent['enabled'] else "❌"
        lines.append(f"   {emoji} `{agent['id']}` - {agent['name']}")
    
    return "\n".join(lines)
