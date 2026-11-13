import { describe, expect, it } from 'vitest';
import { isCoreCopyable } from '../electron/core-locator';

describe('isCoreCopyable', () => {
  it('copies seed data that ships inside the package', () => {
    expect(isCoreCopyable('mazhost/data/dev_checklists/feature-tests.md')).toBe(true);
    expect(isCoreCopyable('mazhost/data/workflow_templates/templates.json')).toBe(true);
  });

  it('never overwrites user state or generated cruft at any depth', () => {
    expect(isCoreCopyable('data')).toBe(false);
    expect(isCoreCopyable('.env')).toBe(false);
    expect(isCoreCopyable('.venv/Lib/site-packages/x.py')).toBe(false);
    expect(isCoreCopyable('mazhost/__pycache__/app.cpython-312.pyc')).toBe(false);
    expect(isCoreCopyable('logs/core.log')).toBe(false);
    expect(isCoreCopyable('tests/test_dev_centre.py')).toBe(false);
  });

  it('copies ordinary package files and directory roots', () => {
    expect(isCoreCopyable('')).toBe(true);
    expect(isCoreCopyable('mazhost')).toBe(true);
    expect(isCoreCopyable('mazhost\\app.py')).toBe(true);
    expect(isCoreCopyable('requirements.txt')).toBe(true);
    expect(isCoreCopyable('VERSION')).toBe(true);
  });
});
