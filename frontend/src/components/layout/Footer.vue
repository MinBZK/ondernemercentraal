<script setup lang="ts">
const { config } = useConfig()
</script>

<template>
  <footer class="footer-wrapper px-4">
    <div class="footer-wrapper-content">
      {{ config.tenant_name }}
    </div>
  </footer>
</template>

<style scoped lang="css">
.footer-wrapper {
  background-color: var(--color-primary);
  color: white;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 76px;
}

.footer-wrapper-content {
  font-size: 24px;
  display: flex;
  flex-basis: 100%;
  max-width: 1200px;
  align-items: center;
  justify-content: space-between;
  position: relative;
  min-height: 50px;
}
</style>
