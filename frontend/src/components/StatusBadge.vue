<script setup lang="ts">
import {computed} from 'vue'
import {statusColor} from '../status'

/** A vehicle's status digit in the colour of the status. */
const props = defineProps<{ status: string }>()
const color = computed(() => statusColor(props.status))
</script>

<template>
  <UBadge :color="color" variant="solid" class="tabular size-10 shrink-0 justify-center text-lg font-bold">
    {{ status }}
  </UBadge>
</template>
