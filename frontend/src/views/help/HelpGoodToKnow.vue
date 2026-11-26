<script setup lang="ts">
import {HelpSection, HelpTopic} from '@emberbox/ui'

/** Help topic: connection, browser storage and how long an exercise is kept. */
</script>

<template>
  <HelpSection title="Verbindung">
    <HelpTopic :paragraphs="[
      'Jede Seite fragt den Server alle zwei Sekunden nach dem neuesten Stand, nach einer eigenen Aktion sofort. Liegt die Seite im Hintergrund, fragt sie alle zehn Sekunden; manche Browser bremsen Seiten, die länger im Hintergrund liegen, auf etwa einmal pro Minute oder halten sie bei gesperrtem Bildschirm ganz an.',
      'Ein Fahrzeug gilt als verbunden, solange seine Seite den Server erreicht. Nach 15 Sekunden ohne Kontakt erscheint es als getrennt, nach fünf Minuten verschwindet es aus der Übung. Meldet es sich danach wieder, tritt es neu mit Status 2 bei; Status und offene Sprechwünsche sind dann verloren.',
    ]"/>
  </HelpSection>
  <HelpSection title="Speicher im Browser">
    <HelpTopic :paragraphs="[
      'Im Browser merkt sich Status Sim je Übung den Namen und Funkkanal von Leitstelle und Staffelführer und ob die Leitstelle Sprechwünsche zusammenfasst. Diese Angaben werden nach sieben Tagen verworfen.',
      'Hell und dunkel wechselst du mit dem Knopf rechts im Kopf der Seite.',
    ]"/>
  </HelpSection>
  <HelpSection title="Löschfrist">
    <HelpTopic :paragraphs="[
      'Eine Übung wird sieben Tage nach dem letzten Zugriff vollständig gelöscht, mit allen Fahrzeugen, Nachrichten und Notizen. Solange jemand sie geöffnet hat, bleibt sie erhalten.',
    ]"/>
  </HelpSection>
</template>
