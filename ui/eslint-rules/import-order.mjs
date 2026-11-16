// 项目导入分组；无绑定导入、注释和可执行语句作为排序边界。
import path from 'node:path'

const compare = (left, right) => (left < right ? -1 : left > right ? 1 : 0)
const frameworks = ['vue', 'vue-router', 'pinia']

function groupOf(source, isType, filename) {
  if (isType) return 1
  const resolved = source.startsWith('.') ? path.resolve(path.dirname(filename), source).replaceAll('\\', '/') : source
  if (/(?:@\/|\/src\/)api\/enums(?:\/|\.|$)/.test(resolved)) return 2
  if (/(?:@\/|\/src\/)api\//.test(resolved)) return 3
  if (!source.startsWith('.') && !source.startsWith('@/')) return 0
  if (/^@\/permission(?:\/index(?:\.ts)?)?$/.test(source)) return 6
  if (source.startsWith('.') || /^@\/(?:components|layout|views|workflow-canvas|conversation-panel|assets)\//.test(source)) return 4
  return 5
}

function renderImport(node, specifiers, isType, code) {
  const prefix = isType ? 'import type ' : 'import '
  const defaults = specifiers.filter((specifier) => specifier.type !== 'ImportSpecifier')
  const named = specifiers
    .filter((specifier) => specifier.type === 'ImportSpecifier')
    .sort((left, right) => compare(left.imported.name ?? left.imported.value, right.imported.name ?? right.imported.value))
  const bindings = defaults.map((specifier) => code.getText(specifier))
  if (named.length) {
    const names = named.map((specifier) =>
      specifier.importKind === 'type' ? code.getText(specifier).replace(/^type\s+/, '') : code.getText(specifier),
    )
    const singleLine = `{ ${names.join(', ')} }`
    const length = prefix.length + [...bindings, singleLine].join(', ').length + code.getText(node.source).length + 6
    // 与 .prettierrc.json 的 printWidth 保持一致。
    bindings.push(length > 150 ? `{\n${names.map((name) => `  ${name},`).join('\n')}\n}` : singleLine)
  }
  return `${prefix}${bindings.join(', ')} from ${code.getText(node.source)}${code.text.slice(node.source.range[1], node.range[1])}`
}

export default {
  meta: {
    type: 'layout',
    fixable: 'code',
    schema: [],
    messages: { order: '按框架、类型、枚举、API、组件与功能、公共模块、perm 的顺序整理导入。' },
  },
  create(context) {
    const code = context.sourceCode
    function check(nodes) {
      if (!nodes.length) return
      const entries = nodes.flatMap((node) => {
        // 带内部注释的声明原样保留，避免改变注释的作用对象。
        if (code.getCommentsInside(node).length) {
          return [
            { source: node.source.value, group: groupOf(node.source.value, node.importKind === 'type', context.filename), text: code.getText(node) },
          ]
        }
        const types = node.specifiers.filter((specifier) => node.importKind === 'type' || specifier.importKind === 'type')
        const values = node.specifiers.filter((specifier) => !types.includes(specifier))
        return [
          [types, true],
          [values, false],
        ]
          .filter(([specifiers]) => specifiers.length)
          .map(([specifiers, isType]) => ({
            source: node.source.value,
            group: groupOf(node.source.value, isType, context.filename),
            text: renderImport(node, specifiers, isType, code),
          }))
      })
      entries.sort((left, right) => {
        if (left.group !== right.group) return left.group - right.group
        if (left.group === 0) {
          const rank = (source) => (frameworks.includes(source) ? frameworks.indexOf(source) : frameworks.length)
          if (rank(left.source) !== rank(right.source)) return rank(left.source) - rank(right.source)
        }
        if (left.group === 4 && left.source.startsWith('@/') !== right.source.startsWith('@/')) return left.source.startsWith('@/') ? -1 : 1
        return compare(left.source, right.source)
      })
      const replacement = entries.map((entry) => entry.text).join('\n')
      const range = [nodes[0].range[0], nodes.at(-1).range[1]]
      if (code.text.slice(...range) !== replacement) {
        context.report({ node: nodes[0], messageId: 'order', fix: (fixer) => fixer.replaceTextRange(range, replacement) })
      }
    }
    return {
      Program(program) {
        let block = []
        for (const node of program.body) {
          // 仅含 inline type 的值导入在 verbatimModuleSyntax 下仍会执行模块。
          // 保留声明及位置，避免拆分后丢失初始化副作用。
          const inlineTypesOnly =
            node.type === 'ImportDeclaration' &&
            node.importKind !== 'type' &&
            node.specifiers.length > 0 &&
            node.specifiers.every((specifier) => specifier.importKind === 'type')
          const previous = block.at(-1)
          const gap = previous ? code.text.slice(previous.range[1], node.range[0]) : ''
          const leadingComment =
            node.type === 'ImportDeclaration' && code.getCommentsBefore(node).some((comment) => comment.loc.end.line >= node.loc.start.line - 1)
          // 不跨越声明、初始化、样式导入或注释调整模块执行次序。
          if (node.type !== 'ImportDeclaration' || !node.specifiers.length || inlineTypesOnly || leadingComment || gap.trim()) {
            check(block)
            block = []
          }
          if (node.type === 'ImportDeclaration' && node.specifiers.length && !inlineTypesOnly && !leadingComment) {
            const trailingComment = code.getCommentsAfter(node).some((comment) => comment.loc.start.line === node.loc.end.line)
            if (trailingComment) {
              check(block)
              block = []
            } else block.push(node)
          }
        }
        check(block)
      },
    }
  },
}
