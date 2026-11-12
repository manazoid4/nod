from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mazhost import library
from mazhost.config import Settings
from mazhost.share_in import FakeTranscriber, Share, ShareIn, build_share_router


def test_captions_take_priority_and_summary_is_searchable(tmp_path):
    transcriber = FakeTranscriber('wrong transcript')

    class Model:
        def chat(self, messages, route):
            assert route == 'local_fast'
            assert messages[-1]['content'] == 'Build a garden bed. Add compost.'
            return 'Composting guide for the garden.', 'fake'

    svc = ShareIn(tmp_path, Model(), transcriber)
    result = svc.save(Share(url='https://example.com/garden', title='Garden',
                            captions='Build a garden bed. Add compost.'))
    assert transcriber.calls == []
    found = svc.resurface('composting')
    assert found[0]['id'] == result['id']
    saved = Path(found[0]['path']).read_text(encoding='utf-8')
    assert '## Notes\nComposting guide' in saved
    assert 'shared' in saved and 'captions' in saved
    assert library.recent(tmp_path)[0]['notes'] == result['summary']


def test_transcriber_and_deterministic_fallback(tmp_path):
    transcriber = FakeTranscriber('First sentence. Second sentence. Third sentence. Fourth sentence.')
    svc = ShareIn(tmp_path, transcriber=transcriber)
    result = svc.save(Share(url='https://example.com/video'))
    assert transcriber.calls == ['https://example.com/video']
    assert result['summary'] == 'First sentence. Second sentence. Third sentence.'
    assert svc.resurface('Second')[0]['id'] == result['id']


def test_model_failure_and_long_output_are_bounded(tmp_path):
    class Model:
        def chat(self, messages, route):
            raise RuntimeError('offline')

    result = ShareIn(tmp_path, Model()).save(Share(text='A useful reminder.'))
    assert result['summary'] == 'A useful reminder.'
    assert len(ShareIn(tmp_path).save(Share(text='x' * 2000))['summary']) <= 800


@pytest.mark.parametrize('body', [{}, {'url': 'file:///private'}, {'url': 'https://'}, {'text': ' '}])
def test_share_route_rejects_bad_input(tmp_path, body):
    api = FastAPI()
    api.include_router(build_share_router(Settings(dumps_dir=str(tmp_path), _env_file=None)))
    assert TestClient(api).post('/share', json=body).status_code == 422


def test_resaving_preserves_notes_and_merges_tags(tmp_path):
    original = library.save_item(tmp_path, url='https://example.com/item', notes='Personal note', tags=['mine'])
    result = ShareIn(tmp_path).save(Share(url='https://example.com/item', captions='Useful captions.'))
    assert result['id'] == original['id']
    text = Path(library.search(tmp_path, 'Personal')[0]['path']).read_text(encoding='utf-8')
    assert 'Personal note' in text and 'Useful captions.' in text and 'mine' in text
