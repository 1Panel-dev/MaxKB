// 树形结构转平
export function TreeToFlatten(treeData: any[]) {
  return treeData.reduce((acc, node) => {
    const { children, ...rest } = node
    return [...acc, rest, ...(children ? TreeToFlatten(children) : [])]
  }, [])
}
