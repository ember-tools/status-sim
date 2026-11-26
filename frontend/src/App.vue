<script setup lang="ts">
import {AppFooter, AppHeader, EmberboxApp} from '@emberbox/ui'
import {useHead} from '@unhead/vue'
import {computed, defineAsyncComponent} from 'vue'
import {resolvePage, useNavigation} from './navigation'
import HelpView from './views/HelpView.vue'
import HelpTopicView from './views/HelpTopicView.vue'
import LandingView from './views/LandingView.vue'

const DispatchView = defineAsyncComponent(() => import('./views/DispatchView.vue'))
const UnitLeaderView = defineAsyncComponent(() => import('./views/UnitLeaderView.vue'))
const VehicleView = defineAsyncComponent(() => import('./views/VehicleView.vue'))

const {location} = useNavigation()
const page = computed(() => resolvePage(location.value))

/** Landing page and help are prerendered and describe themselves; every exercise page stays out of search engines. */
const isPublic = computed(() => ['landing', 'help', 'helpTopic'].includes(page.value.view))

useHead({
  meta: () => (isPublic.value ? [] : [{name: 'robots', content: 'noindex, nofollow'}]),
})
</script>

<template>
  <EmberboxApp>
    <AppHeader name="Status Sim" subtitle="Funk und Status üben" logo="/favicon.svg">
      <template #actions>
        <UButton href="/hilfe" icon="i-lucide-circle-help" color="neutral" variant="ghost" aria-label="Hilfe"/>
      </template>
    </AppHeader>
    <LandingView v-if="page.view === 'landing'"/>
    <HelpView v-else-if="page.view === 'help'"/>
    <HelpTopicView v-else-if="page.view === 'helpTopic'" :key="page.slug" :slug="page.slug"/>
    <DispatchView v-else-if="page.view === 'dispatch'" :key="page.code" :code="page.code"/>
    <UnitLeaderView v-else-if="page.view === 'unitLeader'" :key="page.code" :code="page.code"/>
    <VehicleView v-else :key="`${page.code}/${page.name}`" :code="page.code" :name="page.name"/>
    <AppFooter tool="Status Sim" source="https://github.com/ember-tools/status-sim" license="GPL-3.0" help="/hilfe"/>
  </EmberboxApp>
</template>
