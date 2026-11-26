<script setup lang="ts">
import {useHead} from '@unhead/vue'
import {computed, onMounted, ref, watch} from 'vue'
import statusSoundUrl from '../assets/fns_status_1.mp3'
import ChatLog from '../components/ChatLog.vue'
import MissingExercise from '../components/MissingExercise.vue'
import StatusKeypad from '../components/StatusKeypad.vue'
import {useAction} from '../composables/useAction'
import {useExercisePoll} from '../composables/useExercisePoll'
import {vehicleAction, vehicleInfo} from '../exercise'

/**
 * A vehicle of an exercise: the status keypad, the channels of dispatch and unit leader, requests of
 * the unit leader, short status messages and the messages from dispatch.
 */
const props = defineProps<{
  code: string
  name: string
}>()

/** The short status messages a vehicle can send with one tap. */
const SHORT_STATUSES = [
  'Lage bestä., Maßn. eing.',
  'Lage bestä., Gef-Abw. eing.',
  'Keine Feststellung, Erk. läuft',
  'Fehlalarm BMA',
  'Müco, 1 C-Rohr, EstuK',
]

const dispatchName = ref('')
const missing = ref(false)
const tab = ref<'short' | 'messages'>('short')
const unread = ref(false)
const lastPressed = ref<string | null>(null)
let statusSound: HTMLAudioElement | undefined

const {state, refresh} = useExercisePoll(props.code, () => props.name)
const {attempt} = useAction()

useHead({title: () => `${props.name} – Status Sim`})

onMounted(async () => {
  statusSound = new Audio(statusSoundUrl)
  statusSound.volume = 0.5
  try {
    dispatchName.value = await vehicleInfo(props.code, props.name)
  } catch {
    missing.value = true
  }
})

const me = computed(() => state.value?.connections.find(car => car.name === props.name))
const notice = computed(() => state.value?.notices[props.name])
const messages = computed(() => [...(state.value?.messages ?? [])].reverse())

const tabs = computed(() => [
  {label: 'Kurzlagemeldung', value: 'short', icon: 'i-lucide-list'},
  {label: 'Nachrichten', value: 'messages', icon: 'i-lucide-message-square', badge: unread.value ? {label: 'Neu', color: 'signal' as const} : undefined},
])

watch(() => messages.value.length, (count, previous) => {
  if (previous > 0 && count > previous && tab.value !== 'messages') unread.value = true
})

watch(tab, value => {
  if (value === 'messages') unread.value = false
})

watch(() => [me.value?.status, me.value?.special], () => {
  lastPressed.value = null
})

async function act(action: string, value?: string): Promise<void> {
  if (await attempt(() => vehicleAction(props.code, props.name, action, value))) refresh()
}

/** Key 9 only clicks, since it is no status of its own. */
function press(key: string): void {
  lastPressed.value = key
  if (statusSound) {
    statusSound.currentTime = 0
    void statusSound.play().catch(() => undefined)
  }
  if (key !== '9') void act('status', key)
}
</script>

<template>
  <MissingExercise v-if="missing" title="Zu diesem Code gibt es keine Übung."/>
  <main v-else class="mx-auto flex w-full max-w-xl flex-col gap-4 px-4 py-6">
    <div class="flex items-center justify-between gap-3">
      <div>
        <p class="eyebrow m-0">Verbunden mit {{ dispatchName || '…' }}</p>
        <h1 class="headline m-0 text-3xl">{{ name }}</h1>
      </div>
      <UButton v-if="!me?.talking_to_sf" color="info" icon="i-lucide-message-circle" @click="act('toggle_sf')">Mit SF sprechen</UButton>
      <UButton v-else color="error" icon="i-lucide-phone-off" @click="act('toggle_sf')">Gespräch beenden</UButton>
    </div>

    <div v-if="me?.ls_radio_channel || me?.sf_radio_channel" class="flex flex-wrap gap-2">
      <UBadge v-if="me?.ls_radio_channel" color="info" variant="soft" size="lg" class="tabular">LS {{ me.ls_claimed_by }}: {{ me.ls_radio_channel }}</UBadge>
      <UBadge v-if="me?.sf_radio_channel" color="success" variant="soft" size="lg" class="tabular">SF {{ me.claimed_by }}: {{ me.sf_radio_channel }}</UBadge>
    </div>

    <div v-if="notice?.status === 'pending'" class="flex animate-pulse flex-col gap-3 rounded-sm bg-signal p-4 text-inverted" role="alert">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <span class="text-lg font-bold uppercase tracking-widest">{{ notice.text }}</span>
        <UButton color="success" size="lg" @click="act('confirm_notice')">Kanal gewechselt</UButton>
      </div>
      <div v-if="me?.radio_channel" class="flex items-center justify-center gap-2 rounded-sm bg-inverted/30 p-2">
        <span class="text-sm font-medium">Neuer Funkkanal:</span>
        <span class="tabular text-xl font-black">{{ me.radio_channel }}</span>
      </div>
    </div>
    <div v-else-if="notice || me?.talking_to_sf" class="flex items-center gap-2.5 rounded-sm bg-success p-4 font-bold uppercase tracking-widest text-inverted">
      <span class="size-3 animate-ping rounded-full bg-current"/>
      <span>Spricht mit Staffelführer</span>
    </div>

    <StatusKeypad :status="me?.status" :special="me?.special" :last-pressed="lastPressed" @press="press"/>

    <UTabs v-model="tab" :items="tabs" :content="false" class="w-full"/>

    <ul v-if="tab === 'short'" class="m-0 flex list-none flex-col overflow-hidden rounded-sm border border-default p-0">
      <li v-for="option in SHORT_STATUSES" :key="option" class="border-b border-default last:border-0">
        <button type="button" class="w-full px-4 py-3 text-left hover:bg-accented"
                :class="me?.kurzstatus === option ? 'bg-info/15 font-bold text-info' : 'bg-elevated'"
                :aria-pressed="me?.kurzstatus === option" @click="act('kurzstatus', option)">
          {{ option }}
        </button>
      </li>
    </ul>
    <ChatLog v-else :messages="messages" height-class="h-52"/>
  </main>
</template>
