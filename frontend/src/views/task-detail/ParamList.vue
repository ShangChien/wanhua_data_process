<template>
  <div>
    <div :class="['overflow-auto']" v-html="htmlStr"></div>
  </div>
</template>

<script lang="ts" setup>
import { paramLabelMap } from "@/constants/task";
import { useTaskDetailStore } from "@/stores/modules/taskDetail";
import { isString } from "lodash";
import { ref, watchEffect } from "vue";
import { codeToHtml } from "shiki";
const taskDetailStore = useTaskDetailStore();
const modelParamDict = ref<any>({});
const htmlStr = ref("");
watchEffect(() => {
  const blackList = ["filter_size", "active"];
  if (
    taskDetailStore.currentSelfModel &&
    taskDetailStore.modelParamData[taskDetailStore.currentSelfModel]
  ) {
    const getCNFormatterJSON = (obj: unknown) => {
      if (obj !== null && typeof obj === "object") {
        const keys = Reflect.ownKeys(obj);
        const ret: any = Array.isArray(obj) ? [] : {};
        for (const key of keys) {
          if (!blackList.includes(key as string)) {
            if (key in paramLabelMap) {
              ret[paramLabelMap[key as string]] = getCNFormatterJSON(
                (obj as any)[key]
              );
            } else {
              ret[key] = getCNFormatterJSON((obj as any)[key]);
            }
          }
        }
        return ret;
      } else {
        if (isString(obj) && obj in paramLabelMap) {
          return paramLabelMap[obj];
        }
        return obj;
      }
    };
    modelParamDict.value = getCNFormatterJSON(
      taskDetailStore.modelParamData[taskDetailStore.currentSelfModel]
    );
  }
});
watchEffect(() => {
  codeToHtml(JSON.stringify(modelParamDict.value, null, 2), {
    lang: "javascript",
    theme: "github-light",
  }).then((res) => {
    htmlStr.value = res;
  });
});
</script>

<style lang="scss" scoped>
:deep() {
  .vjs-tree-brackets {
    display: none;
  }
  .vjs-value.vjs-value-string {
    color: #0009;
  }
}
</style>
