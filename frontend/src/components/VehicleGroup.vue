<script setup lang="ts">
/**
 * A group of vehicles under a coloured top edge, such as the requests to talk or the vehicles nobody
 * has taken over. `tone` picks the colour of edge and title.
 */
withDefaults(defineProps<{
  title: string
  tone?: 'neutral' | 'warning' | 'signal' | 'info'
  muted?: boolean
}>(), {tone: 'neutral', muted: false})

const TONES = {
  neutral: 'border-t-default text-highlighted',
  warning: 'border-t-4 border-t-warning text-warning',
  signal: 'border-t-4 border-t-signal text-signal',
  info: 'border-t-4 border-t-info text-info',
} as const
</script>

<template>
  <section class="rounded-sm border border-default bg-muted p-4" :class="[TONES[tone], muted ? 'opacity-70' : '']">
    <div class="mb-4 flex items-center justify-between gap-2 border-b border-default pb-2">
      <h2 class="m-0 text-sm font-bold uppercase tracking-widest">{{ title }}</h2>
      <slot name="action"/>
    </div>
    <div class="text-default">
      <slot/>
    </div>
  </section>
</template>
