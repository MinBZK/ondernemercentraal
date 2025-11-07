export function useParentRoute() {
  const router = useRouter()
  const route = useRoute()

  function navigateToParentRoute() {
    const parentRoute = route.matched[route.matched.length - 2]
    if (!parentRoute) {
      console.error('No parent route, matched routes: ', route.matched)
    } else {
      const parentRouteName = parentRoute.name || parentRoute.children[0].name
      const targetRoute = { name: parentRouteName, params: route.params }
      router.push(targetRoute)
    }
  }

  return { navigateToParentRoute }
}
