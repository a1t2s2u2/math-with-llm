import { ref } from 'vue'
import { generateSkeleton, generateLean } from '~/utils/api'
import type { SkeletonCard, LeanGeneration } from '~/types/api'

export function useAssist(noteId: string) {
  const skeletonCards = ref<SkeletonCard[]>([])
  const loadingSkeleton = ref(false)
  const loadingLean = ref(false)

  const requestSkeleton = async (blockId: string) => {
    loadingSkeleton.value = true
    const result = await generateSkeleton(noteId, blockId)
    skeletonCards.value = result.cards
    loadingSkeleton.value = false
  }

  const requestLean = async (blockId: string): Promise<LeanGeneration> => {
    loadingLean.value = true
    const result = await generateLean(noteId, blockId)
    loadingLean.value = false
    return result
  }

  return {
    skeletonCards,
    loadingSkeleton,
    loadingLean,
    requestSkeleton,
    requestLean
  }
}
