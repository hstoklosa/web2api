import js from '@eslint/js'
import pluginQuery from '@tanstack/eslint-plugin-query'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  ...pluginQuery.configs['flat/recommended'],
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
    },
    rules: {
      // Mantine's polymorphic wrappers are components, so shared UI built
      // with them stays eligible for fast refresh.
      'react-refresh/only-export-components': [
        'error',
        {
          allowConstantExport: true,
          extraHOCs: ['createPolymorphicComponent'],
        },
      ],
    },
  },
  {
    // Route modules export data-mode APIs alongside their component.
    files: ['src/app/routes/**/*.tsx'],
    rules: {
      'react-refresh/only-export-components': [
        'warn',
        {
          allowExportNames: [
            'loader',
            'action',
            'ErrorBoundary',
            'HydrateFallback',
            'shouldRevalidate',
          ],
        },
      ],
    },
  },
])
