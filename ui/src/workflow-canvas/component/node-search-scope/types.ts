export interface NodeSearchScopeData {
  search_scope_type: 'custom' | 'referencing'
  search_scope_source: 'knowledge' | 'document'
  search_scope_reference: string[]
}
