<script setup lang="ts">
import {ref} from 'vue'
import type {ChatMessage} from '../types'
import {formatRelativeTime} from '../utils/format'

/** The messages between dispatch or unit leader and a vehicle, in the order given. */
withDefaults(defineProps<{
  messages: ChatMessage[]
  loading?: boolean
  heightClass?: string
}>(), {
  loading: false,
  heightClass: 'h-40',
})

const root = ref<HTMLDivElement | null>(null)

/** Scrolls to the newest message. */
function scrollToEnd(): void {
  if (root.value) root.value.scrollTop = root.value.scrollHeight
}

defineExpose({scrollToEnd})
</script>

<template>
  <div ref="root" class="flex flex-col overflow-y-auto rounded-sm border border-default bg-default" :class="heightClass">
    <p v-if="loading" class="m-auto text-sm italic text-dimmed">Nachrichten werden geladen …</p>
    <p v-else-if="messages.length === 0" class="m-auto text-sm italic text-dimmed">Keine Nachrichten</p>
    <ul v-else class="m-0 list-none p-0">
      <li v-for="(message, index) in messages" :key="index" class="flex items-start gap-2.5 border-b border-muted px-3 py-2 last:border-0">
        <UBadge :color="message.sender === 'LS' ? 'info' : 'signal'" variant="solid" size="sm" class="mt-0.5">{{ message.sender }}</UBadge>
        <span class="mt-0.5 min-w-16 whitespace-nowrap text-xs text-dimmed">{{ formatRelativeTime(message.timestamp) }}</span>
        <span class="grow break-all">{{ message.text }}</span>
      </li>
    </ul>
  </div>
</template>
