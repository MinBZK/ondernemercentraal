<script setup lang="ts">
const useSidebar = true
</script>

<template>
  <div
    id="main"
    :class="[
      'py-4 gap-x-4',
      {
        'grid grid-cols-[190px_1fr]': useSidebar,
      },
    ]"
  >
    <div>
      <div class="sticky top-0 relative"><BeheerMenu /></div>
    </div>
    <div class="flex-row overflow-x-auto">
      <router-view name="modal" />
      <router-view />

      <!-- <router-view v-slot="{ Component }">
        <transition name="slide-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view> -->
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.005s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.07s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.07s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  /* transform: translateY(20px); */
  opacity: 0;
}
</style>
