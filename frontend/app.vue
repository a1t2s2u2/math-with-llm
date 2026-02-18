<template>
  <div class="app">
    <NuxtPage />
  </div>
</template>

<script setup lang="ts">
import { useTheme } from '~/composables/useTheme'

const { initTheme } = useTheme()
initTheme()
</script>

<style>
html,
body,
#__nuxt,
.app {
  height: 100%;
}
</style>
