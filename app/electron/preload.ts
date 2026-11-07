import { contextBridge, ipcRenderer } from 'electron';
import type { CoreState, NodBridge } from '../shared/types';

const invoke = <T>(channel: string, ...args: unknown[]) => ipcRenderer.invoke(channel, ...args) as Promise<T>;

const bridge: NodBridge = {
  platform: process.platform,
  version: process.argv.find((a) => a.startsWith('--nod-version='))?.slice(14) ?? '',
  core: {
    state: () => invoke('core:state'),
    ensure: () => invoke('core:ensure'),
    restart: () => invoke('core:restart'),
    install: () => invoke('core:install'),
    openLogs: () => invoke('core:open-logs'),
    onState(cb) {
      const handler = (_e: unknown, s: CoreState) => cb(s);
      ipcRenderer.on('core:state-changed', handler);
      return () => ipcRenderer.removeListener('core:state-changed', handler);
    },
  },
  api: (method, path, body) => invoke('api:request', method, path, body),
  screen: () => invoke('api:screen'),
  audio: (path, body) => invoke('api:audio', path, body),
  device: { pair: () => invoke('device:pair') },
  settings: { get: () => invoke('settings:get'), set: (patch) => invoke('settings:set', patch) },
  env: { get: () => invoke('env:get'), set: (key, value) => invoke('env:set', key, value) },
  openExternal: (url) => invoke('shell:open-external', url),
};

contextBridge.exposeInMainWorld('nod', bridge);
