import assert from 'node:assert/strict'
import test from 'node:test'
import { createUrlFile } from '../src/conversation-panel/components/message-input/url-upload/index.ts'

test('URL 文本附件保留中文和换行，不按 Base64 解码', async () => {
  const content = '知识库内容\n第二行'
  const file = createUrlFile(content, '知识.txt', 'text/plain')
  assert.equal(await file.text(), content)
  assert.equal(file.size, Buffer.byteLength(content))
})

test('URL 二进制附件支持纯 Base64 和 data URL', async () => {
  const bytes = Uint8Array.from([0, 127, 128, 255])
  const base64 = Buffer.from(bytes).toString('base64')
  for (const content of [base64, `data:application/pdf;base64,${base64}`]) {
    const file = createUrlFile(content, 'test.pdf', 'application/pdf')
    assert.deepEqual(new Uint8Array(await file.arrayBuffer()), bytes)
    assert.equal(file.type, 'application/pdf')
  }
})

test('URL 附件拒绝损坏的 Base64', () => {
  assert.throws(() => createUrlFile('%%%invalid', 'test.pdf', 'application/pdf'))
})
