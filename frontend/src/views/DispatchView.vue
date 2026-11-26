<script setup lang="ts">
import {CodeDisplay} from '@emberbox/ui'
import {useHead} from '@unhead/vue'
import {computed, onMounted, provide, ref} from 'vue'
import {post} from '../api'
import MissingExercise from '../components/MissingExercise.vue'
import VehicleGroup from '../components/VehicleGroup.vue'
import VehicleItem from '../components/VehicleItem.vue'
import {useAction} from '../composables/useAction'
import {REFRESH_KEY, useExercisePoll} from '../composables/useExercisePoll'
import {type DispatchInfo, dispatchInfo, exercisePath} from '../exercise'
import {specialSince} from '../status'
import type {VehicleStatus} from '../types'
import {joinLink, loadSettings, saveSettings, writeSettingsToAddress} from '../settings'

/**
 * The dispatch centre of an exercise: the codes to hand out, the dispatcher's name and channel, a
 * message to all vehicles and the vehicles grouped by urgency. Several dispatchers can work in
 * parallel; each takes over the vehicles they handle.
 */
const props = defineProps<{ code: string }>()

const info = ref<DispatchInfo | null>(null)
const missing = ref(false)
const saved = loadSettings('dispatch', props.code)
const query = new URLSearchParams(window.location.search)
const lsName = ref(query.get('name') || saved.name || 'Disponent 1')
const radioChannel = ref(query.get('channel') || saved.channel || '')
const combineRequests = ref(saved.combine ?? true)
const message = ref('')
const path = exercisePath(props.code)

const {state, connected, refresh} = useExercisePoll(props.code, () => lsName.value)
provide(REFRESH_KEY, refresh)
const {attempt} = useAction()

useHead({title: () => (info.value ? `Leitstelle ${info.value.name} – Status Sim` : 'Leitstelle – Status Sim')})

onMounted(async () => {
  try {
    info.value = await dispatchInfo(props.code)
  } catch {
    missing.value = true
    return
  }
  if (radioChannel.value) await attempt(() => post(`${path}/channel`, {name: lsName.value, channel: radioChannel.value}))
})

const vehicles = computed(() => {
  const notices = state.value?.notices ?? {}
  return (state.value?.connections ?? [])
    .map(car => ({...car, talking_to_sf: car.talking_to_sf || notices[car.name]?.status === 'confirmed'}))
    .sort((a, b) => a.last_activity - b.last_activity)
})

const byWait = (a: VehicleStatus, b: VehicleStatus) => specialSince(a) - specialSince(b)
const claimed = computed(() => vehicles.value.filter(car => car.ls_claimed_by === lsName.value))
const unclaimed = computed(() => vehicles.value.filter(car => car.ls_claimed_by !== lsName.value))
const flashes = computed(() => claimed.value.filter(car => car.special === '0').sort(byWait))
const requests = computed(() => claimed.value.filter(car => car.special === '5').sort(byWait))
const allRequests = computed(() => claimed.value.filter(car => car.special === '0' || car.special === '5').sort(byWait))
const withUnitLeader = computed(() => claimed.value.filter(car => car.talking_to_sf && !car.special))
const quiet = computed(() => claimed.value.filter(car => !car.special && !car.talking_to_sf))
const dispatchTurn = computed(() => quiet.value.filter(car => car.next_todo === 'LS'))
const others = computed(() => quiet.value.filter(car => car.next_todo !== 'LS'))

function toggleCombine(): void {
  combineRequests.value = !combineRequests.value
  saveSettings('dispatch', props.code, {combine: combineRequests.value})
}

async function sendToAll(): Promise<void> {
  if (!message.value) return
  if (!await attempt(() => post(`${path}/message`, {message: message.value}))) return
  message.value = ''
  refresh()
}

/** A new name registers a new dispatcher connection, so the page reloads with it. */
function saveName(): void {
  saveSettings('dispatch', props.code, {name: lsName.value})
  writeSettingsToAddress(lsName.value, radioChannel.value)
  window.location.reload()
}

async function saveChannel(): Promise<void> {
  saveSettings('dispatch', props.code, {channel: radioChannel.value})
  writeSettingsToAddress(lsName.value, radioChannel.value)
  if (await attempt(() => post(`${path}/channel`, {name: lsName.value, channel: radioChannel.value}))) refresh()
}
</script>

<template>
  <MissingExercise v-if="missing" title="Zu diesem Code gibt es keine Leitstelle."/>
  <main v-else class="mx-auto flex w-full max-w-[1200px] flex-col gap-5 px-4 py-6 md:px-6">
    <div class="flex flex-wrap items-start justify-between gap-5 rounded-sm border border-default bg-default p-4">
      <div class="flex min-w-[250px] flex-1 flex-col gap-3">
        <div>
          <p class="eyebrow m-0">Leitstelle</p>
          <h1 class="headline m-0 text-3xl">{{ info?.name ?? '…' }}</h1>
        </div>
        <div class="flex flex-wrap gap-3">
          <CodeDisplay v-if="info" title="Fahrzeuge" :code="info.vehicle_code" :link="joinLink(info.vehicle_code)" qr/>
          <CodeDisplay v-if="info" title="Staffelführer" :code="info.staffelfuehrer_code" :link="joinLink(info.staffelfuehrer_code)" qr/>
          <CodeDisplay title="Leitstelle" :code="code" :link="joinLink(code)" hidden/>
        </div>
      </div>
      <div class="flex flex-col gap-2">
        <form class="flex items-end gap-2" @submit.prevent="saveName">
          <UFormField label="Disponent">
            <UInput v-model="lsName" class="w-44" placeholder="Disponentenname"/>
          </UFormField>
          <UButton type="submit" color="neutral" variant="outline">Speichern</UButton>
        </form>
        <form class="flex items-end gap-2" @submit.prevent="saveChannel">
          <UFormField label="Funkkanal">
            <UInput v-model="radioChannel" class="w-44" placeholder="z. B. 501"/>
          </UFormField>
          <UButton type="submit" color="neutral" variant="outline">Kanal setzen</UButton>
        </form>
      </div>
    </div>

    <UAlert v-if="!connected && info" color="warning" variant="subtle" icon="i-lucide-wifi-off" title="Verbindung unterbrochen …"/>

    <form class="flex gap-2 rounded-sm border border-default bg-default p-4" @submit.prevent="sendToAll">
      <UInput v-model="message" placeholder="Nachricht an alle Fahrzeuge" class="flex-1" aria-label="Nachricht an alle Fahrzeuge" required/>
      <UButton type="submit" icon="i-lucide-send">Senden</UButton>
    </form>

    <div v-if="unclaimed.length > 0" class="flex items-center gap-3 rounded-sm border border-l-4 border-default border-l-warning bg-default p-3">
      <span class="text-sm font-bold uppercase tracking-wider text-warning">{{ unclaimed.length }} nicht übernommen</span>
      <span class="text-sm text-muted">Fahrzeuge ohne Zuordnung warten auf Übernahme.</span>
    </div>

    <template v-if="combineRequests">
      <VehicleGroup v-if="allRequests.length > 0" title="Sprechwünsche" tone="warning">
        <template #action>
          <UButton size="xs" color="neutral" variant="outline" @click="toggleCombine">Aufteilen</UButton>
        </template>
        <VehicleItem v-for="car in allRequests" :key="car.name" :car="car" :admin-code="code" :ls-name="lsName"/>
      </VehicleGroup>
    </template>
    <template v-else>
      <VehicleGroup v-if="flashes.length > 0" title="0 Blitz" tone="signal">
        <template #action>
          <UButton size="xs" color="neutral" variant="outline" @click="toggleCombine">Zusammenfassen</UButton>
        </template>
        <VehicleItem v-for="car in flashes" :key="car.name" :car="car" :admin-code="code" :ls-name="lsName"/>
      </VehicleGroup>
      <VehicleGroup v-if="requests.length > 0" title="5 Sprechwunsch" tone="warning">
        <template v-if="flashes.length === 0" #action>
          <UButton size="xs" color="neutral" variant="outline" @click="toggleCombine">Zusammenfassen</UButton>
        </template>
        <VehicleItem v-for="car in requests" :key="car.name" :car="car" :admin-code="code" :ls-name="lsName"/>
      </VehicleGroup>
    </template>

    <VehicleGroup v-if="withUnitLeader.length > 0" title="Gespräch mit Staffelführer" tone="signal">
      <VehicleItem v-for="car in withUnitLeader" :key="car.name" :car="car" :admin-code="code" :ls-name="lsName"/>
    </VehicleGroup>

    <VehicleGroup v-if="dispatchTurn.length > 0" title="Aktion erforderlich (LS)" tone="info">
      <VehicleItem v-for="car in dispatchTurn" :key="car.name" :car="car" :admin-code="code" :ls-name="lsName"/>
    </VehicleGroup>

    <VehicleGroup title="Alle Fahrzeuge">
      <p v-if="others.length === 0" class="m-0 italic text-dimmed">
        {{ claimed.length === 0 ? 'Keine Fahrzeuge übernommen.' : 'Keine weiteren Fahrzeuge.' }}
      </p>
      <VehicleItem v-for="car in others" :key="car.name" :car="car" :admin-code="code" :ls-name="lsName"/>
    </VehicleGroup>

    <VehicleGroup v-if="unclaimed.length > 0" title="Nicht übernommen" tone="warning" muted>
      <VehicleItem v-for="car in unclaimed" :key="car.name" :car="car" :admin-code="code" :ls-name="lsName"/>
    </VehicleGroup>
  </main>
</template>
