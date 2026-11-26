<script setup lang="ts">
import {HelpSection, HelpTopic} from '@emberbox/ui'

/** Help topic: how scenarios turn into the radio messages of an incident. */
</script>

<template>
  <HelpSection title="Einsatz erstellen">
    <HelpTopic :paragraphs="[
      '„Einsatz erstellen“ in der Leitstelle wählt ein Szenario, das das Fahrzeug noch nicht hatte, und erzeugt daraus die Funksprüche für Alarmierung, Anfahrt, Lagemeldungen und Abschluss, mit dem Namen der Leitstelle, dem Funkrufnamen und einer Einsatznummer.',
      'Ist ein Szenario durch, startet „Neuer Einsatz“ das nächste. Sind alle Szenarien verbraucht, beginnt die Auswahl von vorn.',
    ]"/>
  </HelpSection>
  <HelpSection title="Die Checkliste">
    <HelpTopic :paragraphs="[
      'Jeder Funkspruch nennt, wer spricht: LS für die Leitstelle, SF für den Staffelführer, FZ für das Fahrzeug. Leitstelle und Staffelführer sehen dieselbe Checkliste und haken gemeinsam ab; „Alle erledigt“ hakt einen ganzen Schritt ab.',
      'Wer als Nächstes spricht, bestimmt, in welchem Bereich das Fahrzeug steht: Bei LS rückt es bei der Leitstelle, die es übernommen hat, nach oben, bei SF beim Staffelführer. So bleibt in einer großen Übung sichtbar, wo gerade jemand auf eine Antwort wartet.',
    ]"/>
  </HelpSection>
</template>
