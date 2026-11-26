<script setup lang="ts">
import {ref} from 'vue'
import {statusBorder} from '../status'
import type {ChecklistState, Notice, VehicleStatus} from '../types'
import ScenarioChecklist from './ScenarioChecklist.vue'
import StatusBadge from './StatusBadge.vue'
import Timer from './Timer.vue'
import VehicleChatPanel from './VehicleChatPanel.vue'

/**
 * A vehicle in the unit leader view: status, channel, the state of a request to switch channels and
 * who handles it. Opened, it shows the scenario checklist, messages and the note.
 */
defineProps<{
  car: VehicleStatus
  code: string
  sfName: string
  notice?: Notice
}>()

const emit = defineEmits<{
  claim: []
  release: []
  request: []
  finish: []
  'update:checklist': [state: ChecklistState]
}>()

const open = ref(false)
</script>

<template>
  <div class="mb-2 flex flex-col rounded-sm border border-l-[5px] border-default bg-default px-4 py-3" :class="statusBorder(car.status)">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-wrap items-center gap-4">
        <button type="button" class="flex items-center gap-3 text-left" :aria-expanded="open" @click="open = !open">
          <span class="flex min-w-[120px] flex-col">
            <span class="text-lg font-bold">{{ car.name }}</span>
            <span v-if="car.claimed_by" class="text-[10px] uppercase tracking-tight text-muted">Übernommen von: {{ car.claimed_by }}</span>
          </span>
          <UIcon :name="open ? 'i-lucide-chevron-up' : 'i-lucide-chevron-down'" class="size-4 text-muted"/>
        </button>
        <UBadge v-if="car.next_todo" color="neutral" variant="outline">Als Nächstes: {{ car.next_todo }}</UBadge>
        <span class="flex items-center gap-2">
          <StatusBadge :status="car.status"/>
          <Timer :timestamp="car.last_status_update" :active="car.is_online"/>
        </span>
        <UBadge v-if="car.radio_channel" color="info" variant="soft" class="tabular">Kanal {{ car.radio_channel }}</UBadge>
        <div v-if="notice" class="flex items-center gap-2 rounded-sm border px-3 py-1 text-sm font-bold"
             :class="notice.status === 'confirmed' ? 'border-success bg-success/10 text-success' : 'border-warning bg-warning/10 text-warning'">
          <span>{{ notice.status === 'confirmed' ? 'Spricht' : 'Angefragt' }}</span>
          <UButton v-if="notice.status === 'confirmed'" size="xs" color="success" @click="emit('finish')">Fertig</UButton>
        </div>
        <div v-if="car.talking_to_sf" class="flex items-center gap-2 rounded-sm bg-signal px-2.5 py-1 text-sm font-bold text-white">
          <span>Aktiv</span>
          <Timer :timestamp="car.talking_to_sf_since" :active="true" class="rounded-sm bg-black/20 px-1 !text-white"/>
        </div>
      </div>
      <div class="flex gap-2">
        <UButton v-if="!car.claimed_by" size="sm" @click="emit('claim')">Übernehmen</UButton>
        <UButton v-else-if="car.claimed_by === sfName" size="sm" color="neutral" variant="outline" @click="emit('release')">Freigeben</UButton>
        <UButton v-if="!car.talking_to_sf && car.claimed_by === sfName" size="sm" color="signal" icon="i-lucide-radio-tower" @click="emit('request')">Anfrage</UButton>
      </div>
    </div>
    <div v-if="open" class="mt-2.5 flex flex-col gap-3 border-t border-default pt-2.5">
      <ScenarioChecklist v-if="car.active_scenario" :scenario="car.active_scenario" :checklist-state="car.checklist_state"
                         @update:state="state => emit('update:checklist', state)"/>
      <VehicleChatPanel :code="code" :target-name="car.name" :note="car.sf_note"/>
    </div>
  </div>
</template>
