<template>
  <div v-if="show" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Proof Strategy Suggestions</h3>
        <button @click="$emit('close')" class="close-btn">×</button>
      </div>

      <div class="modal-body">
        <div v-if="loading" class="loading">Generating strategies...</div>
        <div v-else-if="cards.length === 0" class="empty">No strategies generated</div>
        <div v-else class="cards">
          <div v-for="(card, i) in cards" :key="i" class="strategy-card">
            <h4>{{ card.strategy }}</h4>
            <p class="description">{{ card.description }}</p>

            <div v-if="card.required_lemmas.length > 0" class="section">
              <strong>Required Lemmas:</strong>
              <ul>
                <li v-for="lemma in card.required_lemmas" :key="lemma">{{ lemma }}</li>
              </ul>
            </div>

            <div v-if="card.assumptions_to_check.length > 0" class="section">
              <strong>Assumptions to Check:</strong>
              <ul>
                <li v-for="assumption in card.assumptions_to_check" :key="assumption">
                  {{ assumption }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SkeletonCard } from '~/types/api'

defineProps<{
  show: boolean
  cards: SkeletonCard[]
  loading: boolean
}>()

defineEmits<{
  close: []
}>()
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 700px;
  max-height: 80vh;
  width: 90%;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #dee2e6;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 32px;
  line-height: 1;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 32px;
  height: 32px;
}

.close-btn:hover {
  color: #000;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.loading, .empty {
  text-align: center;
  color: #6c757d;
  padding: 40px 20px;
}

.cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.strategy-card {
  padding: 16px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: #f8f9fa;
}

.strategy-card h4 {
  margin: 0 0 8px 0;
  color: #007acc;
  font-size: 16px;
}

.description {
  margin: 0 0 12px 0;
  color: #212529;
  line-height: 1.5;
}

.section {
  margin-top: 12px;
}

.section strong {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #495057;
}

.section ul {
  margin: 0;
  padding-left: 20px;
}

.section li {
  margin: 4px 0;
  font-size: 14px;
  color: #212529;
}
</style>
