"""
n8n Workflow Generator — v1.0
OpenCode Bot Feature

Natural language to working n8n workflow JSON:
- Workflow generation from descriptions
- Template library
- Workflow editing
- Import/export
- Testing & validation
"""

import json
import os
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
N8N_DATA_FILE = os.path.join(BASE_DIR, "n8n_data.json")


class NodeType(Enum):
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    TRANSFORM = "transform"
    OUTPUT = "output"


@dataclass
class N8NNode:
    node_id: str
    node_type: str
    name: str
    parameters: Dict = field(default_factory=dict)
    position: List[int] = field(default_factory=lambda: [0, 0])
    credentials: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.node_id,
            "type": self.node_type,
            "name": self.name,
            "parameters": self.parameters,
            "position": self.position,
            "credentials": self.credentials
        }


@dataclass
class N8NWorkflow:
    workflow_id: str
    name: str
    description: str
    nodes: List[N8NNode] = field(default_factory=list)
    connections: Dict[str, Any] = field(default_factory=dict)
    active: bool = False
    created_by: str = ""
    created_at: float = 0.0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "nodes": [n.to_dict() for n in self.nodes],
            "connections": self.connections,
            "active": self.active,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "tags": self.tags
        }

    def to_n8n_json(self) -> Dict:
        n8n_nodes = []
        for node in self.nodes:
            n8n_node = {
                "id": node.node_id,
                "type": node.node_type,
                "typeVersion": 1,
                "position": node.position,
                "name": node.name,
                "parameters": node.parameters,
            }
            if node.credentials:
                n8n_node["credentials"] = node.credentials
            n8n_nodes.append(n8n_node)
        return {
            "name": self.name,
            "nodes": n8n_nodes,
            "connections": self.connections,
            "active": self.active,
            "settings": {
                "executionOrder": "v1"
            }
        }


WORKFLOW_TEMPLATES = {
    "telegram_ai_chatbot": {
        "name": "Telegram AI Chatbot",
        "description": "Listen for Telegram messages, process with AI, reply automatically",
        "nodes": [
            {"type": "n8n-nodes-base.telegramTrigger", "name": "Telegram Trigger",
             "parameters": {"updates": ["message"]}},
            {"type": "@n8n/n8n-nodes-langchain.agent", "name": "AI Agent",
             "parameters": {"options": {"systemMessage": "You are a helpful assistant."}}},
            {"type": "n8n-nodes-base.telegram", "name": "Send Reply",
             "parameters": {"operation": "sendMessage", "chatId": "={{$json.message.chat.id}}",
                           "text": "={{$json.output}}"}}
        ],
        "connections": {
            "Telegram Trigger": {"main": [[{"node": "AI Agent", "type": "main", "index": 0}]]},
            "AI Agent": {"main": [[{"node": "Send Reply", "type": "main", "index": 0}]]}
        },
        "tags": ["ai", "telegram", "chatbot"]
    },
    "rss_to_telegram": {
        "name": "RSS to Telegram Channel",
        "description": "Monitor RSS feeds and post new items to Telegram channel",
        "nodes": [
            {"type": "n8n-nodes-base.rssFeedRead", "name": "RSS Feed",
             "parameters": {"url": "={{$json.feedUrl}}"}},
            {"type": "n8n-nodes-base.if", "name": "Check New",
             "parameters": {"conditions": {"boolean": [{"value1": "={{$json.isNew}}"}]}}},
            {"type": "n8n-nodes-base.telegram", "name": "Post to Channel",
             "parameters": {"operation": "sendMessage", "chatId": "channel_id",
                           "text": "={{$json.title}}\n\n{{$json.link}}"}}
        ],
        "connections": {
            "RSS Feed": {"main": [[{"node": "Check New", "type": "main", "index": 0}]]},
            "Check New": {"main": [[{"node": "Post to Channel", "type": "main", "index": 0}]]}
        },
        "tags": ["rss", "telegram", "automation"]
    },
    "email_to_telegram": {
        "name": "Email Forwarder to Telegram",
        "description": "Forward incoming emails to Telegram with summary",
        "nodes": [
            {"type": "n8n-nodes-base.emailReadImap", "name": "Read Email",
             "parameters": {"options": {"forceReconnect": "everyMinute"}}},
            {"type": "n8n-nodes-base.openAi", "name": "Summarize",
             "parameters": {"operation": "message",
                           "prompt": "Summarize this email briefly:\n\n={{$json.text}}"}},
            {"type": "n8n-nodes-base.telegram", "name": "Send Summary",
             "parameters": {"operation": "sendMessage", "chatId": "user_id",
                           "text": "📧 {{$json.subject}}\n\n{{$json.output}}"}}
        ],
        "connections": {
            "Read Email": {"main": [[{"node": "Summarize", "type": "main", "index": 0}]]},
            "Summarize": {"main": [[{"node": "Send Summary", "type": "main", "index": 0}]]}
        },
        "tags": ["email", "telegram", "ai"]
    },
    "webhook_api": {
        "name": "Webhook API + Response",
        "description": "Receive webhook data and process with AI, return response",
        "nodes": [
            {"type": "n8n-nodes-base.webhook", "name": "Webhook",
             "parameters": {"httpMethod": "POST", "path": "api"}},
            {"type": "n8n-nodes-base.set", "name": "Parse Data",
             "parameters": {"values": {"string": [{"name": "input", "value": "={{$json.body}}"}]}}},
            {"type": "@n8n/n8n-nodes-langchain.agent", "name": "Process",
             "parameters": {}},
            {"type": "n8n-nodes-base.respondToWebhook", "name": "Respond",
             "parameters": {"respondWith": "json", "responseBody": "={{$json.output}}"}}
        ],
        "connections": {
            "Webhook": {"main": [[{"node": "Parse Data", "type": "main", "index": 0}]]},
            "Parse Data": {"main": [[{"node": "Process", "type": "main", "index": 0}]]},
            "Process": {"main": [[{"node": "Respond", "type": "main", "index": 0}]]}
        },
        "tags": ["webhook", "api", "ai"]
    },
    "scheduled_report": {
        "name": "Daily Report Sender",
        "description": "Generate and send daily reports via Telegram on schedule",
        "nodes": [
            {"type": "n8n-nodes-base.scheduleTrigger", "name": "Daily Trigger",
             "parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": "0 8 * * *"}]}}},
            {"type": "@n8n/n8n-nodes-langchain.agent", "name": "Generate Report",
             "parameters": {"prompt": "Generate a daily summary report."}},
            {"type": "n8n-nodes-base.telegram", "name": "Send Report",
             "parameters": {"operation": "sendMessage", "chatId": "user_id",
                           "text": "={{$json.output}}"}}
        ],
        "connections": {
            "Daily Trigger": {"main": [[{"node": "Generate Report", "type": "main", "index": 0}]]},
            "Generate Report": {"main": [[{"node": "Send Report", "type": "main", "index": 0}]]}
        },
        "tags": ["schedule", "report", "telegram"]
    },
    "lead_capture": {
        "name": "Lead Capture Funnel",
        "description": "Capture leads from webhook, enrich with AI, store in database",
        "nodes": [
            {"type": "n8n-nodes-base.webhook", "name": "Webhook",
             "parameters": {"httpMethod": "POST", "path": "leads"}},
            {"type": "@n8n/n8n-nodes-langchain.agent", "name": "Qualify Lead",
             "parameters": {"prompt": "Qualify this lead based on the data provided."}},
            {"type": "n8n-nodes-base.postgres", "name": "Store in DB",
             "parameters": {"operation": "insert", "table": "leads"}},
            {"type": "n8n-nodes-base.slack", "name": "Notify Team",
             "parameters": {"operation": "post", "channel": "#leads",
                           "text": "New lead: {{$json.name}}"}}
        ],
        "connections": {
            "Webhook": {"main": [[{"node": "Qualify Lead", "type": "main", "index": 0}]]},
            "Qualify Lead": {"main": [[{"node": "Store in DB", "type": "main", "index": 0}]]},
            "Store in DB": {"main": [[{"node": "Notify Team", "type": "main", "index": 0}]]}
        },
        "tags": ["lead", "crm", "database"]
    },
    "ai_content_pipeline": {
        "name": "AI Content Pipeline",
        "description": "Generate content with AI, review, post to social media",
        "nodes": [
            {"type": "n8n-nodes-base.scheduleTrigger", "name": "Schedule",
             "parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": "0 9 * * 1"}]}}},
            {"type": "@n8n/n8n-nodes-langchain.agent", "name": "Generate Content",
             "parameters": {"prompt": "Generate a social media post about tech trends."}},
            {"type": "n8n-nodes-base.telegram", "name": "Review Request",
             "parameters": {"operation": "sendMessage", "chatId": "admin_id",
                           "text": "📝 New content for review:\n\n{{$json.output}}\n\nApprove?"}},
            {"type": "n8n-nodes-base.telegramTrigger", "name": "Admin Response",
             "parameters": {"updates": ["callback_query"]}},
            {"type": "n8n-nodes-base.if", "name": "Approved?",
             "parameters": {"conditions": {"boolean": [{"value1": "={{$json.callback_query.data}}"}]}}},
            {"type": "n8n-nodes-base.twitter", "name": "Post to Twitter",
             "parameters": {"operation": "tweet", "text": "={{$json.content}}"}}
        ],
        "connections": {
            "Schedule": {"main": [[{"node": "Generate Content", "type": "main", "index": 0}]]},
            "Generate Content": {"main": [[{"node": "Review Request", "type": "main", "index": 0}]]},
            "Review Request": {"main": [[{"node": "Admin Response", "type": "main", "index": 0}]]},
            "Admin Response": {"main": [[{"node": "Approved?", "type": "main", "index": 0}]]},
            "Approved?": {"main": [[{"node": "Post to Twitter", "type": "main", "index": 0}]]}
        },
        "tags": ["content", "ai", "social"]
    },
    "google_sheets_sync": {
        "name": "Google Sheets Sync",
        "description": "Sync data between Google Sheets and other services",
        "nodes": [
            {"type": "n8n-nodes-base.googleSheetsTrigger", "name": "Sheet Trigger",
             "parameters": {"event": "rowAdded"}},
            {"type": "n8n-nodes-base.set", "name": "Transform",
             "parameters": {"values": {"string": [{"name": "key", "value": "={{$json.column1}}"}]}}},
            {"type": "n8n-nodes-base.notion", "name": "Update Notion",
             "parameters": {"operation": "create", "resource": "databasePage"}}
        ],
        "connections": {
            "Sheet Trigger": {"main": [[{"node": "Transform", "type": "main", "index": 0}]]},
            "Transform": {"main": [[{"node": "Update Notion", "type": "main", "index": 0}]]}
        },
        "tags": ["google", "notion", "sync"]
    }
}


N8N_NODE_CATEGORIES = {
    "triggers": [
        "n8n-nodes-base.webhook",
        "n8n-nodes-base.scheduleTrigger",
        "n8n-nodes-base.telegramTrigger",
        "n8n-nodes-base.emailReadImap",
        "n8n-nodes-base.rssFeedRead",
        "n8n-nodes-base.googleSheetsTrigger"
    ],
    "ai": [
        "@n8n/n8n-nodes-langchain.agent",
        "@n8n/n8n-nodes-langchain.chain",
        "@n8n/n8n-nodes-langchain.openAi",
        "n8n-nodes-base.openAi"
    ],
    "messaging": [
        "n8n-nodes-base.telegram",
        "n8n-nodes-base.slack",
        "n8n-nodes-base.emailSend"
    ],
    "data": [
        "n8n-nodes-base.postgres",
        "n8n-nodes-base.googleSheets",
        "n8n-nodes-base.notion",
        "n8n-nodes-base.airtable"
    ],
    "logic": [
        "n8n-nodes-base.if",
        "n8n-nodes-base.switch",
        "n8n-nodes-base.set",
        "n8n-nodes-base.merge"
    ],
    "social": [
        "n8n-nodes-base.twitter",
        "n8n-nodes-base.facebookGraph"
    ]
}


class N8NManager:
    def __init__(self):
        self.workflows: Dict[str, N8NWorkflow] = {}
        self.user_workflows: Dict[str, List[str]] = {}
        self._load_data()

    def _load_data(self):
        try:
            if os.path.exists(N8N_DATA_FILE):
                with open(N8N_DATA_FILE, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.user_workflows = data.get("user_workflows", {})
                    for wid, wdata in data.get("workflows", {}).items():
                        try:
                            wf = N8NWorkflow(
                                workflow_id=wid,
                                name=wdata.get("name", ""),
                                description=wdata.get("description", ""),
                                active=wdata.get("active", False),
                                created_by=wdata.get("created_by", ""),
                                created_at=wdata.get("created_at", 0),
                                tags=wdata.get("tags", [])
                            )
                            for ndata in wdata.get("nodes", []):
                                wf.nodes.append(N8NNode(**{
                                    k: v for k, v in ndata.items()
                                    if k in N8NNode.__dataclass_fields__
                                }))
                            wf.connections = wdata.get("connections", {})
                            self.workflows[wid] = wf
                        except Exception as e:
                            logger.warning(f"Failed to restore workflow {wid}: {e}")
        except Exception as e:
            logger.error(f"Failed to load n8n data: {e}")

    def _save_data(self):
        try:
            with open(N8N_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "workflows": {wid: wf.to_dict() for wid, wf in self.workflows.items()},
                    "user_workflows": self.user_workflows
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save n8n data: {e}")

    def list_templates(self) -> List[Dict]:
        return [
            {"id": tid, "name": t["name"], "description": t["description"],
             "tags": t.get("tags", []), "nodes": len(t["nodes"])}
            for tid, t in WORKFLOW_TEMPLATES.items()
        ]

    def get_template(self, template_id: str) -> Optional[Dict]:
        return WORKFLOW_TEMPLATES.get(template_id)

    def create_from_template(self, template_id: str, user_id: str,
                            name: str = "") -> Optional[N8NWorkflow]:
        template = WORKFLOW_TEMPLATES.get(template_id)
        if not template:
            return None
        wf_id = f"wf_{int(time.time()*1000) % 100000}"
        wf = N8NWorkflow(
            workflow_id=wf_id,
            name=name or template["name"],
            description=template["description"],
            active=False,
            created_by=user_id,
            created_at=time.time(),
            tags=template.get("tags", [])
        )
        for i, ndata in enumerate(template["nodes"]):
            wf.nodes.append(N8NNode(
                node_id=f"node_{i}",
                node_type=ndata["type"],
                name=ndata["name"],
                parameters=ndata.get("parameters", {}),
                position=[i * 200, 300]
            ))
        wf.connections = template.get("connections", {})
        self.workflows[wf_id] = wf
        if user_id not in self.user_workflows:
            self.user_workflows[user_id] = []
        self.user_workflows[user_id].append(wf_id)
        self._save_data()
        return wf

    def create_custom_workflow(self, user_id: str, name: str,
                               description: str, nodes_data: List[Dict]) -> N8NWorkflow:
        wf_id = f"wf_{int(time.time()*1000) % 100000}"
        wf = N8NWorkflow(
            workflow_id=wf_id, name=name, description=description,
            active=False, created_by=user_id, created_at=time.time()
        )
        connections = {}
        prev_name = None
        for i, ndata in enumerate(nodes_data):
            node_name = ndata.get("name", f"Node {i+1}")
            wf.nodes.append(N8NNode(
                node_id=f"node_{i}",
                node_type=ndata.get("type", "n8n-nodes-base.set"),
                name=node_name,
                parameters=ndata.get("parameters", {}),
                position=[i * 200, 300]
            ))
            if prev_name:
                if prev_name not in connections:
                    connections[prev_name] = {"main": [[]]}
                connections[prev_name]["main"][0].append({
                    "node": node_name, "type": "main", "index": 0
                })
            prev_name = node_name
        wf.connections = connections
        self.workflows[wf_id] = wf
        if user_id not in self.user_workflows:
            self.user_workflows[user_id] = []
        self.user_workflows[user_id].append(wf_id)
        self._save_data()
        return wf

    def generate_from_description(self, user_id: str, description: str) -> N8NWorkflow:
        desc_lower = description.lower()
        nodes_data = []

        if any(w in desc_lower for w in ["telegram", "bot", "chat"]):
            nodes_data.append({"type": "n8n-nodes-base.telegramTrigger", "name": "Telegram Trigger",
                              "parameters": {"updates": ["message"]}})
            nodes_data.append({"type": "@n8n/n8n-nodes-langchain.agent", "name": "AI Agent",
                              "parameters": {"options": {"systemMessage": "You are a helpful assistant."}}})
            nodes_data.append({"type": "n8n-nodes-base.telegram", "name": "Send Reply",
                              "parameters": {"operation": "sendMessage",
                                            "chatId": "={{$json.message.chat.id}}",
                                            "text": "={{$json.output}}"}})

        if any(w in desc_lower for w in ["email", "mail", "imap"]):
            nodes_data.append({"type": "n8n-nodes-base.emailReadImap", "name": "Read Email",
                              "parameters": {}})
            if any(w in desc_lower for w in ["summarize", "ai", "llm", "gpt"]):
                nodes_data.append({"type": "@n8n/n8n-nodes-langchain.agent", "name": "Summarize",
                                  "parameters": {"prompt": "Summarize this email."}})
            nodes_data.append({"type": "n8n-nodes-base.telegram", "name": "Notify",
                              "parameters": {"operation": "sendMessage"}})

        if any(w in desc_lower for w in ["webhook", "api", "http"]):
            nodes_data.append({"type": "n8n-nodes-base.webhook", "name": "Webhook",
                              "parameters": {"httpMethod": "POST", "path": "endpoint"}})
            if any(w in desc_lower for w in ["ai", "process", "gpt", "llm"]):
                nodes_data.append({"type": "@n8n/n8n-nodes-langchain.agent", "name": "Process",
                                  "parameters": {}})
            nodes_data.append({"type": "n8n-nodes-base.respondToWebhook", "name": "Respond",
                              "parameters": {"respondWith": "json"}})

        if any(w in desc_lower for w in ["schedule", "daily", "cron", "periodic"]):
            cron = "0 9 * * *"
            if "hourly" in desc_lower:
                cron = "0 * * * *"
            elif "weekly" in desc_lower:
                cron = "0 9 * * 1"
            elif "monthly" in desc_lower:
                cron = "0 9 1 * *"
            nodes_data.append({"type": "n8n-nodes-base.scheduleTrigger", "name": "Schedule",
                              "parameters": {"rule": {"interval": [
                                  {"field": "cronExpression", "expression": cron}
                              ]}}})

        if any(w in desc_lower for w in ["database", "postgres", "sql", "store"]):
            nodes_data.append({"type": "n8n-nodes-base.postgres", "name": "Database",
                              "parameters": {"operation": "insert"}})

        if any(w in desc_lower for w in ["google sheets", "spreadsheet", "excel"]):
            nodes_data.append({"type": "n8n-nodes-base.googleSheets", "name": "Sheets",
                              "parameters": {"operation": "append"}})

        if any(w in desc_lower for w in ["notion", "wiki", "docs"]):
            nodes_data.append({"type": "n8n-nodes-base.notion", "name": "Notion",
                              "parameters": {"operation": "create"}})

        if any(w in desc_lower for w in ["slack", "team"]):
            nodes_data.append({"type": "n8n-nodes-base.slack", "name": "Slack",
                              "parameters": {"operation": "post"}})

        if any(w in desc_lower for w in ["filter", "if", "condition", "check"]):
            nodes_data.insert(-1 if nodes_data else 0,
                            {"type": "n8n-nodes-base.if", "name": "Condition",
                             "parameters": {"conditions": {}}})

        if not nodes_data:
            nodes_data = [
                {"type": "n8n-nodes-base.webhook", "name": "Webhook Trigger",
                 "parameters": {"httpMethod": "POST"}},
                {"type": "n8n-nodes-base.set", "name": "Process Data",
                 "parameters": {"values": {}}},
            ]

        wf = self.create_custom_workflow(
            user_id, f"Custom: {description[:40]}", description, nodes_data
        )
        return wf

    def get_user_workflows(self, user_id: str) -> List[N8NWorkflow]:
        wf_ids = self.user_workflows.get(user_id, [])
        return [self.workflows[wid] for wid in wf_ids if wid in self.workflows]

    def delete_workflow(self, workflow_id: str, user_id: str) -> bool:
        if workflow_id in self.workflows:
            wf = self.workflows[workflow_id]
            if wf.created_by == user_id:
                del self.workflows[workflow_id]
                if user_id in self.user_workflows:
                    self.user_workflows[user_id] = [
                        w for w in self.user_workflows[user_id] if w != workflow_id
                    ]
                self._save_data()
                return True
        return False

    def toggle_workflow(self, workflow_id: str) -> bool:
        if workflow_id in self.workflows:
            self.workflows[workflow_id].active = not self.workflows[workflow_id].active
            self._save_data()
            return True
        return False

    def export_workflow(self, workflow_id: str) -> Optional[Dict]:
        wf = self.workflows.get(workflow_id)
        if wf:
            return wf.to_n8n_json()
        return None

    def get_node_categories(self) -> Dict[str, List[str]]:
        return N8N_NODE_CATEGORIES


_n8n_manager = None

def get_n8n_manager() -> N8NManager:
    global _n8n_manager
    if _n8n_manager is None:
        _n8n_manager = N8NManager()
    return _n8n_manager


def build_n8n_commands() -> str:
    return """
⚡ n8n Workflow Commands:

📋 TEMPLATES:
/n8n templates — List available templates
/n8n use <template_id> [name] — Create workflow from template

🔧 CREATE:
/n8n create <description> — Generate workflow from description
/n8n list — Your workflows
/n8n export <workflow_id> — Export as n8n JSON
/n8n delete <workflow_id> — Delete workflow
/n8n toggle <workflow_id> — Activate/deactivate

📖 HELP:
/n8n nodes — List node categories
/n8n help — Show this help

💡 Describe your automation and I'll generate the workflow!
Example: /n8n create a Telegram bot that summarizes emails daily
"""


def handle_n8n_command(update, context) -> str:
    if not context.args:
        return build_n8n_commands()

    subcmd = context.args[0].lower()
    user_id = str(update.effective_user.id)
    mgr = get_n8n_manager()

    if subcmd == "templates":
        templates = mgr.list_templates()
        lines = ["📋 **Workflow Templates:**\n"]
        for t in templates:
            tags = ", ".join(t["tags"]) if t["tags"] else "general"
            lines.append(f"**{t['id']}** — {t['name']}")
            lines.append(f"  {t['description']}")
            lines.append(f"  Tags: {tags} | Nodes: {t['nodes']}\n")
        return "\n".join(lines)

    elif subcmd == "use":
        if len(context.args) < 2:
            return "Usage: /n8n use <template_id> [name]"
        template_id = context.args[1]
        name = " ".join(context.args[2:]) if len(context.args) > 2 else ""
        wf = mgr.create_from_template(template_id, user_id, name)
        if wf:
            return (f"✅ Workflow created: **{wf.name}**\n"
                    f"ID: `{wf.workflow_id}`\n"
                    f"Nodes: {len(wf.nodes)}\n"
                    f"Export: /n8n export {wf.workflow_id}")
        return f"❌ Template '{template_id}' not found. Use /n8n templates to list."

    elif subcmd == "create":
        if len(context.args) < 2:
            return "Usage: /n8n create <description>\nExample: /n8n create a Telegram bot that summarizes emails daily"
        description = " ".join(context.args[1:])
        wf = mgr.generate_from_description(user_id, description)
        nodes_list = "\n".join(f"  {i+1}. `{n.node_type.split('.')[-1]}` — {n.name}"
                               for i, n in enumerate(wf.nodes))
        return (f"✅ Generated: **{wf.name}**\n"
                f"ID: `{wf.workflow_id}`\n\n"
                f"**Nodes:**\n{nodes_list}\n\n"
                f"Export: /n8n export {wf.workflow_id}")

    elif subcmd == "list":
        workflows = mgr.get_user_workflows(user_id)
        if not workflows:
            return "No workflows yet. Use /n8n create or /n8n use to start."
        lines = ["📁 **Your Workflows:**\n"]
        for wf in workflows:
            status = "🟢" if wf.active else "⚪"
            lines.append(f"{status} **{wf.name}** (`{wf.workflow_id}`)")
            lines.append(f"  Nodes: {len(wf.nodes)} | Tags: {', '.join(wf.tags) if wf.tags else 'none'}")
        return "\n".join(lines)

    elif subcmd == "export":
        if len(context.args) < 2:
            return "Usage: /n8n export <workflow_id>"
        wf_id = context.args[1]
        n8n_json = mgr.export_workflow(wf_id)
        if n8n_json:
            json_str = json.dumps(n8n_json, indent=2)
            return f"📦 **n8n Workflow JSON:**\n\n```json\n{json_str[:2000]}\n```"
        return "❌ Workflow not found."

    elif subcmd == "delete":
        if len(context.args) < 2:
            return "Usage: /n8n delete <workflow_id>"
        ok = mgr.delete_workflow(context.args[1], user_id)
        return "✅ Deleted." if ok else "❌ Not found or not yours."

    elif subcmd == "toggle":
        if len(context.args) < 2:
            return "Usage: /n8n toggle <workflow_id>"
        ok = mgr.toggle_workflow(context.args[1])
        if ok:
            wf = mgr.workflows.get(context.args[1])
            status = "activated" if wf and wf.active else "deactivated"
            return f"✅ Workflow {status}."
        return "❌ Workflow not found."

    elif subcmd == "nodes":
        cats = mgr.get_node_categories()
        lines = ["📖 **n8n Node Categories:**\n"]
        for cat, nodes in cats.items():
            lines.append(f"**{cat.title()}**:")
            for n in nodes:
                lines.append(f"  `{n.split('.')[-1]}`")
        return "\n".join(lines)

    elif subcmd == "help":
        return build_n8n_commands()

    return build_n8n_commands()
