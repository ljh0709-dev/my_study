<template>
  <div id="app">
    <NavigationBar />
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <div class="footer-inner">
        <span class="footer-brand">TrendBook</span>
        <nav class="footer-nav">
          <a href="#">About</a>
          <a href="#">Privacy</a>
          <a href="#">Contact</a>
          <a href="#">Curation Policy</a>
        </nav>
        <span class="footer-copy">© 2026 TrendBook. All rights reserved.</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import NavigationBar from './components/NavigationBar.vue'
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-background);
  color: var(--color-on-background);
}

.app-main {
  flex: 1;
  width: 100%;
}

/* Footer — Calm Edition */
.app-footer {
  background: var(--color-surface-container-lowest);
  width: 100%;
  padding: 48px 0;
  border-top: 1px solid var(--color-outline-variant);
  margin-top: auto;
}

.footer-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  max-width: var(--container-max);
  margin: 0 auto;
  padding: 0 var(--space-margin-mobile);
}

.footer-brand {
  font: 300 24px/1.4 var(--font-headline);
  letter-spacing: var(--ls-headline-md);
  color: var(--color-primary);
}

.footer-nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 24px;
}

.footer-nav a {
  font-size: 0.72rem;
  font-weight: 300;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-outline);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.footer-nav a:hover {
  color: var(--color-primary);
}

.footer-copy {
  font-size: 0.72rem;
  font-weight: 300;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-secondary);
}

@media (min-width: 768px) {
  .footer-inner {
    flex-direction: row;
    justify-content: space-between;
    padding: 0 var(--space-margin-desktop);
  }
}
</style>
