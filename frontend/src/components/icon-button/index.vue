<template>
  <div>
    <ElTooltip :content="props.tooltipText" placement="top">
      <ElButton link>
        <slot name="default">
          <svg
            class="default-icon"
            :style="{
              width: props.width + 'px',
              height: props.height + 'px',
            }"
          >
            <use :href="props.iconSVGHref"></use>
          </svg>
        </slot>
      </ElButton>
    </ElTooltip>
  </div>
</template>

<script lang="ts" setup>
import { ElButton, ElTooltip } from "element-plus";
const props = defineProps<{
  iconSVGHref: string;
  tooltipText: string;
  width?: number | string;
  height?: number | string;
}>();
</script>

<style lang="scss" scoped>
.default-icon {
  width: 18px;
  height: 18px;
}
</style>
