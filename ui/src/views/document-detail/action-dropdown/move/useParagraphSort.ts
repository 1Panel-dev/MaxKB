/** 分段菜单移动和两处拖拽共用位置保存及本地排序。 */
import type { Ref } from 'vue'
import type { ParagraphItem } from '@/api/types'
import type { useDocumentDetailContext } from '@/views/document-detail/context'
import type { ParagraphMoveDirection } from './types'
import { useSortable, type SortableChange } from '@/utils/use-sortable'
import { MsgSuccess } from '@/utils/message'

interface ParagraphSortOptions {
  paragraphs: Ref<ParagraphItem[]>
  loading: Ref<boolean>
  disabled: Readonly<Ref<boolean>>
  directoryRef: Ref<HTMLElement | undefined>
  cardsRef: Ref<HTMLElement | undefined>
  knowledgeId: Readonly<Ref<string>>
  documentId: Readonly<Ref<string>>
  resourceApi: ReturnType<typeof useDocumentDetailContext>['resourceApi']
  onStart: () => void
}

export function useParagraphSort(options: ParagraphSortOptions) {
  let sortSnapshot: ParagraphItem[] = []

  // 菜单和拖拽均使用移动前的位置；索引只用于本地排序，不作为接口位置。
  function savePosition(previousParagraphs: ParagraphItem[], oldIndex: number, newIndex: number, position = previousParagraphs[newIndex]?.position) {
    const movedParagraph = previousParagraphs[oldIndex]
    if (!movedParagraph || position === undefined || (oldIndex === newIndex && position === movedParagraph.position)) {
      options.paragraphs.value = previousParagraphs
      sortSnapshot = []
      return
    }
    const oldPosition = movedParagraph.position
    options.loading.value = true
    return (
      options.resourceApi.paragraph
        .putParagraphPosition?.(options.knowledgeId.value, options.documentId.value, movedParagraph.id, position)
        .then(() => {
          // 拖拽已经移动数组；按当前索引移动到目标索引，两种入口得到相同的本地顺序。
          const reorderedParagraphs = [...options.paragraphs.value]
          const currentIndex = reorderedParagraphs.findIndex(({ id }) => id === movedParagraph.id)
          if (currentIndex < 0) return
          const currentParagraph = reorderedParagraphs.splice(currentIndex, 1)[0]!
          reorderedParagraphs.splice(newIndex, 0, currentParagraph)
          options.paragraphs.value = reorderedParagraphs.map((paragraph) => {
            let nextPosition = paragraph.position
            if (paragraph.id === movedParagraph.id) nextPosition = position
            else if (oldPosition < position && nextPosition > oldPosition && nextPosition <= position) nextPosition -= 1
            else if (oldPosition > position && nextPosition >= position && nextPosition < oldPosition) nextPosition += 1
            return nextPosition === paragraph.position ? paragraph : { ...paragraph, position: nextPosition }
          })
          MsgSuccess('移动成功')
        })
        .catch(() => {
          options.paragraphs.value = previousParagraphs
        }) ??
      Promise.resolve().then(() => {
        options.paragraphs.value = previousParagraphs
      })
    ).finally(() => {
      options.loading.value = false
      sortSnapshot = []
    })
  }

  function handleMoveParagraph(paragraph: ParagraphItem, direction: ParagraphMoveDirection) {
    if (options.loading.value) return
    const previousParagraphs = [...options.paragraphs.value]
    const oldIndex = previousParagraphs.findIndex(({ id }) => id === paragraph.id)
    if (oldIndex < 0) return
    const newIndex = direction === 'top' ? 0 : direction === 'bottom' ? previousParagraphs.length - 1 : oldIndex + (direction === 'up' ? -1 : 1)
    if (newIndex < 0 || newIndex >= previousParagraphs.length) return
    const position = direction === 'top' ? 1 : previousParagraphs[newIndex]!.position
    if (position === paragraph.position) return
    options.onStart()
    return savePosition(previousParagraphs, oldIndex, newIndex, position)
  }

  function handleSortStart() {
    sortSnapshot = [...options.paragraphs.value]
    options.onStart()
  }

  function handleSortEnd() {
    if (!options.loading.value) sortSnapshot = []
  }

  function handleSort({ oldIndex, newIndex }: SortableChange<ParagraphItem>) {
    return savePosition(sortSnapshot, oldIndex, newIndex)
  }

  const getSortOptions = () => ({
    disabled: options.disabled.value,
    preventOnFilter: false,
    onStart: handleSortStart,
    onEnd: handleSortEnd,
    onReorder: handleSort,
  })
  useSortable(options.directoryRef, options.paragraphs, () => ({
    ...getSortOptions(),
    filter: 'button:not(.paragraph-directory-drag-handle)',
    draggable: '> .paragraph-directory-row',
  }))
  useSortable(options.cardsRef, options.paragraphs, () => ({
    ...getSortOptions(),
    filter: '.paragraph-card-actions, a, button:not(.paragraph-card-drag__handle)',
    draggable: '> .paragraph-sort-row',
  }))

  return { handleMoveParagraph }
}
