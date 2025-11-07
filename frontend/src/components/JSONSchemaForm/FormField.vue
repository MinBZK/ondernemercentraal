<script setup lang="ts">
type LabelWidth = 'small' | 'medium' | 'large'

type LabelFontSize = 'small' | 'medium' | 'large'

withDefaults(
  defineProps<{
    label?: string
    fieldId: string
    isRequired?: boolean
    warning?: string
    hideLabel?: boolean
    showDivider?: boolean
    labelBold?: boolean
    labelWidth?: LabelWidth
    labelFontSize?: LabelFontSize
    fullWidth?: boolean
    expandable?: boolean
  }>(),
  {
    hideLabel: false,
    showDivider: true,
    labelBold: false,
    isRequired: false,
    labelWidth: 'large',
    labelFontSize: 'medium',
    fullWidth: true,
    expandable: false,
  },
)
</script>

<template>
  <div>
    <label
      v-if="!hideLabel"
      :class="[
        'font-bold',
        {
          'text-lg': labelFontSize == 'large',
          'text-md': labelFontSize == 'medium',
          'text-sm': labelFontSize == 'small',
        },
      ]"
      :for="fieldId"
      >{{ label }}
      <div :class="['inline', isRequired && 'text-red-500']">
        {{ isRequired ? '*' : '' }}
      </div></label
    >

    <div :class="['mt-2', fullWidth ? 'w-full' : 'w-[300px]']">
      <slot />
    </div>
    <slot name="button"></slot>
  </div>
</template>
