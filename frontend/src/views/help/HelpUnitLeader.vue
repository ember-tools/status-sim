<script setup lang="ts">
import {HelpSection, HelpTopic} from '@emberbox/ui'
import UnitLeaderVehicleCard from '../../components/UnitLeaderVehicleCard.vue'
import {exampleVehicle} from '../../helpExamples'

/** Help topic: working as a unit leader. */

const unitLeaderExample = exampleVehicle({status: '3', claimed_by: 'ZF Müller', radio_channel: '401', next_todo: 'SF'})
</script>

<template>
  <HelpSection title="Fahrzeuge übernehmen und anfordern">
    <HelpTopic mockup="Ein übernommenes Fahrzeug, bei dem der Staffelführer als Nächstes spricht" :paragraphs="[
      'Der Staffelführer übernimmt die Fahrzeuge, die er führt. Nur übernommene Fahrzeuge kann er anfordern.',
      'Vorher trägt er seinen Funkkanal ein. „Anfrage“ schickt dem Fahrzeug die Aufforderung, auf diesen Kanal zu wechseln. Bestätigt das Fahrzeug, steht dort „Spricht“; „Fertig“ schließt das Gespräch ab.',
    ]">
      <UnitLeaderVehicleCard :car="unitLeaderExample" code="E5F6A7B8" sf-name="ZF Müller"/>
    </HelpTopic>
  </HelpSection>
  <HelpSection title="Szenario und Nachrichten">
    <HelpTopic :paragraphs="[
      'Aufgeklappt zeigt ein Fahrzeug die Checkliste seines Szenarios, die Nachrichten und eigene Notizen des Staffelführers. Fahrzeuge, bei denen er als Nächstes spricht, stehen im Bereich „Aktion erforderlich (SF)“ ganz oben.',
      'Während ein Fahrzeug mit dem Staffelführer spricht, sieht die Leitstelle, die es übernommen hat, es im Bereich „Gespräch mit Staffelführer“ und weiß, dass es auf ihrem Kanal gerade nicht erreichbar ist.',
    ]"/>
  </HelpSection>
</template>
