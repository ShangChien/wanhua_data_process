<template>
  <div :class="['flex', 'flex-col', 'h-full']">
    <div :class="['h-0', 'flex-1', 'list-wrapper']">
      <VxeTable
        show-overflow
        :scroll-y="{ enabled: true, gt: 0 }"
        round
        border="none"
        :data="props.list"
        height="auto"
        auto-resize
      >
        <template v-for="item in colList" :key="item.prop">
          <VxeColumn
            show-header-overflow
            show-overflow="title"
            show-footer-overflow
            :title="item.label"
            :field="item.prop"
            :prop="item.prop"
            min-width="100"
          >
          </VxeColumn>
        </template>
      </VxeTable>
    </div>
    <div :class="['mt-2', 'flex', 'items-center', 'gap-2']">
      <div :class="['text-label']">
        {{ $t("common.数据集总数") }}
      </div>
      <ElStatistic :value="outputValue" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { useTransition } from "@vueuse/core";
import { ElSpace, ElStatistic } from "element-plus";
import { computed, ref, watchEffect } from "vue";

const props = defineProps<{
  list: any[];
}>();
const source = ref(0);
const outputValue = useTransition(source, {
  duration: 1500,
});
watchEffect(() => {
  source.value = props.list.length;
});
const colList = computed(() => {
  if (props.list && props.list.length)
    return Object.keys(props.list[0])
      .filter((item) => item !== "_X_ROW_KEY")
      .map((item) => {
        return {
          label: item,
          prop: item,
        };
      });
  return [];
});
</script>

<style lang="scss" scoped>
@import "@/assets/variables.scss";
.list-wrapper {
  box-shadow: 0px 4px 19px 0px rgba(222, 222, 222, 0.2);
}

:deep() {
  .el-statistic__content {
    font-size: 16px;
    color: $brand5-color;
  }
}
</style>
