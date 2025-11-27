import { breakpointsTailwind, useBreakpoints } from '@vueuse/core'
const { smallerOrEqual } = useBreakpoints(breakpointsTailwind)

export function useResponsive() {
  const isMobile = computed(() => smallerOrEqual('sm').value)

  return { isMobile }
}
