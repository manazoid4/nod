"""Feature graduation: every feature starts in Dev mode and reaches the main app once Maz confirms it works.

Features and their test steps come from the feature-tests checklist (one `## Heading` per feature).
Confirmations live in `<data>/dev/features.json`; the app shows only confirmed features outside Dev mode.
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


def slug(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


class ConfirmBody(BaseModel):
    model_config = ConfigDict(extra='forbid')
    note: str = Field(default='', max_length=500)


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
                current = {'id': slug(name), 'name': name, 'summary': SUMMARIES.get(slug(name), ''), 'steps': []}
                rows.append(current)
            elif current and (match := re.match(r'^\s*- \[[ xX]\] (.+)$', line)):
                current['steps'].append(match.group(1).strip())
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
        return {**feature, 'status': 'confirmed' if record.get('confirmed_at') else 'testing',
                'confirmed_at': record.get('confirmed_at'), 'note': record.get('note', '')}

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
        return write(feature_id, {'confirmed_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'note': body.note.strip()})

    @router.post('/{feature_id}/unconfirm')
    def unconfirm(feature_id: str):
        return write(feature_id, None)

    return router
