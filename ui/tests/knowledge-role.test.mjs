import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import ts from 'typescript'

function loadModule(path, dependencies = {}) {
  const { outputText } = ts.transpileModule(
    readFileSync(new URL(`../src/permission/${path}.ts`, import.meta.url), 'utf8'),
    { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } },
  )
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    assert.ok(Object.hasOwn(dependencies, id), `Unexpected dependency: ${id}`)
    return dependencies[id]
  }, exports)
  return exports
}

// 使用实际权限引擎和知识库策略，只替换浏览器 Store 与当前路由上下文。
function createPermissionContext(roles, permissions = {}) {
  const user = { roleSet: new Set(roles), permissionMap: new Map(Object.entries(permissions)) }
  const common = loadModule('core/common')
  const data = loadModule('core/data', { './common': common })
  const resourceContext = { getWorkspaceId: () => 'default' }
  const core = loadModule('core/index', {
    './common': common,
    './data': data,
    '@/stores': { useStore: () => ({ user }) },
    '@/utils/resource-context': resourceContext,
  })
  const policy = loadModule('policy', { './core': core, '@/utils/resource-context': resourceContext })
  const knowledge = loadModule('modules/knowledge/workspace', {
    '../../policy': policy,
    '../../core': core,
    '../../core/common': common,
    '@/utils/resource-context': resourceContext,
  })
  return { ...common, ...data, ...knowledge }
}

test('工作空间角色序列化与后端角色键一致，系统角色保持全局键', () => {
  const { Role, RoleConstants } = createPermissionContext([])
  assert.equal(new Role('WORKSPACE_MANAGE', 'default').toString(), 'WORKSPACE_MANAGE:w:default')
  assert.equal(RoleConstants.USER.getWorkspaceRole()({ workspaceId: 'default' }).toString(), 'USER:w:default')
  assert.equal(RoleConstants.ADMIN.toString(), 'ADMIN')
})

for (const [label, roles, allowed] of [
  ['所属空间管理员', ['WORKSPACE_MANAGE', 'WORKSPACE_MANAGE:w:default'], true],
  ['系统管理员', ['ADMIN'], true],
  ['其他空间管理员', ['WORKSPACE_MANAGE', 'WORKSPACE_MANAGE:w:other'], false],
  ['只有全局管理员类型、未分配空间', ['WORKSPACE_MANAGE'], false],
  ['未授权普通用户', ['USER', 'USER:w:default'], false],
]) {
  test(`${label}的知识库权限判断`, () => {
    const { canWorkspaceKnowledge, PermissionConstants, Group } = createPermissionContext(roles)
    for (const [name, permission] of Object.entries(PermissionConstants)) {
      if (permission.group === Group.KNOWLEDGE) {
        assert.equal(canWorkspaceKnowledge(permission, 'knowledge-a', 'default'), allowed, name)
      }
    }
  })
}

test('目标工作空间覆盖当前路由空间，管理员权限不能跨空间使用', () => {
  const { canWorkspaceKnowledge, PermissionConstants: P } = createPermissionContext(['WORKSPACE_MANAGE:w:other'])
  assert.equal(canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_READ, 'knowledge-a', 'other'), true)
  assert.equal(canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_READ, 'knowledge-a', 'default'), false)
})

test('普通用户的所有者权限只适用于本人资源和所属空间', () => {
  const permissions = { 'KNOWLEDGE:w:default:r:knowledge-a': 1n }
  const { canWorkspaceKnowledge, PermissionConstants: P } = createPermissionContext(['USER:w:default'], permissions)
  assert.equal(canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_READ, 'knowledge-a', 'default'), true)
  assert.equal(canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_READ, 'knowledge-b', 'default'), false)
  assert.equal(canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_READ, 'knowledge-a', 'other'), false)
  const foreignUser = createPermissionContext(['USER:w:other'], permissions)
  assert.equal(foreignUser.canWorkspaceKnowledge(foreignUser.PermissionConstants.KNOWLEDGE_DOCUMENT_READ, 'knowledge-a', 'default'), false)
})

test('显式授予文档查看权限不会放开图片及其他空间', () => {
  const { canWorkspaceKnowledge, PermissionConstants: P } = createPermissionContext([], { 'KNOWLEDGE_DOCUMENT:w:default': 1n })
  assert.equal(canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_READ, 'knowledge-a', 'default'), true)
  assert.equal(canWorkspaceKnowledge(P.KNOWLEDGE_IMAGE_READ, 'knowledge-a', 'default'), false)
  assert.equal(canWorkspaceKnowledge(P.KNOWLEDGE_DOCUMENT_READ, 'knowledge-a', 'other'), false)
})
