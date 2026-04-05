import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config';

export default mergeConfig(viteConfig, defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      include: ['src/lib/**', 'src/hooks/**', 'src/components/**'],
      exclude: ['src/test/**', 'src/**/*.test.*'],
      thresholds: {
        // Global thresholds — chart-heavy dashboard tabs are covered by E2E,
        // not unit tests, so global numbers are lower than lib/hooks.
        statements: 60,
        branches: 45,
        functions: 45,
        lines: 60,
        // Strict thresholds for core business logic
        'src/lib/**': {
          statements: 95,
          branches: 75,
          functions: 95,
          lines: 95,
        },
        'src/hooks/**': {
          statements: 90,
          branches: 80,
          functions: 80,
          lines: 90,
        },
      },
    },
  },
}));
