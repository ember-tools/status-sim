<script setup lang="ts">
import {CodeDisplay, HelpPage, HelpSection, HelpTopic, usePage} from '@emberbox/ui'
import StatusBadge from '../components/StatusBadge.vue'
import StatusKeypad from '../components/StatusKeypad.vue'
import UnitLeaderVehicleCard from '../components/UnitLeaderVehicleCard.vue'
import VehicleGroup from '../components/VehicleGroup.vue'
import VehicleItem from '../components/VehicleItem.vue'
import {exampleVehicle} from '../helpExamples'

usePage({
  title: 'Hilfe – Status Sim',
  description: 'Wie eine Funkübung mit Status Sim abläuft: Übung anlegen, als Fahrzeug, Leitstelle oder Staffelführer beitreten, Status setzen und Szenarien abarbeiten.',
  path: '/hilfe',
})

/** The statuses a vehicle sets itself, what they mean and from which status they can be reached. */
const STATUSES = [
  {status: '1', text: 'Einsatzbereit über Funk. Erreichbar aus 2, 3, 4 und 8.'},
  {status: '2', text: 'Einsatzbereit auf der Wache. Mit diesem Status tritt jedes Fahrzeug bei. Erreichbar aus 1.'},
  {status: '3', text: 'Einsatzauftrag übernommen, auf der Anfahrt. Erreichbar aus 1 und 2.'},
  {status: '4', text: 'An der Einsatzstelle eingetroffen. Erreichbar aus 1 und 3.'},
  {status: '7', text: 'Patient aufgenommen, Transport. Nur aus 4.'},
  {status: '8', text: 'Am Transportziel eingetroffen. Nur aus 7.'},
]

const dispatchExample = exampleVehicle({status: '4', special: '5', kurzstatus: 'Fehlalarm BMA', ls_claimed_by: 'Disponent 1', next_todo: 'LS'})
const unitLeaderExample = exampleVehicle({status: '3', claimed_by: 'ZF Müller', radio_channel: '401', next_todo: 'SF'})
</script>

<template>
  <HelpPage title="Hilfe">
    <HelpSection title="Überblick">
      <HelpTopic :paragraphs="[
        'Status Sim spielt den Funkverkehr zwischen einer Leitstelle, Staffelführern und Fahrzeugen. Jede Rolle nutzt ihr eigenes Gerät, alle sehen denselben Stand. Die Seite fragt den Server alle zwei Sekunden nach dem neuesten Stand; nach einer eigenen Aktion sofort.',
        'Eine Übung hat drei Codes: den der Leitstelle, den für die Fahrzeuge und den für die Staffelführer. Wer einen Code kennt, kann mit dieser Rolle beitreten. Gib den Leitstellen-Code deshalb nur an weitere Disponenten weiter.',
        'Eine Übung wird sieben Tage nach dem letzten Zugriff vollständig gelöscht, mit allen Fahrzeugen, Nachrichten und Notizen. Solange jemand sie geöffnet hat, bleibt sie erhalten.',
      ]"/>
    </HelpSection>

    <HelpSection title="Übung anlegen und beitreten">
      <HelpTopic title="Übung anlegen" :paragraphs="[
        'Auf der Startseite den Namen der Leitstelle eingeben, etwa „Florian Berlin“, und „Leitstelle erstellen“ wählen. Der Name erscheint später in den Funksprüchen der Szenarien.',
      ]"/>
      <HelpTopic title="Codes verteilen" mockup="Die Codes im Kopf der Leitstelle" :paragraphs="[
        'Oben in der Leitstelle stehen die Codes für Fahrzeuge und Staffelführer. Mit den Knöpfen daneben kopierst du den Code oder einen Link, der die Startseite mit dem Code öffnet, oder zeigst den Link als QR-Code zum Abscannen.',
        'Der Leitstellen-Code ist verdeckt. Halte ihn gedrückt oder fokussiere ihn mit der Tastatur, um ihn zu lesen.',
      ]">
        <div class="flex flex-wrap gap-3">
          <CodeDisplay title="Fahrzeuge" code="A1B2C3D4" link="https://statussim.emberbox.app/?code=A1B2C3D4" qr/>
          <CodeDisplay title="Staffelführer" code="E5F6A7B8" link="https://statussim.emberbox.app/?code=E5F6A7B8" qr/>
          <CodeDisplay title="Leitstelle" code="C9D0E1F2" hidden/>
        </div>
      </HelpTopic>
      <HelpTopic title="Beitreten" :paragraphs="[
        'Auf der Startseite den Code und einen Funkrufnamen eingeben und „Beitreten“ wählen. Ein Fahrzeug-Code öffnet das Statusfeld, ein Staffelführer-Code die Ansicht des Staffelführers, der Leitstellen-Code die Leitstelle.',
        'Ist der Funkrufname schon von einem verbundenen Fahrzeug belegt, schlägt die Startseite einen neuen vor.',
      ]"/>
    </HelpSection>

    <HelpSection title="Als Fahrzeug">
      <HelpTopic title="Statusfeld" mockup="Status 2 ist gesetzt, ein Sprechwunsch (5) ist offen" :paragraphs="[
        'Drücke eine Ziffer, um den Status zu wechseln. Der aktuelle Status leuchtet grün, ein offener Sprechwunsch oder Blitz gelb. Bis der Server antwortet, leuchtet die gedrückte Taste blau.',
        'Nicht jeder Status ist aus jedem anderen erreichbar; ein unzulässiger Wechsel wird ignoriert.',
      ]">
        <div class="max-w-[220px]">
          <StatusKeypad status="2" special="5"/>
        </div>
      </HelpTopic>
      <HelpTopic title="Die Status" :paragraphs="[]">
        <template #content>
          <ul class="m-0 flex list-none flex-col gap-2 p-0">
            <li v-for="entry in STATUSES" :key="entry.status" class="flex items-center gap-3">
              <StatusBadge :status="entry.status"/>
              <span class="text-muted">{{ entry.text }}</span>
            </li>
          </ul>
        </template>
      </HelpTopic>
      <HelpTopic title="Sprechwunsch und Blitz" :paragraphs="[
        'Taste 5 meldet einen Sprechwunsch, Taste 0 einen dringenden Sprechwunsch (Blitz). Beide erscheinen in der Leitstelle sofort ganz oben. Ein zweiter Druck auf dieselbe Taste nimmt die Meldung zurück; die Leitstelle kann sie ebenfalls löschen.',
      ]"/>
      <HelpTopic title="Kurzlagemeldung und Nachrichten" :paragraphs="[
        'Unter dem Statusfeld wählst du eine vorbereitete Kurzlagemeldung. Die Leitstelle sieht sie am Fahrzeug und bestätigt sie mit „OK“.',
        'Im Reiter „Nachrichten“ stehen die Nachrichten von Leitstelle und Staffelführer, die neueste oben. Kommt eine neue, zeigt der Reiter „Neu“.',
      ]"/>
      <HelpTopic title="Mit dem Staffelführer sprechen" :paragraphs="[
        '„Mit SF sprechen“ zeigt der Leitstelle, dass das Fahrzeug gerade mit dem Staffelführer spricht und auf dem Kanal der Leitstelle nicht erreichbar ist. „Gespräch beenden“ hebt das wieder auf.',
        'Fordert dich der Staffelführer an, blinkt eine rote Meldung mit seinem Funkkanal. Wechsle den Kanal und bestätige mit „Kanal gewechselt“.',
      ]"/>
    </HelpSection>

    <HelpSection title="In der Leitstelle">
      <HelpTopic title="Name und Funkkanal" :paragraphs="[
        'Mehrere Disponenten können gleichzeitig arbeiten. Jeder gibt rechts oben seinen Namen ein und speichert ihn. Der Funkkanal wird den Fahrzeugen angezeigt, die du übernommen hast.',
        'Name und Kanal stehen danach in der Adresse der Seite. So lässt sich die Leitstelle mit diesen Angaben neu laden oder an einen weiteren Disponenten weitergeben, der dann seinen eigenen Namen einträgt.',
      ]"/>
      <HelpTopic title="Fahrzeuge übernehmen" mockup="Ein übernommenes Fahrzeug mit Sprechwunsch und Kurzlagemeldung" :paragraphs="[
        'Jeder Disponent übernimmt die Fahrzeuge, für die er zuständig ist. Fahrzeuge ohne Zuordnung stehen gedämpft im Bereich „Nicht übernommen“ am Ende.',
        'Ein Klick auf Status und Funkrufnamen klappt das Fahrzeug auf. Dort setzt du den Status von Hand (1 bis 4), erstellst oder verwirfst einen Einsatz, hakst die Funksprüche des Szenarios ab, schreibst Nachrichten an das Fahrzeug und hinterlegst Notizen.',
      ]">
        <VehicleItem :car="dispatchExample" admin-code="C9D0E1F2" ls-name="Disponent 1"/>
      </HelpTopic>
      <HelpTopic title="Bereiche" mockup="Die Bereiche, nach Dringlichkeit geordnet" :paragraphs="[
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

    <HelpSection title="Als Staffelführer">
      <HelpTopic title="Fahrzeuge übernehmen und anfordern" mockup="Ein übernommenes Fahrzeug, bei dem der Staffelführer als Nächstes spricht" :paragraphs="[
        'Der Staffelführer übernimmt die Fahrzeuge, die er führt. Nur übernommene Fahrzeuge kann er anfordern.',
        'Vorher trägt er seinen Funkkanal ein. „Anfrage“ schickt dem Fahrzeug die Aufforderung, auf diesen Kanal zu wechseln. Bestätigt das Fahrzeug, steht dort „Spricht“; „Fertig“ schließt das Gespräch ab.',
      ]">
        <UnitLeaderVehicleCard :car="unitLeaderExample" code="E5F6A7B8" sf-name="ZF Müller"/>
      </HelpTopic>
      <HelpTopic title="Szenario und Nachrichten" :paragraphs="[
        'Aufgeklappt zeigt ein Fahrzeug die Checkliste seines Szenarios, die Nachrichten und eigene Notizen des Staffelführers. Fahrzeuge, bei denen er als Nächstes spricht, stehen im Bereich „Aktion erforderlich (SF)“ ganz oben.',
      ]"/>
    </HelpSection>

    <HelpSection title="Szenarien und Checklisten">
      <HelpTopic :paragraphs="[
        '„Einsatz erstellen“ in der Leitstelle wählt ein Szenario, das das Fahrzeug noch nicht hatte, und erzeugt daraus die Funksprüche für Alarmierung, Anfahrt, Lagemeldungen und Abschluss, mit dem Namen der Leitstelle, dem Funkrufnamen und einer Einsatznummer.',
        'Jeder Funkspruch nennt, wer spricht: LS für die Leitstelle, SF für den Staffelführer, FZ für das Fahrzeug. Leitstelle und Staffelführer sehen dieselbe Checkliste und haken gemeinsam ab; „Alle erledigt“ hakt einen ganzen Schritt ab.',
        'Ist ein Szenario durch, startet „Neuer Einsatz“ das nächste. Sind alle Szenarien verbraucht, beginnt die Auswahl von vorn.',
      ]"/>
    </HelpSection>

    <HelpSection title="Gut zu wissen">
      <HelpTopic :paragraphs="[
        'Hell und dunkel wechselst du mit dem Knopf rechts im Kopf der Seite.',
        'Ein Fahrzeug gilt als verbunden, solange seine Seite den Server erreicht. Nach 15 Sekunden ohne Kontakt erscheint es als getrennt, nach fünf Minuten verschwindet es aus der Übung.',
        'Im Browser merkt sich Status Sim je Übung den Namen und Funkkanal von Leitstelle und Staffelführer und ob die Leitstelle Sprechwünsche zusammenfasst. Diese Angaben werden nach sieben Tagen verworfen.',
      ]"/>
    </HelpSection>
  </HelpPage>
</template>
