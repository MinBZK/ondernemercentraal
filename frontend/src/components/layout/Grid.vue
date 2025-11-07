<template>
  <div class="flex flex-col min-h-screen">
    <header>
      <slot name="header" />
    </header>
    <slot name="hero" />

    <main class="main px-4 lg:px-0">
      <slot />
    </main>

    <footer>
      <slot name="footer" />
    </footer>
  </div>
</template>

<style scoped lang="css">
@import '@/assets/styles/main.css';

:deep(h1),
:deep(h2),
:deep(h3),
:deep(h4) {
  font-family: var(--font-family), sans-serif;
}

body {
  margin: 0;
  font-size: 1.2em;
}

.page-title {
  margin: 0;
}

.main {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  flex-grow: 1;
}
</style>
