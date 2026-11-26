<script setup lang="ts">
import {HelpSection, HelpTopic} from '@emberbox/ui'
import StatusBadge from '../../components/StatusBadge.vue'

/** Help topic: the statuses a vehicle reports, what they mean and which change is allowed. */

/** The statuses a vehicle sets itself, what they mean and from which status they can be reached. */
const STATUSES = [
  {status: '1', text: 'Einsatzbereit über Funk. Erreichbar aus 2, 3, 4 und 8.'},
  {status: '2', text: 'Einsatzbereit auf der Wache. Mit diesem Status tritt ein neues Fahrzeug bei. Erreichbar aus 1.'},
  {status: '3', text: 'Einsatzauftrag übernommen, auf der Anfahrt. Erreichbar aus 1 und 2.'},
  {status: '4', text: 'An der Einsatzstelle eingetroffen. Erreichbar aus 1 und 3.'},
  {status: '7', text: 'Patient aufgenommen, Transport. Nur aus 4.'},
  {status: '8', text: 'Am Transportziel eingetroffen. Nur aus 7.'},
]
</script>

<template>
  <HelpSection title="Status statt Funkspruch">
    <HelpTopic :paragraphs="[
      'Die Ziffern stammen aus dem Funkmeldesystem (FMS) der Feuerwehr und des Rettungsdienstes: Ein Fahrzeug meldet seinen Zustand per Tastendruck, statt ihn per Sprechfunk durchzusagen. Die Leitstelle sieht so jederzeit, welches Fahrzeug frei, unterwegs oder gebunden ist, und der Funkkanal bleibt für das Wichtige frei.',
      'Status Sim übt die Status, die ein Fahrzeug im Einsatzablauf selbst setzt, dazu Sprechwunsch und dringenden Sprechwunsch. Status 6 (außer Dienst) und 9 kommen in der Übung nicht vor; ihre Tasten bleiben ohne Wirkung.',
    ]"/>
  </HelpSection>
  <HelpSection title="Die Status">
    <HelpTopic :paragraphs="[]">
      <template #content>
        <ul class="m-0 flex list-none flex-col gap-2 p-0">
          <li v-for="entry in STATUSES" :key="entry.status" class="flex items-center gap-3">
            <StatusBadge :status="entry.status"/>
            <span class="text-muted">{{ entry.text }}</span>
          </li>
        </ul>
      </template>
    </HelpTopic>
    <HelpTopic title="Ein typischer Einsatz" :paragraphs="[
      'Alarmiert auf der Wache geht das Fahrzeug von 2 auf 3, an der Einsatzstelle auf 4 und nach dem Einsatz auf 1, einsatzbereit über Funk. Zurück auf der Wache meldet es 2. Ein Rettungsmittel mit Patient geht von 4 über 7 nach 8 und danach auf 1.',
    ]"/>
  </HelpSection>
  <HelpSection title="Sprechwunsch (5) und dringender Sprechwunsch (0)">
    <HelpTopic :paragraphs="[
      'Mit 5 bittet ein Fahrzeug die Leitstelle, es anzusprechen. Die 0, in Status Sim Blitz genannt, ist der dringende Sprechwunsch für Lagen, die nicht warten können. Beide ändern den eigentlichen Status nicht, sie stehen daneben, bis die Leitstelle sie erledigt oder das Fahrzeug sie zurücknimmt.',
    ]"/>
  </HelpSection>
</template>
