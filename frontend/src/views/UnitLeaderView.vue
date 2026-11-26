<script setup lang="ts">
import {CodeDisplay} from '@emberbox/ui'
import {useHead} from '@unhead/vue'
import {computed, onMounted, ref} from 'vue'
import {post} from '../api'
import MissingExercise from '../components/MissingExercise.vue'
import UnitLeaderVehicleCard from '../components/UnitLeaderVehicleCard.vue'
import VehicleGroup from '../components/VehicleGroup.vue'
import {useExercisePoll} from '../composables/useExercisePoll'
import {exercisePath, unitLeaderInfo, unitLeaderPath} from '../exercise'
import {joinLink, loadSettings, saveSettings, writeSettingsToAddress} from '../settings'
import type {ChecklistState} from '../types'

/**
 * The unit leader of an exercise: takes over vehicles, asks them to switch to the unit leader's
 * channel and works through their scenarios with them.
 */
const props = defineProps<{ code: string }>()

const saved = loadSettings('unitLeader', props.code)
const query = new URLSearchParams(window.location.search)
const dispatchName = ref('')
const missing = ref(false)
const sfName = ref(query.get('name') || saved.name || '')
const radioChannel = ref(query.get('channel') || saved.channel || '')
const path = unitLeaderPath(props.code)

const {state, connected, refresh} = useExercisePoll(props.code, () => sfName.value || undefined)

useHead({title: () => `Staffelführer ${sfName.value} – Status Sim`})

onMounted(async () => {
  try {
    dispatchName.value = await unitLeaderInfo(props.code)
  } catch {
    missing.value = true
    return
  }
  if (!sfName.value) sfName.value = dispatchName.value
  if (radioChannel.value) await post(`${path}/channel`, {name: sfName.value, channel: radioChannel.value})
})

const vehicles = computed(() => [...(state.value?.connections ?? [])].sort((a, b) => a.last_activity - b.last_activity))
const claimed = computed(() => vehicles.value.filter(car => car.claimed_by === sfName.value))
const unclaimed = computed(() => vehicles.value.filter(car => car.claimed_by !== sfName.value))
const myTurn = computed(() => claimed.value.filter(car => car.next_todo === 'SF'))
const others = computed(() => claimed.value.filter(car => car.next_todo !== 'SF'))

/** The vehicles in the order the unit leader works through them: own turn first, unclaimed last. */
const groups = computed(() => [
  {title: 'Aktion erforderlich (SF)', tone: 'signal', cars: myTurn.value},
  {title: 'Alle Fahrzeuge', tone: 'neutral', cars: others.value},
  {title: 'Nicht übernommen', tone: 'warning', cars: unclaimed.value},
] as const)

/** A new name registers a new unit leader connection, so the page reloads with it. */
function saveName(): void {
  saveSettings('unitLeader', props.code, {name: sfName.value})
  writeSettingsToAddress(sfName.value, radioChannel.value)
  window.location.reload()
}

async function saveChannel(): Promise<void> {
  saveSettings('unitLeader', props.code, {channel: radioChannel.value})
  writeSettingsToAddress(sfName.value, radioChannel.value)
  await post(`${path}/channel`, {name: sfName.value, channel: radioChannel.value})
}

async function act(action: string, carName: string, extra: object = {}): Promise<void> {
  await post(`${path}/${action}`, {target_name: carName, ...extra})
  refresh()
}

function claim(carName: string): void {
  void act('claim', carName, {sf_name: sfName.value})
}

function request(carName: string): void {
  void act('notice', carName, {text: 'Sprechwunsch Staffelführer', sf_name: sfName.value})
}

async function updateChecklist(carName: string, checklist: ChecklistState): Promise<void> {
  await post(`${exercisePath(props.code)}/scenario/update_state`, {target_name: carName, state: checklist})
  refresh()
}
</script>

<template>
  <MissingExercise v-if="missing" title="Zu diesem Code gibt es keine Übung."/>
  <main v-else class="mx-auto flex w-full max-w-[1200px] flex-col gap-5 px-4 py-6 md:px-6">
    <div class="flex flex-wrap items-start justify-between gap-5 rounded-sm border border-default bg-default p-4">
      <div class="flex flex-col gap-3">
        <div>
          <p class="eyebrow m-0">Staffelführer · {{ dispatchName }}</p>
          <h1 class="headline m-0 text-3xl">{{ sfName || '…' }}</h1>
        </div>
        <CodeDisplay title="Staffelführer" :code="code" :link="joinLink(code)" qr/>
      </div>
      <div class="flex flex-col gap-2">
        <form class="flex items-end gap-2" @submit.prevent="saveName">
          <UFormField label="Eigener Name">
            <UInput v-model="sfName" class="w-44"/>
          </UFormField>
          <UButton type="submit" color="neutral" variant="outline">Speichern</UButton>
        </form>
        <form class="flex items-end gap-2" @submit.prevent="saveChannel">
          <UFormField label="Funkkanal">
            <UInput v-model="radioChannel" class="w-44" placeholder="z. B. 401"/>
          </UFormField>
          <UButton type="submit" color="neutral" variant="outline">Kanal setzen</UButton>
        </form>
      </div>
    </div>

    <UAlert v-if="!connected && dispatchName" color="warning" variant="subtle" icon="i-lucide-wifi-off" title="Verbindung unterbrochen …"/>

    <div v-if="unclaimed.length > 0" class="flex items-center gap-3 rounded-sm border border-l-4 border-default border-l-warning bg-default p-3">
      <span class="text-sm font-bold uppercase tracking-wider text-warning">{{ unclaimed.length }} nicht übernommen</span>
      <span class="text-sm text-muted">Fahrzeuge ohne Zuordnung warten auf Übernahme.</span>
    </div>

    <p v-if="vehicles.length === 0" class="m-0 rounded-sm border border-default bg-default p-10 text-center italic text-dimmed">
      Noch keine Fahrzeuge verbunden.
    </p>

    <template v-for="group in groups" :key="group.title">
      <VehicleGroup v-if="group.cars.length > 0" :title="group.title" :tone="group.tone" :muted="group.tone === 'warning'">
        <UnitLeaderVehicleCard v-for="car in group.cars" :key="car.name" :car="car" :code="code" :sf-name="sfName"
                               :notice="state?.notices[car.name]" @claim="claim(car.name)" @release="act('unclaim', car.name)"
                               @request="request(car.name)" @finish="act('acknowledge', car.name)"
                               @update:checklist="checklist => updateChecklist(car.name, checklist)"/>
      </VehicleGroup>
    </template>
  </main>
</template>
