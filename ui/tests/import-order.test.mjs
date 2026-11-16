import parser from '@typescript-eslint/parser'
import { Linter } from 'eslint'
import assert from 'node:assert/strict'
import { test } from 'node:test'
import vueParser from 'vue-eslint-parser'
import importOrder from '../eslint-rules/import-order.mjs'

function fix(source, vue = false) {
  return new Linter().verifyAndFix(source, [
    {
      languageOptions: { parser: vue ? vueParser : parser, parserOptions: { parser, sourceType: 'module', ecmaVersion: 'latest' } },
      plugins: { project: { rules: { 'import-order': importOrder } } },
      rules: { 'project/import-order': 'error' },
    },
  ])
}

test('groups dependencies, separates types, sorts members and keeps aliases', () => {
  const source = `import perm from '@/permission/index.ts'
import { z as last, a } from '@/utils/example'
import Local from './Local.vue'
import { RESOURCE_TYPE } from '@/api/enums'
import Api from '@/api/example'
import Shared from '@/components/Shared.vue'
import { ref, type Ref as VueRef, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { Z, A } from '@/api/types'
`
  const result = fix(source)
  assert.equal(result.messages.length, 0)
  assert.equal(
    result.output,
    `import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import type { A, Z } from '@/api/types'
import type { Ref as VueRef } from 'vue'
import { RESOURCE_TYPE } from '@/api/enums'
import Api from '@/api/example'
import Shared from '@/components/Shared.vue'
import Local from './Local.vue'
import { a, z as last } from '@/utils/example'
import perm from '@/permission/index.ts'
`,
  )
  assert.equal(fix(result.output).fixed, false)
})

test('preserves side effects, executable boundaries and comment associations', () => {
  const source = `import Z from './Z'
import './style.scss'
import A from './A'
initialize()
import B from './B' // 必须保留
// 特殊初始化说明
import C from './C'
import { z, /* 保留成员注释 */ a } from './D'
`
  assert.equal(fix(source).output, source)
})

test('sorts Vue script imports without changing template, style or script body', () => {
  const source = `<template><div>{{ value }}</div></template>
<script setup lang="ts">
import { ref, type Ref } from 'vue'
import type { Dict } from '@/api/types'
const value: Ref<Dict> = ref({})
</script>
<style scoped>div { color: red; }</style>`
  const result = fix(source, true)
  assert.equal(result.messages.length, 0)
  assert.match(result.output, /import type \{ Dict \} from '@\/api\/types'\nimport type \{ Ref \} from 'vue'/)
  assert.ok(result.output.startsWith('<template><div>{{ value }}</div></template>'))
  assert.ok(result.output.endsWith('const value: Ref<Dict> = ref({})\n</script>\n<style scoped>div { color: red; }</style>'))
  assert.equal(fix(result.output, true).fixed, false)
})

test('preserves runtime imports containing only inline types and import attributes', () => {
  const source = `import { type Model } from '@logicflow/core'
import data from './data.json' with { type: 'json' }
import { type as typeAlias } from './types'
`
  assert.equal(fix(source).output, source)
})

test('keeps leading comments attached to their original import', () => {
  const source = `// 特殊依赖
import Z from './Z'
import A from './A'
`
  assert.equal(fix(source).output, source)
})
