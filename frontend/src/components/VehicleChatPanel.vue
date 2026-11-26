<script setup lang="ts">
import {nextTick, onBeforeUnmount, onMounted, ref, watch} from 'vue'
import {get, post} from '../api'
import {exercisePath} from '../exercise'
import type {ChatMessage} from '../types'
import ChatLog from './ChatLog.vue'

/**
 * The messages with one vehicle and a note about it, for the dispatch and the unit leader view. The
 * messages are reloaded every three seconds while the panel is open; the note is saved when the
 * field loses focus.
 */
const props = defineProps<{
  code: string
  targetName: string
  note: string
}>()

const CHAT_INTERVAL_MS = 3000

const message = ref('')
const note = ref(props.note)
const log = ref<InstanceType<typeof ChatLog> | null>(null)
const messages = ref<ChatMessage[]>([])
const loading = ref(false)
let timer: ReturnType<typeof setInterval> | undefined

async function loadMessages(): Promise<void> {
  try {
    const answer = await get<{ messages: ChatMessage[] }>(`${exercisePath(props.code)}/chat_history`, {target_name: props.targetName})
    messages.value = answer.messages
    await nextTick()
    log.value?.scrollToEnd()
  } catch {
    return
  }
}

watch(() => props.note, value => {
  note.value = value
})

onMounted(() => {
  loading.value = true
  void loadMessages().finally(() => {
    loading.value = false
  })
  timer = setInterval(() => void loadMessages(), CHAT_INTERVAL_MS)
})

onBeforeUnmount(() => clearInterval(timer))

async function send(): Promise<void> {
  if (!message.value.trim()) return
  await post(`${exercisePath(props.code)}/message`, {message: message.value, target_name: props.targetName})
  message.value = ''
  await loadMessages()
}

async function saveNote(): Promise<void> {
  await post(`${exercisePath(props.code)}/update_note`, {target_name: props.targetName, note: note.value})
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <ChatLog ref="log" :messages="messages" :loading="loading"/>
    <form class="flex items-center gap-1.5" @submit.prevent="send">
      <UInput v-model="message" placeholder="Nachricht …" class="flex-1" aria-label="Nachricht an das Fahrzeug"/>
      <UButton type="submit" color="neutral" variant="outline" icon="i-lucide-send">Senden</UButton>
    </form>
    <UFormField label="Notizen">
      <UTextarea v-model="note" autoresize :rows="2" class="w-full" @blur="saveNote"/>
    </UFormField>
  </div>
</template>
