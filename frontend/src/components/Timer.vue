<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref} from 'vue'
import {formatDuration} from '../utils/format'

/**
 * Time since a moment, ticking every second once mounted. While `active`, it turns from green to
 * amber after a minute and to red after three; inactive it stays grey. Before mounting it shows no
 * time, so a prerendered page and the browser agree.
 */
const props = defineProps<{
  timestamp: number | null
  active: boolean
}>()

const now = ref<number | null>(null)
let interval: ReturnType<typeof setInterval> | undefined

onMounted(() => {
  now.value = Date.now() / 1000
  interval = setInterval(() => {
    now.value = Date.now() / 1000
  }, 1000)
})

onBeforeUnmount(() => clearInterval(interval))

const elapsed = computed(() => (props.timestamp && now.value !== null ? Math.max(0, Math.floor(now.value - props.timestamp)) : 0))

const colorClass = computed(() => {
  if (!props.active) return 'text-dimmed'
  if (elapsed.value < 60) return 'text-success'
  if (elapsed.value < 180) return 'text-warning'
  return 'text-error'
})
</script>

<template>
  <span class="tabular text-[0.8rem]" :class="colorClass">{{ formatDuration(elapsed) }}</span>
</template>
