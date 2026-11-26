<script setup lang="ts">
import {computed, inject, ref} from 'vue'
import {get, post} from '../api'
import {REFRESH_KEY} from '../composables/useExercisePoll'
import {exercisePath} from '../exercise'
import {statusBorder} from '../status'
import type {ChecklistState, VehicleStatus} from '../types'
import ScenarioChecklist from './ScenarioChecklist.vue'
import StatusBadge from './StatusBadge.vue'
import Timer from './Timer.vue'
import VehicleChatPanel from './VehicleChatPanel.vue'

/**
 * A vehicle in the dispatch view: status, special status, short status message and who handles it.
 * Opened, it lets the dispatcher set the status, start or discard an incident, tick the scenario and
 * write to the vehicle.
 */
const props = defineProps<{
  car: VehicleStatus
  adminCode: string
  lsName?: string
}>()

const MANUAL_STATUSES = [
  {status: '1', color: 'info'},
  {status: '2', color: 'success'},
  {status: '3', color: 'warning'},
  {status: '4', color: 'error'},
] as const

const refresh = inject(REFRESH_KEY, () => undefined)
const open = ref(false)
const path = computed(() => exercisePath(props.adminCode))
const target = computed(() => ({target_name: props.car.name}))

async function act(action: string, body: object = target.value): Promise<void> {
  await post(`${path.value}/${action}`, body)
  refresh()
}

/**
 * Starts a new incident from a scenario the vehicle has not had yet, discarding the running one.
 * When all are used up, a random one starts again.
 */
async function newIncident(): Promise<void> {
  if (props.car.active_scenario) await post(`${path.value}/scenario/discard`, target.value)
  try {
    const answer = await post<{ scenario: { name: string } }>(`${path.value}/scenario/next`, target.value)
    await post(`${path.value}/scenario/start`, {...target.value, scenario_name: answer.scenario.name})
  } catch {
    const {scenarios} = await get<{ scenarios: { name: string }[] }>(`${path.value}/scenarios`)
    const scenario = scenarios[Math.floor(Math.random() * scenarios.length)]
    if (scenario) await post(`${path.value}/scenario/start`, {...target.value, scenario_name: scenario.name})
  }
  refresh()
}

function updateChecklist(state: ChecklistState): void {
  void act('scenario/update_state', {...target.value, state})
}
</script>

<template>
  <div class="mb-2 flex flex-col rounded-sm border border-l-[5px] border-default bg-default px-3.5 py-2.5" :class="statusBorder(car.status)">
    <div class="flex w-full flex-wrap items-center justify-between gap-2.5">
      <div class="flex flex-wrap items-center gap-2.5">
        <button type="button" class="flex items-center gap-2.5 text-left" :aria-expanded="open" @click="open = !open">
          <StatusBadge :status="car.status"/>
          <span class="max-w-[150px] truncate font-bold" :title="car.name">{{ car.name }}</span>
          <UIcon :name="open ? 'i-lucide-chevron-up' : 'i-lucide-chevron-down'" class="size-4 text-muted"/>
        </button>
        <UBadge v-if="car.next_todo" color="neutral" variant="outline">{{ car.next_todo }}</UBadge>
        <div v-if="car.kurzstatus" class="flex items-center gap-2.5 whitespace-nowrap rounded-sm bg-info/10 px-2.5 py-1 text-sm">
          <span class="font-bold text-info">K:</span>
          <span>{{ car.kurzstatus }}</span>
          <UButton size="xs" color="info" @click="act('clear_kurzstatus')">OK</UButton>
        </div>
        <div v-if="car.talking_to_sf" class="flex items-center gap-2 rounded-sm bg-signal px-2.5 py-1 text-sm font-bold text-white">
          <span>SF</span>
          <Timer :timestamp="car.talking_to_sf_since" :active="true" class="rounded-sm bg-black/20 px-1 !text-white"/>
        </div>
        <span v-if="car.ls_claimed_by" class="text-[10px] uppercase tracking-tight text-muted">LS: {{ car.ls_claimed_by }}</span>
      </div>
      <div class="flex items-center gap-4">
        <template v-if="lsName">
          <UButton v-if="!car.ls_claimed_by" size="xs" @click="act('claim', {...target, sf_name: lsName})">Übernehmen</UButton>
          <UButton v-else-if="car.ls_claimed_by === lsName" size="xs" color="neutral" variant="outline" @click="act('unclaim')">Freigeben</UButton>
        </template>
        <div v-if="car.special" class="flex items-center gap-2 rounded-sm bg-warning px-3 py-1 text-sm font-extrabold uppercase text-ink">
          <span>{{ car.special === '0' ? '0 Blitz' : '5 Spr-W' }}</span>
          <Timer :timestamp="car.special === '0' ? car.last_blitz_update : car.last_sprechwunsch_update" :active="true" class="!text-ink"/>
          <UButton size="xs" color="error" icon="i-lucide-x" aria-label="Sprechwunsch löschen" @click="act('clear_special')"/>
        </div>
        <Timer :timestamp="car.last_status_update" :active="car.is_online"/>
      </div>
    </div>

    <div v-if="open" class="mt-2.5 flex w-full flex-col gap-2.5 border-t border-default pt-2.5">
      <div class="flex w-full gap-2">
        <UButton v-for="manual in MANUAL_STATUSES" :key="manual.status" :color="manual.color" class="tabular flex-1 justify-center font-extrabold"
                 :aria-label="`Status ${manual.status} setzen`" @click="act('set_status', {...target, status: manual.status})">
          {{ manual.status }}
        </UButton>
      </div>
      <div class="flex w-full gap-2">
        <UButton v-if="!car.active_scenario" class="flex-1 justify-center" icon="i-lucide-siren" @click="newIncident">Einsatz erstellen</UButton>
        <UButton v-else class="flex-1 justify-center" color="error" variant="outline" icon="i-lucide-trash-2" @click="act('scenario/discard')">Einsatz verwerfen</UButton>
        <UButton class="flex-1 justify-center" color="neutral" variant="outline" icon="i-lucide-refresh-cw" @click="newIncident">Neuer Einsatz</UButton>
      </div>
      <ScenarioChecklist v-if="car.active_scenario" :scenario="car.active_scenario" :checklist-state="car.checklist_state" @update:state="updateChecklist"/>
      <VehicleChatPanel :code="adminCode" :target-name="car.name" :note="car.note"/>
    </div>
  </div>
</template>
