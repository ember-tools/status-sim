<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref, watch} from 'vue'
import type {ActiveScenario, ChecklistState, RadioEntry, ScenarioIncident} from '../types'

/**
 * The radio messages of a vehicle's scenario as a checklist, by incident and step. Expanded parts
 * and ticked messages are shared through the server, so everyone looking at the vehicle sees the
 * same state; every change is emitted as the complete new state.
 */
const props = defineProps<{
  scenario: ActiveScenario
  checklistState?: ChecklistState | null
}>()

const emit = defineEmits<{ 'update:state': [state: ChecklistState] }>()

/** How the scenario files name the step types. */
const STEP_LABELS: Record<string, string> = {
  eigenunfall: 'Eigenunfall',
  neue_taetigkeit_mit_fzn: 'Neue Tätigkeit (FZN)',
  neue_taetigkeit_ohne_fzn: 'Neue Tätigkeit',
  einsatzstellenkorrektur: 'Einsatzstellenkorrektur',
  identische_einsatzstelle_anfrage: 'Identische Einsatzstelle Anfrage',
  ankommen: 'Ankunft am Einsatzort',
  kurzlagemeldung_fms: 'Kurzlagemeldung FMS',
  kurzlagemeldung: 'Kurzlagemeldung',
  lagemeldung: 'Lagemeldung',
  ohne_lagemeldung: 'Abschluss ohne Lagemeldung',
  nachalarmierung: 'Nachalarmierung',
  nachalarmierung_fahrzeuge: 'Nachalarmierung Fahrzeuge',
  fehlalarm_lagemeldung: 'Fehlalarm BMA',
}

const ACTOR_COLORS: Record<RadioEntry['actor'], string> = {
  LS: 'text-info',
  SF: 'text-signal',
  FZ: 'text-success',
}

const CLOCK_INTERVAL_MS = 10_000

const expandedIncidents = ref<Record<string, boolean>>({...props.checklistState?.expanded_einsaetze})
const expandedSteps = ref<Record<string, boolean>>({...props.checklistState?.expanded_schritte})
const checked = computed(() => props.checklistState?.checked_entries ?? {})
const clock = ref('')
let clockTimer: ReturnType<typeof setInterval> | undefined

watch(() => props.checklistState, state => {
  if (!state) return
  expandedIncidents.value = {...state.expanded_einsaetze}
  expandedSteps.value = {...state.expanded_schritte}
}, {deep: true})

function updateClock(): void {
  const now = new Date()
  clock.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  updateClock()
  clockTimer = setInterval(updateClock, CLOCK_INTERVAL_MS)
})

onBeforeUnmount(() => clearInterval(clockTimer))

const progress = computed(() => {
  const total = props.scenario.generated_entries.length
  const done = Object.values(checked.value).filter(Boolean).length
  return {done, total, percent: total > 0 ? Math.round((done / total) * 100) : 0}
})

function emitState(change: Partial<ChecklistState>): void {
  emit('update:state', {
    expanded_einsaetze: {...expandedIncidents.value},
    expanded_schritte: {...expandedSteps.value},
    checked_entries: {...checked.value},
    ...change,
  })
}

function toggleIncident(incident: number): void {
  expandedIncidents.value[incident] = !expandedIncidents.value[incident]
  emitState({expanded_einsaetze: {...expandedIncidents.value}})
}

function toggleStep(incident: number, step: number): void {
  const key = `${incident}-${step}`
  expandedSteps.value[key] = !expandedSteps.value[key]
  emitState({expanded_schritte: {...expandedSteps.value}})
}

function toggleEntry(incident: number, step: number, entry: number): void {
  const key = `${incident}-${step}-${entry}`
  emitState({checked_entries: {...checked.value, [key]: !checked.value[key]}})
}

function markStepDone(incident: number, step: number): void {
  const next = {...checked.value}
  entriesOf(incident, step).forEach((_, entry) => {
    next[`${incident}-${step}-${entry}`] = true
  })
  emitState({checked_entries: next})
}

/**
 * The radio messages of one step. The generated messages carry their incident and step as a
 * `[[E<n>]][[S<n>]]` prefix, which is cut off here, and `<time>` stands for the current time.
 */
function entriesOf(incident: number, step: number): RadioEntry[] {
  const prefix = `[[E${incident}]][[S${step}]]`
  return props.scenario.generated_entries
    .filter(entry => entry.message?.startsWith(prefix))
    .map(entry => ({...entry, message: (entry.message ?? '').replace(prefix, '').replace('<time>', clock.value)}))
}

/** Step 0 is the alerting, the others are the steps of the scenario file. */
function stepLabel(incident: ScenarioIncident, step: number): string {
  if (step === 0) return 'Alarmierung'
  const type = incident.schritte[step - 1]?.typ
  if (!type) return `Schritt ${step}`
  return STEP_LABELS[type] ?? type
}

function stepProgress(incident: number, step: number): string {
  const entries = entriesOf(incident, step)
  const done = entries.filter((_, entry) => checked.value[`${incident}-${step}-${entry}`]).length
  return `${done}/${entries.length}`
}

/** The step numbers of an incident, starting with the alerting as 0. */
function stepsOf(incident: ScenarioIncident): number[] {
  return Array.from({length: incident.schritte.length + 1}, (_, step) => step)
}
</script>

<template>
  <div class="overflow-hidden rounded-sm border border-default bg-muted">
    <div class="flex items-center justify-between gap-2 border-b border-default bg-elevated px-3 py-2">
      <span class="section-title">Szenario: {{ scenario.name }}</span>
      <UBadge color="neutral" variant="outline" class="tabular">{{ progress.done }}/{{ progress.total }} ({{ progress.percent }} %)</UBadge>
    </div>
    <div class="flex flex-col gap-4 p-3">
      <p class="m-0 text-sm italic text-muted">{{ scenario.beschreibung }}</p>
      <div v-for="(incident, incidentIndex) in scenario.einsaetze" :key="incidentIndex" class="flex flex-col gap-2">
        <button type="button" class="flex items-center justify-between rounded-sm border border-default bg-elevated p-2 text-left hover:bg-accented"
                :aria-expanded="!!expandedIncidents[incidentIndex]" @click="toggleIncident(incidentIndex)">
          <span class="flex flex-col">
            <span class="font-bold text-highlighted">{{ incident.stichwort }}</span>
            <span class="text-sm text-muted">{{ incident.adresse }}, {{ incident.ortsteil }}</span>
          </span>
          <UIcon :name="expandedIncidents[incidentIndex] ? 'i-lucide-chevron-up' : 'i-lucide-chevron-down'" class="size-4"/>
        </button>
        <div v-if="expandedIncidents[incidentIndex]" class="ml-3 flex flex-col gap-2 border-l-2 border-default pl-3">
          <div v-for="step in stepsOf(incident)" :key="step" class="flex flex-col gap-1">
            <div class="flex items-center justify-between gap-2 rounded-sm border border-default bg-default p-2">
              <button type="button" class="flex flex-1 items-center justify-between gap-2 text-left" :aria-expanded="!!expandedSteps[`${incidentIndex}-${step}`]"
                      @click="toggleStep(incidentIndex, step)">
                <span class="flex items-center gap-2">
                  <span class="text-sm font-bold">{{ stepLabel(incident, step) }}</span>
                  <UBadge color="neutral" variant="soft" size="sm" class="tabular">{{ stepProgress(incidentIndex, step) }}</UBadge>
                </span>
                <UIcon :name="expandedSteps[`${incidentIndex}-${step}`] ? 'i-lucide-chevron-up' : 'i-lucide-chevron-down'" class="size-4"/>
              </button>
              <UButton size="xs" color="neutral" variant="soft" icon="i-lucide-check-check" @click="markStepDone(incidentIndex, step)">Alle erledigt</UButton>
            </div>
            <ul v-if="expandedSteps[`${incidentIndex}-${step}`]" class="m-0 ml-2 flex list-none flex-col gap-1 p-0">
              <li v-for="(entry, entryIndex) in entriesOf(incidentIndex, step)" :key="entryIndex"
                  class="flex items-start gap-2 rounded-sm border border-muted p-1.5">
                <UCheckbox :model-value="!!checked[`${incidentIndex}-${step}-${entryIndex}`]" class="mt-0.5"
                           :aria-label="`Funkspruch ${entryIndex + 1} erledigt`" @update:model-value="toggleEntry(incidentIndex, step, entryIndex)"/>
                <div class="min-w-0 flex-1">
                  <div class="mb-0.5 flex items-center gap-2">
                    <span class="text-sm font-bold" :class="ACTOR_COLORS[entry.actor]">{{ entry.actor }}</span>
                    <UBadge v-if="entry.status" color="neutral" variant="solid" size="sm">Status {{ entry.status }}</UBadge>
                  </div>
                  <p class="m-0 text-sm leading-relaxed" :class="checked[`${incidentIndex}-${step}-${entryIndex}`] ? 'text-dimmed line-through' : 'text-default'">
                    {{ entry.message }}
                  </p>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
