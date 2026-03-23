"""
config_loader.py
================
Single source of truth for all constants.

"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

# ── Paths ─────────────────────────────────────────────────────────────────────
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent

CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"
EXPORT_DIR = PROJECT_ROOT / "export"

EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load YAML ─────────────────────────────────────────────────────────────────
with open(CONFIG_PATH, "r") as _f:
    _data = yaml.safe_load(_f)

if _data is None:
    raise ValueError("Config file is empty")

CONFIG: Dict[str, Any] = _data

# ── Top-level constants ───────────────────────────────────────────────────────
COMPANY_NAME = CONFIG["simulation"]["company_name"]
COMPANY_DOMAIN = CONFIG["simulation"]["domain"]
COMPANY_DESCRIPTION = CONFIG["simulation"]["company_description"]
INDUSTRY = CONFIG["simulation"].get("industry", "technology")
BASE = CONFIG["simulation"].get("output_dir", str(EXPORT_DIR))
ORG_CHART = CONFIG["org_chart"]
LEADS = CONFIG["leads"]
PERSONAS = CONFIG["personas"]
DEFAULT_PERSONA = CONFIG["default_persona"]
LEGACY = CONFIG["legacy_system"]
PRODUCT_PAGE = CONFIG.get("product_page", "Product Launch")

# ── Platform abstraction constants ────────────────────────────────────────────
# These drive all user-facing platform names in LLM prompts, output paths,
# MongoDB collection names, and SimEvent tags.
_PLATFORM = CONFIG.get("platform", {})
_MSG = _PLATFORM.get("messaging", {})
_TKT = _PLATFORM.get("tickets", {})
_WIKI = _PLATFORM.get("wiki", {})

MSG_PLATFORM_NAME = _MSG.get("name", "Slack")
MSG_DM_LABEL = _MSG.get("dm_label", "Slack DM")
MSG_CHANNEL_LABEL = _MSG.get("channel_label", "Slack channel")
MSG_THREAD_LABEL = _MSG.get("thread_label", "Slack thread")
MSG_EXPORT_DIR = _MSG.get("export_dir", "slack")
MSG_COLLECTION = _MSG.get("collection", "slack_messages")

TKT_PLATFORM_NAME = _TKT.get("name", "JIRA")
TKT_ID_PREFIX = _TKT.get("id_prefix", "JIRA")
TKT_EXPORT_DIR = _TKT.get("export_dir", "jira")
TKT_COLLECTION = _TKT.get("collection", "jira_tickets")

WIKI_PLATFORM_NAME = _WIKI.get("name", "Confluence")
WIKI_ID_PREFIX = _WIKI.get("id_prefix", "CONF")
WIKI_EXPORT_DIR = _WIKI.get("export_dir", "confluence")

DEPARTED_EMPLOYEES: Dict[str, Dict] = {
    gap["name"]: {
        "left": gap["left"],
        "role": gap["role"],
        "knew_about": gap["knew_about"],
        "documented_pct": gap["documented_pct"],
    }
    for gap in CONFIG.get("knowledge_gaps", [])
}

ALL_NAMES = [name for dept in ORG_CHART.values() for name in dept]
LIVE_ORG_CHART = {dept: list(members) for dept, members in ORG_CHART.items()}
LIVE_PERSONAS = {k: dict(v) for k, v in PERSONAS.items()}

# ── Model preset ──────────────────────────────────────────────────────────────
_PRESET_NAME = CONFIG.get("quality_preset", "local_cpu")
_PRESET = CONFIG["model_presets"][_PRESET_NAME]
_PROVIDER = _PRESET.get("provider", "ollama")


def resolve_role(role_key: str) -> str:
    dept = CONFIG.get("roles", {}).get(role_key)
    if dept and dept in LEADS:
        return LEADS[dept]
    # Check org_chart directly for depts not in LEADS (e.g. CEO)
    if dept and dept in CONFIG.get("org_chart", {}):
        members = CONFIG["org_chart"][dept]
        if members:
            return members[0]
    return next(iter(LEADS.values()))
