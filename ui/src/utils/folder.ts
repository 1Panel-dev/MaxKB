/**
 * 位运算排序工具函数
 * 高16位-整数，低16位-小数
 */

const FRACTION_BITS = 16
const FRACTION_MASK = 0xffff

// 编码32位整数
function encode(integer: number, fraction = 0) {
  return (integer << FRACTION_BITS) | (fraction & FRACTION_MASK)
}

// 计算两个位置中间值 
function mid(pos1: number, pos2: number) {
  const midPos = (pos1 + pos2) >> 1
  if (midPos === pos1 || midPos === pos2) {
    return null
  }
  return midPos
}

// 重平衡，相邻位差小于2时，无法插入
// positions - { nodeId: position }
function rebalance(positions: any) {
  const sorted = Object.entries(positions).sort((a: any, b: any) => a[1] - b[1])

  const rebalanced = {} as Record<string, number>
  sorted.forEach(([nodeId], index) => {
    rebalanced[nodeId] = encode(index + 1, 0)
  })
  return rebalanced
}


export { encode, rebalance, mid }
