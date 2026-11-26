<script setup lang="ts">
import {breadcrumbData, HelpPage, helpPath, usePage} from '@emberbox/ui'
import {type Component, computed} from 'vue'
import {HELP_TOPICS, type HelpSlug} from '../helpTopics'
import HelpCreateJoin from './help/HelpCreateJoin.vue'
import HelpDispatch from './help/HelpDispatch.vue'
import HelpGoodToKnow from './help/HelpGoodToKnow.vue'
import HelpScenarios from './help/HelpScenarios.vue'
import HelpStatuses from './help/HelpStatuses.vue'
import HelpUnitLeader from './help/HelpUnitLeader.vue'
import HelpVehicle from './help/HelpVehicle.vue'

/** One page of the help center; the navigation only routes here for a known slug. */
const props = defineProps<{ slug: HelpSlug }>()

/** The content of each topic, by slug. */
const CONTENT: Record<HelpSlug, Component> = {
  'uebung-anlegen': HelpCreateJoin,
  'fahrzeug': HelpVehicle,
  'status': HelpStatuses,
  'leitstelle': HelpDispatch,
  'staffelfuehrer': HelpUnitLeader,
  'szenarien': HelpScenarios,
  'verbindung-und-speicher': HelpGoodToKnow,
}

const topic = computed(() => HELP_TOPICS.find(candidate => candidate.slug === props.slug)!)

usePage(() => ({
  title: `${topic.value.title} – Hilfe – Status Sim`,
  description: topic.value.description,
  path: helpPath(topic.value.slug),
  structuredData: [breadcrumbData([
    {name: 'Status Sim', path: '/'},
    {name: 'Hilfe', path: helpPath()},
    {name: topic.value.title, path: helpPath(topic.value.slug)},
  ])],
}))
</script>

<template>
  <HelpPage :title="topic.title" :topics="HELP_TOPICS" :current="topic.slug">
    <component :is="CONTENT[props.slug]"/>
  </HelpPage>
</template>
