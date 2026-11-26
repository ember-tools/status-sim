<script setup lang="ts">
import {HelpSection, HelpTopic} from '@emberbox/ui'
import StatusKeypad from '../../components/StatusKeypad.vue'

/** Help topic: what a vehicle does during the exercise. */
</script>

<template>
  <HelpSection title="Statusfeld">
    <HelpTopic mockup="Status 2 ist gesetzt, ein Sprechwunsch (5) ist offen" :paragraphs="[
      'Drücke eine Ziffer, um den Status zu wechseln. Der aktuelle Status leuchtet grün, ein offener Sprechwunsch oder Blitz gelb. Bis der Server antwortet, leuchtet die gedrückte Taste blau.',
      'Nicht jeder Status ist aus jedem anderen erreichbar; ein unzulässiger Wechsel wird ignoriert. Welche Wechsel erlaubt sind, steht unter „Die Status im Überblick“.',
    ]">
      <div class="max-w-[220px]">
        <StatusKeypad status="2" special="5"/>
      </div>
    </HelpTopic>
  </HelpSection>
  <HelpSection title="Sprechwunsch und Blitz">
    <HelpTopic :paragraphs="[
      'Taste 5 meldet einen Sprechwunsch, Taste 0 einen dringenden Sprechwunsch (Blitz). Beide erscheinen bei der Leitstelle, die das Fahrzeug übernommen hat, sofort ganz oben. Ein zweiter Druck auf dieselbe Taste nimmt die Meldung zurück; die Leitstelle kann sie ebenfalls löschen.',
    ]"/>
  </HelpSection>
  <HelpSection title="Kurzlagemeldung und Nachrichten">
    <HelpTopic :paragraphs="[
      'Unter dem Statusfeld wählst du eine vorbereitete Kurzlagemeldung. Die Leitstelle sieht sie am Fahrzeug und bestätigt sie mit „OK“.',
      'Im Reiter „Nachrichten“ stehen die Nachrichten von Leitstelle und Staffelführer, die neueste oben. Kommt eine neue, zeigt der Reiter „Neu“.',
    ]"/>
  </HelpSection>
  <HelpSection title="Mit dem Staffelführer sprechen">
    <HelpTopic :paragraphs="[
      '„Mit SF sprechen“ zeigt der Leitstelle, dass das Fahrzeug gerade mit dem Staffelführer spricht und auf dem Kanal der Leitstelle nicht erreichbar ist. „Gespräch beenden“ hebt das wieder auf.',
      'Fordert dich der Staffelführer an, blinkt eine rote Meldung mit seinem Funkkanal. Wechsle den Kanal und bestätige mit „Kanal gewechselt“.',
    ]"/>
  </HelpSection>
</template>
