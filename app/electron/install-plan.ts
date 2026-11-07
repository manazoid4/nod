// Pure decision logic for "Set up Core": reuse an existing Core scheduled task instead of adding a second autostart.

export type InstallPlan = { kind: 'reuse-task'; task: string } | { kind: 'run-installer' };

/** Names of scheduled tasks that already keep Core alive (the real MAZPC uses `nod-core`; older installs use "MAZ Core ..."). */
const CORE_TASK = /^(nod-core|maz[ -]core)(\b.*)?$/i;

export function findCoreTask(taskNames: readonly string[]): string | null {
  const names = taskNames.map((n) => n.trim()).filter(Boolean);
  // Prefer the canonical name when several match.
  return names.find((n) => n.toLowerCase() === 'nod-core') ?? names.find((n) => CORE_TASK.test(n)) ?? null;
}

export function planInstall(taskNames: readonly string[]): InstallPlan {
  const task = findCoreTask(taskNames);
  return task ? { kind: 'reuse-task', task } : { kind: 'run-installer' };
}

/** Task names are passed to schtasks; refuse anything that is not a plain name. */
export function isSafeTaskName(name: string): boolean {
  return /^[\w .-]{1,80}$/.test(name);
}
