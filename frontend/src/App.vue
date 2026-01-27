<script setup lang="ts">
import { ElConfigProvider } from "element-plus";
import en from "element-plus/es/locale/lang/en";
import zhCn from "element-plus/es/locale/lang/zh-cn";
import { computed, watchEffect } from "vue";
import GlobalSetting from "./components/global-setting/index.vue";
import ModalContainer from "./components/modal/ModalContainer.vue";
import { LocaleOptions } from "./constants/storage";
import { useUserStore } from "./stores/modules/user";
import useLocale from "./utils/locale";
import VXEzhCN from "vxe-table/lib/locale/lang/zh-CN";
import VXEenUS from "vxe-table/lib/locale/lang/en-US";
import VxeTable from "vxe-table";
const locale = useLocale();
const elementLocale = computed(() => {
  return locale.currentLocale.value === LocaleOptions.cn ? zhCn : en;
});
const userStore = useUserStore();
userStore.initToken();
watchEffect(() => {
  if (locale.currentLocale.value === LocaleOptions.cn) {
    VxeTable.setI18n("zh-CN", VXEzhCN);
  } else {
    VxeTable.setI18n("zh-CN", VXEenUS);
  }
});
</script>

<template>
  <ElConfigProvider :locale="elementLocale">
    <RouterView />
    <ModalContainer />
    <GlobalSetting />
  </ElConfigProvider>
</template>
