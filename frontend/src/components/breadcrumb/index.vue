<template>
  <div>
    <ElBreadcrumb separator="/">
      <ElBreadcrumbItem v-for="item in matchedRouteList">
        {{ item.name }}
      </ElBreadcrumbItem>
    </ElBreadcrumb>
  </div>
</template>

<script lang="ts" setup>
import { ElBreadcrumb, ElBreadcrumbItem } from "element-plus";
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
const route = useRoute();
const matchedRouteList = route.matched;
</script>

<style lang="scss" scoped></style>
