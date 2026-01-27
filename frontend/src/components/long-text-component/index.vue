<template>
  <div :class="['entire-text-container']">
    <div
      :class="['one-line']"
      :style="{
        '-webkit-line-clamp': props.lineNumber || 2,
        'max-width': props.width || '180px',
      }"
      :title="props.text"
    >
      {{ props.text }}
    </div>
    <div class="icon">
      <template v-if="copied">
        <Icon icon="ep:success-filled" style="color: #1fa92c" />
      </template>
      <template v-else>
        <ElTooltip effect="dark" :content="$t('common.复制')" placement="top">
          <Icon
            class="copy-icon"
            icon="ant-design:copy-outlined"
            @click="handleCopy"
          />
        </ElTooltip>
      </template>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { Icon } from "@iconify/vue/dist/iconify.js";
import { ElMessage, ElTooltip } from "element-plus";
import { ref } from "vue";
import { useI18n } from "vue-i18n";
const { t } = useI18n();

const props = defineProps<{
  text: string;
  lineNumber?: number;
  width?: string;
}>();
const copied = ref(false);
const handleCopy = () => {
  const textarea = document.createElement("textarea");
  textarea.value = props.text;
  document.body.appendChild(textarea);
  textarea.select();
  try {
    const successful = document.execCommand("copy");
    const msg = successful ? "成功" : "失败";
    copied.value = true;
    ElMessage({
      type: "success",
      message: t("common.复制到剪贴板"),
    });
    setTimeout(() => {
      copied.value = false;
    }, 3000);
  } catch (err) {
    console.warn("无法复制", err);
  }
  // 移除临时创建的 textarea
  document.body.removeChild(textarea);

  // if (navigator.clipboard) {
  //   try {
  //     navigator.clipboard
  //       .writeText(props.text)
  //       .then(() => {
  //         copied.value = true;
  //         ElMessage({
  //           type: "success",
  //           message: "复制到剪贴板！",
  //         });
  //         setTimeout(() => {
  //           copied.value = false;
  //         }, 3000);
  //       })
  //       .catch((e) => {
  //         console.log(e);
  //       });
  //   } catch (error) {
  //     console.log(error);
  //   }
  // }
};
</script>

<style lang="scss" scoped>
.one-line {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal; /* 重写以支持换行 */
  flex-grow: 1;
  // width: 180px;
  word-break: break-all;
}
.icon {
  transition: opacity 0.5s ease;
}
.entire-text-container {
  display: flex;
  align-items: center;
  &:hover {
    cursor: pointer;
    .icon {
      opacity: 1;
    }
  }
  .icon {
    display: flex;
    align-items: center;
    opacity: 0;
  }
}
.copy-icon {
  &:hover {
    color: #3976f5;
  }
}
</style>
