import js from '@eslint/js'
import typescript from '@typescript-eslint/eslint-plugin'
import typescriptParser from '@typescript-eslint/parser'
import vuePlugin from 'eslint-plugin-vue'
import vueParser from 'vue-eslint-parser'
import prettier from 'eslint-config-prettier'

export default [
  js.configs.recommended,
  ...vuePlugin.configs['flat/recommended'],
  {
    ignores: ['.nuxt/**', 'dist/**', '.output/**', 'node_modules/**']
  },
  {
    files: ['**/*.ts'],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module'
      },
      globals: {
        console: 'readonly',
        process: 'readonly'
      }
    },
    plugins: {
      '@typescript-eslint': typescript
    },
    rules: {
      ...typescript.configs.recommended.rules,
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-undef': 'off'
    }
  },
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: typescriptParser,
        ecmaVersion: 'latest',
        sourceType: 'module'
      },
      globals: {
        console: 'readonly',
        process: 'readonly',
        defineProps: 'readonly',
        defineEmits: 'readonly',
        defineExpose: 'readonly',
        withDefaults: 'readonly',
        defineNuxtComponent: 'readonly',
        useRoute: 'readonly',
        useRouter: 'readonly',
        useNuxtApp: 'readonly',
        navigateTo: 'readonly'
      }
    },
    plugins: {
      '@typescript-eslint': typescript
    },
    rules: {
      ...typescript.configs.recommended.rules,
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-undef': 'off',
      'vue/multi-word-component-names': 'off'
    }
  },
  prettier
]
