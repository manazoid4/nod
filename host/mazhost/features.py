"""Feature graduation: every feature starts in Dev mode and reaches the main app once Maz confirms it works.

Features and their test steps come from the feature-tests checklist (one `## Heading` per feature).
Confirmations live in `<data>/dev/features.json`.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .dev_centre import atomic_write, file_lock

TEMPLATE = Path(__file__).parent / 'data' / 'dev_checklists' / 'feature-tests.md'
SUMMARIES = {
    'ask-on-piblo': 'Agents ask before risky steps; you allow or deny on Piblo.',
    'private-mode': 'One switch keeps everything on your own computers.',
    'where-was-i-park-it': 'Park a thought, then pick up where you left off.',
    'memory': 'Tell Piblo something once; it remembers.',
    'rescue': 'Your emergency contacts and notes, even offline.',
    'agent-builder': 'Describe a helper; Piblo drafts it for you to approve.',
    'speaks-first': 'Piblo speaks up when something is due.',
    'catch-me-up': 'A short summary of what you missed.',
    'buddy-forms': 'Buddy changes as you focus.',
    'onboarding': 'A few questions so Piblo fits you.',
    'maker': 'Printer status and safe pause or cancel.',
}

# These references describe the implementation, not proof of a device test.
CATALOGUE = {
    'ask-on-piblo': ('secure', 'host/mazhost/buddy.py', 'Piblo'),
    'private-mode': ('secure', 'host/mazhost/private_mode.py', 'None'),
    'where-was-i-park-it': ('everyday', 'host/mazhost/where.py', 'Piblo'),
    'memory': ('everyday', 'host/mazhost/memory_notes.py', 'None'),
    'rescue': ('everyday', 'host/mazhost/rescue.py', 'Piblo'),
    'agent-builder': ('workflows', 'host/mazhost/agent_builder.py', 'An available agent'),
    'speaks-first': ('buddy', 'host/mazhost/speaks_first.py', 'Audio output'),
    'catch-me-up': ('everyday', 'host/mazhost/catchup.py', 'None'),
    'buddy-forms': ('buddy', 'host/mazhost/buddy_forms.py', 'Piblo'),
    'onboarding': ('everyday', 'host/mazhost/onboarding.py', 'Piblo'),
    'maker': ('maker', 'host/mazhost/maker.py', 'Supported printer connection'),
    'device-pairing': ('connect', 'host/mazhost/pairing.py', 'Piblo and a computer on the same network'),
    'piblo-dev': ('dev', 'app/src/pages/PibloDev.tsx', 'Piblo Core and the Windows app'),
    'workflow-templates': ('workflows', 'host/mazhost/data/workflow_templates/templates.json', 'Piblo Core and the Windows app'),
}

EXTRA_FEATURES = [
    {'id': 'device-pairing', 'name': 'Connect Piblo', 'summary': 'Approve a connection between Piblo and this PC.',
     'steps': ['Start Connect to computer on Piblo.', 'Review the request on the PC.', 'Allow it and check the connection.']},
    {'id': 'piblo-dev', 'name': 'Piblo Dev', 'summary': 'Review development work, checks and agent usage.',
     'steps': ['Open Piblo Dev in the Windows app.', 'Review Today, Agents and Builds.']},
    {'id': 'workflow-templates', 'name': 'Workflow templates', 'summary': 'Prepare a task from a reusable workflow.',
     'steps': ['Open Templates in Piblo Dev.', 'Use a template and save a task draft.']},
]


def slug(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


class ConfirmBody(BaseModel):
    model_config = ConfigDict(extra='forbid')
    note: str = Field(default='', max_length=500)
    who: str = Field(default='', max_length=100)


def build_features_router(data_dir: Path) -> APIRouter:
    router = APIRouter(prefix='/features', tags=['features'])
    base = Path(data_dir) / 'dev'
    store = base / 'features.json'

    def catalogue() -> list[dict]:
        source = base / 'checklists' / 'feature-tests.md'
        text = (source if source.exists() else TEMPLATE).read_text(encoding='utf-8')
        rows, current = [], None
        for line in text.splitlines():
            if line.startswith('## '):
                name = line[3:].strip()
                ident = slug(name)
                category, source, dependencies = CATALOGUE.get(ident, ('dev', '', 'Unknown'))
                current = {'id': ident, 'name': name, 'summary': SUMMARIES.get(ident, name), 'steps': [],
                           'category': category, 'source': source, 'dependencies': dependencies}
                rows.append(current)
            elif current and (match := re.match(r'^\s*- \[[ xX]\] (.+)$', line)):
                current['steps'].append(match.group(1).strip())
        for extra in EXTRA_FEATURES:
            if any(row['id'] == extra['id'] for row in rows):
                continue
            category, source, dependencies = CATALOGUE[extra['id']]
            rows.append({**extra, 'category': category, 'source': source, 'dependencies': dependencies})
        return rows

    def load() -> dict:
        # Missing file = nothing confirmed. A damaged file is set aside and refused, never silently emptied
        # (otherwise the next confirm would wipe every other confirmation).
        if not store.exists():
            return {}
        try:
            state = json.loads(store.read_text(encoding='utf-8'))
            if isinstance(state, dict):
                return state
        except ValueError:
            pass
        store.replace(store.with_name(store.name + '.corrupt'))
        raise HTTPException(500, 'features_store_corrupt')

    def view(feature: dict, state: dict) -> dict:
        record = state.get(feature['id'], {})
        confirmed_at = record.get('confirmed_at')
        simulated = feature['id'] in {'private-mode', 'where-was-i-park-it', 'memory', 'rescue', 'agent-builder', 'speaks-first', 'catch-me-up', 'buddy-forms', 'maker', 'device-pairing', 'piblo-dev', 'workflow-templates'}
        status = 'simulated' if simulated else ('implemented' if feature['source'] else 'proposed')
        return {**feature, 'status': 'confirmed' if confirmed_at else status,
                'confirmed_at': confirmed_at, 'note': record.get('note', ''),
                'evidence': {'who': record.get('who') or None, 'when': confirmed_at, 'note': record.get('note', '')}}

    def find(feature_id: str) -> dict:
        feature = next((row for row in catalogue() if row['id'] == feature_id), None)
        if feature is None:
            raise HTTPException(404, 'feature_not_found')
        return feature

    def write(feature_id: str, record: dict | None) -> dict:
        feature = find(feature_id)
        base.mkdir(parents=True, exist_ok=True)
        with file_lock(store):
            state = load()
            if record is None:
                state.pop(feature_id, None)
            else:
                state[feature_id] = record
            atomic_write(store, json.dumps(state, indent=2))
        return view(feature, state)

    @router.get('')
    def list_features():
        with file_lock(store):
            state = load()
        return {'features': [view(row, state) for row in catalogue()]}

    @router.post('/{feature_id}/confirm')
    def confirm(feature_id: str, body: ConfirmBody | None = None):
        body = body or ConfirmBody()
        return write(feature_id, {'confirmed_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'note': body.note.strip(), 'who': body.who.strip()})

    @router.post('/{feature_id}/unconfirm')
    def unconfirm(feature_id: str):
        return write(feature_id, None)

    return router
