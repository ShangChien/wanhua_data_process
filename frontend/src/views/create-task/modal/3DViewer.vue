<template>
  <div id="app" style="height: 500px; width: 500px">
    <canvas id="canvas" width="500" height="500"></canvas>
  </div>
</template>

<script lang="ts" setup>
import { onMounted } from "vue";
import { init } from "./init";
onMounted(() => {
  init();
});
</script>

<style lang="scss" scoped></style>
