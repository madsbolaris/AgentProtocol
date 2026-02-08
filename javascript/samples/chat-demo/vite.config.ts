import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { readFileSync } from 'fs';
import { resolve } from 'path';

// Custom plugin to serve agent-config.json from repository root
function agentConfigPlugin() {
  return {
    name: 'agent-config-plugin',
    configureServer(server: any) {
      server.middlewares.use((req: any, res: any, next: any) => {
        if (req.url === '/agent-config.json') {
          try {
            const configPath = resolve(__dirname, '../../../agent-config.json');
            const content = readFileSync(configPath, 'utf-8');
            res.setHeader('Content-Type', 'application/json');
            res.end(content);
          } catch (error) {
            console.error('Error serving agent-config.json:', error);
            res.statusCode = 404;
            res.end('Config file not found');
          }
        } else {
          next();
        }
      });
    },
  };
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), agentConfigPlugin()],
  server: {
    port: 3000,
    proxy: {
      // Proxy API calls to avoid CORS issues during development
      '/api': {
        target: 'http://localhost:3978',
        changeOrigin: true,
      },
    },
  },
});
