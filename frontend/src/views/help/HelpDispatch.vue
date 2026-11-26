<script setup lang="ts">
import {HelpSection, HelpTopic} from '@emberbox/ui'
import VehicleGroup from '../../components/VehicleGroup.vue'
import VehicleItem from '../../components/VehicleItem.vue'
import {exampleVehicle} from '../../helpExamples'

/** Help topic: working as a dispatcher. */

const dispatchExample = exampleVehicle({status: '4', special: '5', kurzstatus: 'Fehlalarm BMA', ls_claimed_by: 'Disponent 1', next_todo: 'LS'})
</script>

<template>
  <HelpSection title="Name und Funkkanal">
    <HelpTopic :paragraphs="[
      'Mehrere Disponenten können gleichzeitig arbeiten. Jeder gibt rechts oben seinen Namen ein und speichert ihn. Der Funkkanal wird den Fahrzeugen angezeigt, die du übernommen hast.',
      'Name und Kanal stehen danach in der Adresse der Seite. So lässt sich die Leitstelle mit diesen Angaben neu laden oder an einen weiteren Disponenten weitergeben, der dann seinen eigenen Namen einträgt.',
    ]"/>
  </HelpSection>
  <HelpSection title="Fahrzeuge übernehmen">
    <HelpTopic mockup="Ein übernommenes Fahrzeug mit Sprechwunsch und Kurzlagemeldung" :paragraphs="[
      'Jeder Disponent übernimmt die Fahrzeuge, für die er zuständig ist. Fahrzeuge ohne Zuordnung stehen gedämpft im Bereich „Nicht übernommen“ am Ende.',
      'Ein Klick auf Status und Funkrufnamen klappt das Fahrzeug auf. Dort setzt du den Status von Hand (1 bis 4), erstellst oder verwirfst einen Einsatz, hakst die Funksprüche des Szenarios ab, schreibst Nachrichten an das Fahrzeug und hinterlegst Notizen.',
    ]">
      <VehicleItem :car="dispatchExample" admin-code="C9D0E1F2" ls-name="Disponent 1"/>
    </HelpTopic>
  </HelpSection>
  <HelpSection title="Bereiche">
    <HelpTopic mockup="Die Bereiche, nach Dringlichkeit geordnet" :paragraphs="[
      'Ganz oben stehen Fahrzeuge mit Sprechwunsch oder Blitz, nach Wartezeit sortiert. „Aufteilen“ trennt sie in Blitz und Sprechwunsch, „Zusammenfassen“ führt sie wieder zusammen.',
      'Darunter folgen Fahrzeuge im Gespräch mit dem Staffelführer, dann die, bei denen im Szenario die Leitstelle als Nächstes spricht, dann alle übrigen übernommenen Fahrzeuge.',
    ]">
      <div class="flex flex-col gap-2">
        <VehicleGroup title="Sprechwünsche" tone="warning"/>
        <VehicleGroup title="Gespräch mit Staffelführer" tone="signal"/>
        <VehicleGroup title="Aktion erforderlich (LS)" tone="info"/>
        <VehicleGroup title="Alle Fahrzeuge"/>
        <VehicleGroup title="Nicht übernommen" tone="warning" muted/>
      </div>
    </HelpTopic>
  </HelpSection>
</template>
