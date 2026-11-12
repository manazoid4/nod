import react from '@vitejs/plugin-react';
import { defineConfig, type Plugin } from 'vite';

// The strict CSP in index.html applies to builds; the dev server needs inline HMR scripts.
const devNoCsp: Plugin = {
  name: 'dev-no-csp',
  transformIndexHtml: { order: 'pre', handler: (html, ctx) => (ctx.server ? html.replace(/<meta http-equiv="Content-Security-Policy"[^>]*>/, '') : html) },
};

export default defineConfig({
  plugins: [react(), devNoCsp],
  base: './',
  build: { outDir: 'dist/renderer', emptyOutDir: true },
  server: { port: 5173, strictPort: true },
});
