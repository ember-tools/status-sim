<script setup lang="ts">
/**
 * The status keypad of a vehicle radio: digits 1 to 9 and 0, with `*` and `#` as blanks. The
 * current status lights green, a special status (0 flash, 5 request to talk) amber, and a key just
 * pressed blue until the server answers.
 */
const props = defineProps<{
  status?: string | null
  special?: string | null
  lastPressed?: string | null
}>()

const emit = defineEmits<{ press: [key: string] }>()

const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#']
const BLANKS = new Set(['*', '#'])

const BASE = 'flex aspect-square items-center justify-center rounded-xl border-2 text-lg font-extrabold transition-all'

function keyClass(key: string): string {
  if (props.status === key) return 'border-success bg-success text-inverted'
  if (props.special === key) return 'border-warning bg-warning text-ink'
  if (props.lastPressed === key) return 'border-info bg-info text-inverted'
  return 'border-default bg-elevated text-muted hover:bg-accented'
}
</script>

<template>
  <div class="mx-auto mb-4 grid w-full max-w-[300px] grid-cols-3 gap-2.5">
    <template v-for="key in KEYS" :key="key">
      <span v-if="BLANKS.has(key)" :class="[BASE, 'border-default bg-elevated text-dimmed']" aria-hidden="true">{{ key }}</span>
      <button v-else type="button" :class="[BASE, keyClass(key)]" :aria-pressed="status === key || special === key" @click="emit('press', key)">
        {{ key }}
      </button>
    </template>
  </div>
</template>
