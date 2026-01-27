<template>
  <div
    :class="[
      'card-style',
      'w-full',
      isFullscreen ? 'fullscreen-status' : '',
      'transition-all',
    ]"
  >
    <div>
      <div :class="['flex', 'justify-between']">
        <div :class="['text-h6', 'bottom-divider', 'flex', 'items-center']">
          {{ $t("task.日志") }}
        </div>
        <div :class="['flex', 'justify-center', 'items-center', 'gap-2']">
          <ElTooltip placement="top" :content="$t('task.刷新日志')">
            <ElButton :class="['!pt-0']" link @click="refreshTaskLog">
              <svg class="iconpark-icon"><use href="#reload"></use></svg>
            </ElButton>
          </ElTooltip>
          <ElTooltip placement="top" :content="$t('task.导出日志')">
            <ElButton
              :class="['!pt-0', '!ml-0']"
              link
              :disabled="downloadDisabled"
              @click="handleDownloadLog"
            >
              <svg class="iconpark-icon"><use href="#export"></use></svg>
            </ElButton>
          </ElTooltip>
          <IconButton
            iconSVGHref="#"
            :tooltipText="
              isDarkMode ? $t('common.浅色模式') : $t('common.深色模式')
            "
            @click="changeTheme"
          >
            <Icon
              :class="['iconpark-icon']"
              :icon="
                isDarkMode ? 'line-md:sunny-outline' : 'line-md:moon-simple'
              "
            />
          </IconButton>
          <IconButton
            iconSVGHref="#"
            :tooltipText="
              isFullscreen ? $t('common.退出全屏') : $t('common.全屏')
            "
            @click="isFullscreen = !isFullscreen"
          >
            <Icon
              :class="['iconpark-icon']"
              :icon="
                isFullscreen
                  ? 'ant-design:fullscreen-exit-outlined'
                  : 'ant-design:fullscreen-outlined'
              "
            />
          </IconButton>
        </div>
      </div>
    </div>
    <div
      :class="[
        'w-full',
        isFullscreen ? 'h-[90vh]' : 'h-[40vh]',
        'overflow-auto',
        'transition-all',
      ]"
    >
      <template v-if="dataLoading">
        <ElSkeleton animated :rows="7" />
      </template>
      <template v-else>
        <div v-html="htmlStr"></div>
      </template>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { getTaskLog } from "@/service/api/task";
import { useTaskDetailStore } from "@/stores/modules/taskDetail";
import { triggerDownload } from "@/utils/download";
import {
  ElButton,
  ElMessage,
  ElSkeleton,
  ElTooltip,
  vLoading,
  ElSpace,
} from "element-plus";
import { codeToHtml } from "shiki";
import { computed, ref, watchEffect } from "vue";
import { useI18n } from "vue-i18n";
import IconButton from "@/components/icon-button/index.vue";
import { useRoute } from "vue-router";
import { Icon } from "@iconify/vue";

const props = defineProps<{
  logFileName: string;
}>();
const { t } = useI18n();
const route = useRoute();
const taskId = route.query.taskId as string;
const dataLoading = ref<boolean>(true);
const htmlStr = ref<string>("");
const taskDetailStore = useTaskDetailStore();
const downloadDisabled = computed(() => {
  return taskDetailStore.taskLog === "" || dataLoading.value;
});
const isFullscreen = ref(false);
const isDarkMode = ref(false);
const logStr = ref();
const limitNumber = 1000;
const refreshTaskLog = () => {
  dataLoading.value = true;
  return getTaskLog({ run_id: taskId })
    .then((res) => {
      taskDetailStore.updateStore({
        taskLog: res.data.data,
      });
      const str = taskDetailStore.taskLog
        .split("\n")
        .slice(-limitNumber)
        .join("\n");
      codeToHtml(str, {
        lang: "log",
        // theme: "material-theme-lighter",
        themes: {
          light: "material-theme-lighter",
          dark: "material-theme-darker",
        },
      })
        .then((res) => {
          htmlStr.value = res;
        })
        .finally(() => {
          dataLoading.value = false;
        });
    })
    .catch(() => {
      dataLoading.value = false;
    });
};
refreshTaskLog();
const handleDownloadLog = () => {
  triggerDownload(
    taskDetailStore.taskLog,
    { type: "text/plain" },
    props.logFileName
  ).then(() => {
    ElMessage.success(t("common.下载成功"));
  });
};
watchEffect(() => {
  if (isFullscreen.value) {
    // document.body.style.overflow = "hidden";
  } else {
    // document.body.style.overflow = "";
  }
});
const changeTheme = () => {
  if (isDarkMode.value) {
    document.body.classList.remove("dark");
  } else {
    document.body.classList.add("dark");
  }
  isDarkMode.value = !isDarkMode.value;
};
</script>

<style lang="scss" scoped>
:deep() {
  .shiki {
    margin-top: 0;
    // width: fit-content;
    // max-width: 100%;
    min-width: fit-content;
    width: 100%;
    margin-bottom: 0;
  }
}
.bottom-divider {
  border-bottom: 1px solid #d1d5de;
  width: fit-content;
  padding-bottom: 20px;
  margin-bottom: 0;
}

.fullscreen-status {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  width: 100%;
  height: 100%;
}
</style>
<style>
body.dark .shiki,
body.dark .shiki span {
  color: var(--shiki-dark) !important;
  background-color: var(--shiki-dark-bg) !important;
  /* 可选，用于定义字体样式 */
  font-style: var(--shiki-dark-font-style) !important;
  font-weight: var(--shiki-dark-font-weight) !important;
  text-decoration: var(--shiki-dark-text-decoration) !important;
}
@media (prefers-color-scheme: dark) {
  .shiki,
  .shiki span {
    color: var(--shiki-dark) !important;
    background-color: var(--shiki-dark-bg) !important;
    /* 可选，用于定义字体样式 */
    font-style: var(--shiki-dark-font-style) !important;
    font-weight: var(--shiki-dark-font-weight) !important;
    text-decoration: var(--shiki-dark-text-decoration) !important;
  }
}
</style>
