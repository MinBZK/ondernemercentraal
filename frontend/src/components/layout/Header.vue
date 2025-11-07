<script setup lang="ts">
const { locale } = useLocale()

withDefaults(
  defineProps<{
    title: string
    pages: NavigatieItems[]
    routePathHome?: string
    hideNavigation?: boolean
    logoPath: string
  }>(),
  {
    routePathHome: '/',
    hideNavigation: false,
  },
)

const showNav = ref<boolean>(false)
const { me } = useAuth()
</script>

<template>
  <div id="mainwrapper" class="logo-wrapper px-2 lg:px-0">
    <slot name="logo" />
  </div>
  <div id="bar" class="bar-wrapper px-4 bg-primary">
    <div class="bar-wrapper-content">
      <div>
        <router-link
          v-if="!hideNavigation"
          :to="me ? { name: 'Beheer' } : { name: 'Welkom', params: { locale: locale } }"
        >
          {{ title }}
        </router-link>
      </div>
      <nav>
        <div
          :class="['nav-icon', !showNav ? 'hamburger' : 'close-icon']"
          role="button"
          aria-label="Toon het navigatiemenu"
          :aria-expanded="showNav ? 'true' : 'false'"
          @click="showNav = !showNav"
        />
        <ul class="pr-1">
          <template v-if="!hideNavigation">
            <li v-for="p in pages" :key="p.routeName">
              <slot name="item" v-bind="p">
                <router-link
                  :to="
                    p.routeName
                      ? { name: p.routeName, params: { locale: locale } }
                      : p.routePath || ''
                  "
                >
                  <i :class="p.icon" />
                  {{ p.label }}
                </router-link>
              </slot>
            </li>
          </template>
          <li>
            <LanguageSwitcher />
          </li>
        </ul>
      </nav>
    </div>
    <div class="bar-wrapper-content nav-responsive pl-5" :class="{ hide: !showNav }">
      <ul>
        <li v-for="p in pages" :key="p.routeName">
          <slot name="nav-item" v-bind="p">
            <router-link
              :to="
                p.routeName ? { name: p.routeName, params: { locale: locale } } : p.routePath || ''
              "
            >
              {{ p.label }}
            </router-link>
          </slot>
        </li>
        <li>
          <LanguageSwitcher />
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped lang="css">
a {
  text-decoration: none;
  &:hover {
    text-decoration: underline !important;
  }
}

.logo-wrapper figure {
  display: flex;
  align-items: flex-start;
  margin-block-start: 0em;
}

.logo {
  height: 76px;
}

.logo-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  height: 70px;
}

.logo-wrapper img {
  margin-left: 90px;
  height: 70px;
}

.bar-wrapper {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  min-height: 76px;
}

.bar-wrapper-content {
  display: flex;
  flex-basis: 100%;
  flex-wrap: wrap;
  max-width: 1200px;
  flex-shrink: 0;
  align-items: center;
  justify-content: space-between;
  -webkit-margin-end: -16px;
  margin-inline-end: -16px;
  -webkit-margin-start: -16px;
  margin-inline-start: -16px;
  position: relative;
  min-height: 76px;
}

.bar-wrapper-content div a,
.bar-wrapper-content div span,
.bar-wrapper-content nav {
  color: white;
  font-size: 24px;
}

.logo-caption {
  font-family: 'RO Serif', serif;
  font-size: 1rem;
  line-height: 1.1;
  width: 100%;
  max-width: 300px;
  padding: 20px 10px 10px;
  color: #000;
}

nav {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  font-size: 100%;
}

nav ul {
  display: none;
}

nav ul > li {
  font-size: 1.25rem;
  display: block;
  padding: 0 0 0 1em;
}

.barwapper ul > li a {
  color: white;
  text-decoration: none;
  display: block;
}

.hide {
  display: none;
}

.nav-responsive a {
  color: white !important;
  font-size: 14pt;
}

.nav-responsive li {
  padding: 0.5em 0;
  list-style-type: none;
}

.bar-wrapper-content nav a {
  color: white;
  text-decoration: none;
}

.nav-icon {
  cursor: pointer;
  display: flex;
  font-size: 18pt;
}

@media (min-width: 768px) {
  .nav-icon {
    display: none;
  }
}

.hamburger:before {
  content: '☰';
}

.close-icon:before {
  content: '☰';
}

@media (min-width: 768px) {
  nav ul > li {
    display: inline-block;
  }

  .nav-responsive {
    display: none;
  }

  nav ul {
    list-style: none;
    display: table;
    vertical-align: middle;
  }

  .logo-caption {
    padding: 50px 12px 25px;
  }

  .logo-wrapper {
    height: 125px;
  }

  .logo-wrapper img {
    height: 125px;
    margin-left: 112px;
  }

  img.logo-full {
    display: block;
  }

  img.logo-mobile {
    display: none;
  }
}

.logo-mobile {
  display: block;
}

.logo-full {
  display: none;
}

@media (max-width: 768px) {
  ul {
    margin-top: 0;
    padding-left: 1em;
  }
}
</style>
