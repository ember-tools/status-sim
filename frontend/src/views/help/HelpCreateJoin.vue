<script setup lang="ts">
import {CodeDisplay, HelpSection, HelpTopic} from '@emberbox/ui'

/** Help topic: creating an exercise, handing out its codes and joining it. */
</script>

<template>
  <HelpSection title="Übung anlegen">
    <HelpTopic :paragraphs="[
      'Auf der Startseite den Namen der Leitstelle eingeben, etwa „Florian Berlin“, und „Leitstelle erstellen“ wählen. Der Name erscheint später in den Funksprüchen der Szenarien.',
      'Eine Übung hat drei Codes: den der Leitstelle, den für die Fahrzeuge und den für die Staffelführer. Wer einen Code kennt, kann mit dieser Rolle beitreten. Gib den Leitstellen-Code deshalb nur an weitere Disponenten weiter.',
    ]"/>
  </HelpSection>
  <HelpSection title="Codes verteilen">
    <HelpTopic mockup="Die Codes im Kopf der Leitstelle" :paragraphs="[
      'Oben in der Leitstelle stehen die Codes für Fahrzeuge und Staffelführer. Mit den Knöpfen daneben kopierst du den Code oder einen Link, der die Startseite mit dem Code öffnet, oder zeigst den Link als QR-Code zum Abscannen.',
      'Der Leitstellen-Code ist verdeckt. Halte ihn gedrückt oder fokussiere ihn mit der Tastatur, um ihn zu lesen.',
    ]">
      <div class="flex flex-wrap gap-3">
        <CodeDisplay title="Fahrzeuge" code="A1B2C3D4" link="https://statussim.emberbox.app/?code=A1B2C3D4" qr/>
        <CodeDisplay title="Staffelführer" code="E5F6A7B8" link="https://statussim.emberbox.app/?code=E5F6A7B8" qr/>
        <CodeDisplay title="Leitstelle" code="C9D0E1F2" hidden/>
      </div>
    </HelpTopic>
  </HelpSection>
  <HelpSection title="Beitreten">
    <HelpTopic :paragraphs="[
      'Auf der Startseite den Code und einen Funkrufnamen eingeben und „Beitreten“ wählen. Ein Fahrzeug-Code öffnet das Statusfeld, ein Staffelführer-Code die Ansicht des Staffelführers, der Leitstellen-Code die Leitstelle.',
      'Ist der Funkrufname schon von einem verbundenen Fahrzeug belegt, schlägt die Startseite einen neuen vor. Ein neues Fahrzeug tritt mit Status 2 bei, einsatzbereit auf der Wache; wer mit demselben Funkrufnamen zurückkehrt, behält seinen Status.',
      'Jede Rolle nutzt ihr eigenes Gerät, ein Handy reicht.',
    ]"/>
  </HelpSection>
</template>
