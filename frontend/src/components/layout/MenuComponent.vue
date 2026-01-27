<template>
  <ElMenu
    :collapse-transition="false"
    :collapse="tabPageStore.menuCollapsed"
    router
    :default-openeds="defaultOpeneds"
    :default-active="defaultActive"
    unique-opened
    :class="['w-full', 'h-full']"
  >
    <ElMenuItem index="/dashboard/task-manage">
      <!-- <Icon
        :class="['mr-2']"
        icon="eos-icons:job"
        width="24"
        height="24"
      ></Icon> -->
      <svg width="20" height="20" :class="['mr-2']">
        <use href="#task-manage"></use>
      </svg>
      <template #title>{{ $t("common.任务管理") }}</template>
    </ElMenuItem>
  </ElMenu>
</template>

<script lang="ts" setup>
import { useTabPageStore } from "@/stores/modules/page";
import { Icon } from "@iconify/vue";
import { ElMenu, ElMenuItem, ElSubMenu } from "element-plus";
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
const tabPageStore = useTabPageStore();
const route = useRoute();

const defaultActive = computed(() => {
  return route.path;
});
const defaultOpeneds = computed(() => {
  let path = route.matched.map((item) => item.path);
  if (path.length > 1) path = path.slice(0, path.length - 1);
  return path;
});
// const
</script>

<style lang="scss" scoped>
:deep() {
  .el-menu-item .el-menu-tooltip__trigger {
    padding: 0;
    display: flex;
    justify-content: center;
  }
}
</style>
