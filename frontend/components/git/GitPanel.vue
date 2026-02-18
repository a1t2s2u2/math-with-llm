<template>
  <div class="git-panel">
    <div v-if="!gitStatus || !gitStatus.is_repo" class="init-section">
      <p>Not a git repository</p>
      <button class="init-btn" @click="handleInit">Initialize Repository</button>
    </div>

    <template v-else>
      <div class="branch-info">
        <span class="branch-icon">&#9741;</span>
        <span>{{ gitStatus.branch || '(no branch)' }}</span>
      </div>

      <div class="commit-section">
        <input
          v-model="commitMessage"
          class="commit-input"
          placeholder="Commit message"
          @keydown.ctrl.enter="handleCommit"
          @keydown.meta.enter="handleCommit"
        />
        <button
          class="commit-btn"
          :disabled="!commitMessage.trim() || gitStatus.staged.length === 0"
          @click="handleCommit"
        >
          Commit
        </button>
      </div>

      <div v-if="gitStatus.staged.length > 0" class="file-section">
        <div class="section-header">
          <span>Staged Changes</span>
          <span class="count">{{ gitStatus.staged.length }}</span>
        </div>
        <div
          v-for="file in gitStatus.staged"
          :key="'staged-' + file.path"
          class="file-item"
          @click="$emit('showDiff', { path: file.path, staged: true })"
        >
          <span :class="['status-badge', file.status]">{{ statusLabel(file.status) }}</span>
          <span class="file-path" :title="file.path">{{ file.path }}</span>
          <button class="action-btn unstage" title="Unstage" @click.stop="handleUnstage(file.path)">
            &minus;
          </button>
        </div>
      </div>

      <div v-if="gitStatus.unstaged.length > 0" class="file-section">
        <div class="section-header">
          <span>Changes</span>
          <span class="count">{{ gitStatus.unstaged.length }}</span>
        </div>
        <div
          v-for="file in gitStatus.unstaged"
          :key="'unstaged-' + file.path"
          class="file-item"
          @click="$emit('showDiff', { path: file.path, staged: false })"
        >
          <span :class="['status-badge', file.status]">{{ statusLabel(file.status) }}</span>
          <span class="file-path" :title="file.path">{{ file.path }}</span>
          <button
            class="action-btn discard"
            title="Discard Changes"
            @click.stop="handleDiscard(file.path)"
          >
            &#8630;
          </button>
          <button class="action-btn stage" title="Stage" @click.stop="handleStage(file.path)">
            +
          </button>
        </div>
      </div>

      <div
        v-if="gitStatus.staged.length === 0 && gitStatus.unstaged.length === 0"
        class="no-changes"
      >
        No changes
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { GitStatus } from '~/types/api'
import {
  getGitStatus,
  initGitRepo,
  stageFiles,
  unstageFiles,
  discardFiles,
  gitCommit
} from '~/utils/api'

const emit = defineEmits<{
  showDiff: [payload: { path: string; staged: boolean }]
  fileDiscarded: [path: string]
}>()

const gitStatus = ref<GitStatus | null>(null)
const commitMessage = ref('')

const statusLabel = (status: string) => {
  const map: Record<string, string> = {
    modified: 'M',
    added: 'A',
    deleted: 'D',
    renamed: 'R',
    untracked: 'U'
  }
  return map[status] || '?'
}

const refresh = async () => {
  gitStatus.value = await getGitStatus()
}

const handleInit = async () => {
  await initGitRepo()
  await refresh()
}

const handleStage = async (path: string) => {
  await stageFiles([path])
  await refresh()
}

const handleUnstage = async (path: string) => {
  await unstageFiles([path])
  await refresh()
}

const handleDiscard = async (path: string) => {
  if (!confirm(`Discard changes to "${path}"?`)) return
  await discardFiles([path])
  emit('fileDiscarded', path)
  await refresh()
}

const handleCommit = async () => {
  const msg = commitMessage.value.trim()
  if (!msg || !gitStatus.value || gitStatus.value.staged.length === 0) return
  await gitCommit(msg)
  commitMessage.value = ''
  await refresh()
}

onMounted(refresh)

defineExpose({ refresh })
</script>

<style scoped>
.git-panel {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.init-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px 8px;
  color: var(--color-text-muted);
}

.init-btn {
  padding: 6px 16px;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: var(--font-size-sm);
}

.init-btn:hover {
  background: var(--color-primary-hover);
}

.branch-info {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0 8px;
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.branch-icon {
  font-size: var(--font-size-icon);
}

.commit-section {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.commit-input {
  flex: 1;
  padding: 4px 8px;
  background: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: 3px;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  outline: none;
}

.commit-input:focus {
  border-color: var(--color-primary);
}

.commit-btn {
  padding: 4px 12px;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: var(--font-size-sm);
  white-space: nowrap;
}

.commit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.commit-btn:not(:disabled):hover {
  background: var(--color-primary-hover);
}

.file-section {
  margin-bottom: 8px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.count {
  background: var(--color-bg-hover);
  border-radius: 8px;
  padding: 0 6px;
  font-size: var(--font-size-xs);
  font-weight: normal;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 3px 4px;
  border-radius: 3px;
  cursor: pointer;
}

.file-item:hover {
  background: var(--color-bg-hover);
}

.status-badge {
  font-size: var(--font-size-xs);
  font-weight: 600;
  width: 14px;
  text-align: center;
  flex-shrink: 0;
}

.status-badge.modified {
  color: var(--color-git-modified);
}
.status-badge.added {
  color: var(--color-git-added-text);
}
.status-badge.deleted {
  color: var(--color-git-deleted);
}
.status-badge.renamed {
  color: var(--color-git-added-text);
}
.status-badge.untracked {
  color: var(--color-git-added-text);
}

.file-path {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--font-size-sm);
}

.action-btn {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: 1px solid transparent;
  border-radius: 3px;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: var(--font-size-icon);
  font-weight: bold;
  flex-shrink: 0;
  opacity: 0;
}

.file-item:hover .action-btn {
  opacity: 1;
}

.action-btn:hover {
  background: var(--color-bg-input);
  border-color: var(--color-border);
}

.action-btn.discard:hover {
  color: var(--color-git-deleted);
}

.no-changes {
  padding: 24px 8px;
  text-align: center;
  color: var(--color-text-muted);
}
</style>
