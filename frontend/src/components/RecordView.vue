<script setup lang="ts" generic="T extends Record<string, any>">
const props = defineProps<{
  data: T
  attributeConfig: EntityAttributeConfig<T>
  labelDictionary: EntityLabelDictionary<T>
}>()

const attributes = computed(() => Object.keys(props.attributeConfig) as (keyof T)[])

const visibleAttributes = computed(() =>
  attributes.value.filter((a) => getConfig(a)?.hidden !== true),
)

function getConfig(attr: keyof T) {
  return props.attributeConfig?.[attr]
}

function getLabel(attr: keyof T) {
  const generator = props.labelDictionary[attr]
  return generator ? generator() : attr
}
</script>

<template>
  <table>
    <thead>
      <tr>
        <th>Veld</th>
        <th>Waarde</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="attr in visibleAttributes" :key="attr">
        <td>{{ getLabel(attr) }}</td>
        <td>
          <FormattedValue :value="data[attr]" :data-type="getConfig(attr)?.dataType || 'text'" />
        </td>
      </tr>
    </tbody>
  </table>
</template>
