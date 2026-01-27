<template>
  <div :class="['content-wrapper']">
    <ElRow :class="['w-full']">
      <ElCol :span="12" :class="['items-center', 'flex']">
        <ElSpace>
          <ElButton
            link
            @click="
              () => {
                router.push({ name: 'dashboard' });
              }
            "
          >
            <img
              width="124"
              height="32"
              :class="['object-contain']"
              src="@/assets/img/logo.png"
              alt=""
            />
          </ElButton>
          <!-- <Icon
            icon="lets-icons:chemistry-light"
            style="color: #2e3db2"
            width="32"
            height="32"
          ></Icon>

          <span :class="['text-[18px]']">Uni-QSAR</span> -->
        </ElSpace>

        <!-- <ElButton
          link
          :class="'ml-[32px]'"
          @click="tabPageStore.toggleMenuCollapse"
        >
          <Icon icon="fluent-mdl2:collapse-menu"></Icon>
        </ElButton> -->
      </ElCol>
      <ElCol :span="12" :class="['flex', 'flex-row-reverse']">
        <ElSpace :size="24">
          <ElMenu
            :class="['h-[54px]']"
            mode="horizontal"
            router
            :ellipsis="false"
            :default-openeds="defaultOpeneds"
            :default-active="defaultActive"
            unique-opened
          >
            <!-- <ElMenuItem index="/dashboard/create-ADMET-task">
              <svg width="20" height="20" :class="['mr-2']">
                <use href="#ADMET-manage"></use>
              </svg>
              <template #title>ADMET</template>
            </ElMenuItem> -->
            <ElMenuItem index="/dashboard/task-manage">
              <svg width="20" height="20" :class="['mr-2']">
                <use href="#task-manage"></use>
              </svg>
              <template #title>{{ $t("common.任务管理") }}</template>
            </ElMenuItem>
          </ElMenu>
          <ElDivider direction="vertical" />

          <ElButton @click="switchLocale" link>{{
            locale.currentLocale.value === LocaleOptions.cn ? "English" : "中文"
          }}</ElButton>
          <ElTooltip :content="$t('common.我要反馈')" placement="bottom">
            <ElButton link @click="handleFeedback">
              <Icon
                icon="fluent:person-feedback-16-filled"
                width="22"
                height="22"
              ></Icon>
            </ElButton>
          </ElTooltip>

          <ElDropdown
            v-if="userStore.userInfo"
            :hide-on-click="false"
            :disabled="operationDisabled"
          >
            <ElButton link>
              <svg :class="['w-7', 'h-7', 'mr-2']">
                <use href="#default-user"></use>
              </svg>
              {{ userStore.userInfo?.sub }}
            </ElButton>
            <template #dropdown>
              <ElDropdownMenu>
                <ElDropdownItem>
                  <ElButton link @click="handleLogout">
                    {{ $t("common.退出登陆") }}
                  </ElButton>
                </ElDropdownItem>
              </ElDropdownMenu>
            </template>
          </ElDropdown>
        </ElSpace>
      </ElCol>
    </ElRow>
  </div>
</template>

<script lang="ts" setup>
import { LocaleOptions } from "@/constants/storage";
import { logout } from "@/service/api/user";
import { useTabPageStore } from "@/stores/modules/page";
import { useUserStore } from "@/stores/modules/user";
import useLocale from "@/utils/locale";
import { Icon } from "@iconify/vue";
import { useFullscreen } from "@vueuse/core";
import {
  ElButton,
  ElCol,
  ElDropdownItem,
  ElDropdown,
  ElDropdownMenu,
  ElMessage,
  ElRow,
  ElSpace,
  ElDivider,
  ElMenu,
  ElMenuItem,
  ElTooltip,
} from "element-plus";
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { popup } from "../modal/ModalContainer.vue";
import FeedbackModal from "./FeedbackModal.vue";
const operationDisabled = import.meta.env.VITE_IS_BOHRIUM !== undefined;
const { isFullscreen, toggle: toggleFullScreen } = useFullscreen();
const tabPageStore = useTabPageStore();
const router = useRouter();
const locale = useLocale();
const userStore = useUserStore();
const route = useRoute();
const handleLogout = async () => {
  if (userStore.token !== null) {
    logout()
      .then(() => {
        ElMessage.success("账号成功退出");
      })
      .finally(() => {
        router.push({ name: "login" });
      });
  } else {
    router.push({ name: "login" });
  }
};
const switchLocale = () => {
  if (locale.currentLocale.value === LocaleOptions.cn) {
    locale.changeLocale(LocaleOptions.en);
  } else if (locale.currentLocale.value === LocaleOptions.en) {
    locale.changeLocale(LocaleOptions.cn);
  }
};

const defaultActive = computed(() => {
  return route.path;
});
const defaultOpeneds = computed(() => {
  let path = route.matched.map((item) => item.path);
  if (path.length > 1) path = path.slice(0, path.length - 1);
  return path;
});
const handleFeedback = () => {
  popup(FeedbackModal, {})
    .then(() => {})
    .catch(() => {});
};
</script>

<style lang="scss" scoped>
@import "@/assets/variables.scss";
.content-wrapper {
  padding: 0 20px;
  display: flex;
  align-items: center;
  height: 100%;
  background-color: $font-white1-color;
}
:deep() {
  .el-menu--horizontal.el-menu {
    border-bottom-width: 0;
  }
  .el-tooltip__trigger {
    outline: none !important;
  }
}
</style>
