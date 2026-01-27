<template>
  <div class="layout-bg"></div>
  <div class="wrapper">
    <div :style="hiddenDivStyle" v-if="tabPageStore.hasMenu"></div>
    <div :style="sideDivStyle" v-if="tabPageStore.hasMenu">
      <MenuComponent />
    </div>
    <div class="main">
      <div class="header" v-if="tabPageStore.hasNav"></div>
      <header class="real-head" v-if="tabPageStore.hasNav">
        <HeaderComponent />
      </header>
      <main class="main-content">
        <!-- <Breadcrumb /> -->
        <RouterView v-slot="{ Component }">
          <Transition name="fade" mode="out-in">
            <!-- <KeepAlive> -->
            <component :is="Component" />
            <!-- </KeepAlive> -->
          </Transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>

<script lang="ts" setup>
import Breadcrumb from "@/components/breadcrumb/index.vue";
import MenuComponent from "./MenuComponent.vue";
import { RouterView } from "vue-router";
import HeaderComponent from "./HeaderComponent.vue";
import { useTabPageStore } from "@/stores/modules/page";
import { computed } from "vue";
const tabPageStore = useTabPageStore();

const hiddenDivStyle = computed(() => {
  const width = tabPageStore.menuCollapsed ? "64px" : "220px";
  return {
    "max-width": width,
    "min-width": width,
    flex: `0 0 ${width}`,
    width: width,
    overflow: "hidden",
    transition: "all 0.2s ease 0s",
  };
});
const sideDivStyle = computed(() => {
  const width = tabPageStore.menuCollapsed ? "64px" : "220px";
  const navHeight = tabPageStore.hasNav ? "56px" : "0px";
  return {
    transition: "all 0.2s ease 0s",
    "max-width": width,
    "min-width": width,
    flex: `0 0 ${width}`,
    width: width,
    insetBlockStart: `${navHeight}`,
    insetInlineStart: "0",
    zIndex: 100,
    position: "fixed" as any,
    height: `calc(100% - ${navHeight})`,
  };
});
</script>

<style lang="scss" scoped>
@import "@/assets/variables";
.wrapper {
  display: flex;
  flex-direction: row;
  min-height: 100%;
}

.main {
  // background-color: #f3f3f3;
  min-width: 0;
  min-height: 0;
  display: flex;
  width: 100%;
  position: relative;
  flex-direction: column;

  .header {
    height: 56px;
    flex: 0 0 auto;
  }
  .real-head {
    height: 56px;
    position: fixed;
    z-index: 100;
    width: 100%;
    inset-block-start: 0;
    inset-inline-end: 0;
    backdrop-filter: blur(8px);
    background-color: rgba(255, 255, 255, 0.6);
    border-block-end: 1px solid rgba(5, 5, 5, 0.06);
  }
}

.main-content {
  display: flex;
  flex-direction: column;
}
.layout-bg {
  pointer-events: none;
  position: fixed;
  overflow: hidden;
  z-index: 0;
  height: 100%;
  width: 100%;
  background: $gray1-color;
  inset-block-start: 0;
  inset-inline-start: 0;
}
</style>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
