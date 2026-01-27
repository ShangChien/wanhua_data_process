<template>
  <div class="fixed-settings" v-if="!tabPageStore.hasNav">
    <ElButton
      type="primary"
      :class="['w-6']"
      @click="tabPageStore.toggleSettingDrawerVisible"
    >
      <Icon
        icon="uil:setting"
        width="18"
        height="18"
        style="color: #fff"
      ></Icon>
    </ElButton>
  </div>
  <ElDrawer
    :class="['!w-[24%]', ['xl:!w-[14%]']]"
    :title="$t('common.页面配置')"
    v-model="tabPageStore.settingDrawerVisible"
  >
    <template #default>
      <ElForm label-width="auto">
        <ElFormItem
          :label="
            tabPageStore.hasNav
              ? $t('common.隐藏导航栏')
              : $t('common.打开导航栏')
          "
        >
          <ElSwitch size="small" v-model="tabPageStore.hasNav" />
        </ElFormItem>
        <!-- <ElFormItem
          :label="
            tabPageStore.hasNav
              ? $t('common.隐藏菜单栏')
              : $t('common.打开菜单栏')
          "
        >
          <ElSwitch size="small" v-model="tabPageStore.hasMenu" />
        </ElFormItem> -->
        <ElFormItem
          v-if="tabPageStore.hasMenu"
          :label="
            tabPageStore.hasNav
              ? $t('common.展开菜单栏')
              : $t('common.折叠菜单栏')
          "
        >
          <ElSwitch size="small" v-model="tabPageStore.menuCollapsed" />
        </ElFormItem>
        <ElFormItem :label="$t('common.系统语言')">
          <ElRadioGroup
            :model-value="currentLocale"
            @change="handleChangeLocale"
          >
            <ElRadio :value="LocaleOptions.cn">中文</ElRadio>
            <ElRadio :value="LocaleOptions.en">English</ElRadio>
          </ElRadioGroup>
        </ElFormItem>
      </ElForm>
    </template>
  </ElDrawer>
</template>

<script lang="ts" setup>
import { LocaleOptions } from "@/constants/storage";
import { useTabPageStore } from "@/stores/modules/page";
import useLocale from "@/utils/locale";
import { Icon } from "@iconify/vue";
import {
  ElButton,
  ElDrawer,
  ElSpace,
  ElSwitch,
  ElForm,
  ElFormItem,
  ElRadioGroup,
  ElRadio,
} from "element-plus";
const tabPageStore = useTabPageStore();
const { currentLocale, changeLocale } = useLocale();
const handleChangeLocale = (val: any) => {
  changeLocale(val);
};
</script>

<style lang="scss" scoped>
.fixed-settings {
  position: fixed;
  top: 280px;
  right: 0px;
  z-index: 1000;
}
</style>
