<script setup lang="ts">
import {HelpIndex, HelpPage, HelpSection, HelpTopic, usePage} from '@emberbox/ui'
import {HELP_TOPICS} from '../helpTopics'

usePage({
  title: 'Hilfe – Status Sim',
  description: 'Wie eine Funkübung mit Status Sim abläuft: Übung anlegen, als Fahrzeug, Leitstelle oder Staffelführer beitreten, Status setzen und Szenarien abarbeiten.',
  path: '/hilfe',
})
</script>

<template>
  <HelpPage title="Hilfe">
    <HelpSection title="Überblick">
      <HelpTopic :paragraphs="[
        'Status Sim spielt den Funkverkehr zwischen einer Leitstelle, Staffelführern und Fahrzeugen. Jede Rolle nutzt ihr eigenes Gerät, alle sehen denselben Stand.',
      ]"/>
    </HelpSection>
    <HelpIndex :topics="HELP_TOPICS"/>
  </HelpPage>
</template>
