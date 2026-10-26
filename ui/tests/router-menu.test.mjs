import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { compileFunction } from 'node:vm'
import ts from 'typescript'

// 只替换路由树输入，执行生产菜单工具，避免加载页面组件及浏览器 Store。
const { outputText } = ts.transpileModule(
  readFileSync(new URL('../src/router/admin/utils.ts', import.meta.url), 'utf8'),
  { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } },
)

function loadMenuUtils(workspaceChildren = [], systemChildren = []) {
  const dependencies = {
    './workspace': { workspaceRoutes: { meta: { scope: 'workspace' }, children: workspaceChildren } },
    './system': { systemRoutes: { meta: { scope: 'system' }, children: systemChildren } },
  }
  const exports = {}
  compileFunction(outputText, ['require', 'exports'])((id) => {
    assert.ok(Object.hasOwn(dependencies, id), `Unexpected dependency: ${id}`)
    return dependencies[id]
  }, exports)
  return exports
}

function resourceRoute(name, title, order) {
  return {
    name,
    meta: { title, order },
    children: [
      { name: `${name}-list`, meta: { title: `${title}列表`, hidden: true } },
      { name: `${name}-detail`, meta: { title: `${title}详情`, hidden: true } },
    ],
  }
}

test('工作空间保留只有隐藏子路由的知识库和智能体入口', () => {
  const { getChildRouteList } = loadMenuUtils([
    resourceRoute('workspace-knowledge', '知识库', 30),
    resourceRoute('workspace-application', '智能体', 20),
    { name: 'workspace-shared-knowledge', meta: { title: '共享知识库详情', hidden: true } },
  ])
  const menus = getChildRouteList('workspace')
  assert.deepEqual(menus.map((menu) => menu.name), ['workspace-application', 'workspace-knowledge'])
  assert.deepEqual(menus[1].route, { name: 'workspace-knowledge' })
  assert.equal(menus[1].children?.length ?? 0, 0)
})

test('系统分组保留只有隐藏子路由的资源菜单', () => {
  const { getChildRouteList } = loadMenuUtils([], [{
    name: 'system-resource',
    meta: { title: '资源管理' },
    children: [resourceRoute('system-resource-knowledge', '知识库', 10)],
  }])
  const menus = getChildRouteList('system')
  assert.equal(menus[0]?.name, 'system-resource')
  assert.equal(menus[0]?.children?.[0]?.name, 'system-resource-knowledge')
})

test('详情权限过滤隐藏空分组，保留可访问入口并传入当前路由参数', () => {
  const { getMatchedChildRouteList } = loadMenuUtils()
  const params = { workspaceId: 'workspace-a', knowledgeId: 'knowledge-a', type: 'BASE' }
  const menus = getMatchedChildRouteList({
    params,
    matched: [{
      meta: { resourceDetailRoot: true },
      children: [
        {
          name: 'library', meta: { title: '资料库' }, children: [
            { name: 'document', meta: { title: '文档', permission: () => false } },
            {
              name: 'image', meta: {
                title: '图片',
                permission: (route) => {
                  assert.deepEqual(route.params, params)
                  return true
                },
              },
            },
          ],
        },
        {
          name: 'settings', meta: { title: '设置' }, children: [
            { name: 'scheduled-sync', meta: { title: '定时同步', permission: () => false } },
          ],
        },
      ],
    }],
  })
  assert.deepEqual(menus.map((menu) => menu.name), ['library'])
  assert.deepEqual(menus[0].children.map((menu) => menu.name), ['image'])
  assert.equal(menus[0].children[0].permission(), true)
})

test('详情类型过滤后没有可显示子页的分组仍然隐藏', () => {
  const { getMatchedChildRouteList } = loadMenuUtils()
  const menus = getMatchedChildRouteList({
    params: { type: 'WEB' },
    matched: [{
      meta: { resourceDetailRoot: true },
      children: [{
        name: 'library', meta: { title: '资料库' }, children: [{
          name: 'image', meta: { title: '图片', detailMenuVisible: (params) => params.type === 'BASE' },
        }],
      }],
    }],
  })
  assert.deepEqual(menus, [])
})
