<template>
  <div :class="['data-box']">
    <ElSpace alignment="center" :size="12">
      <div :class="['icon-box']">
        <svg ref="svgRef" class="statistic-icon">
          <use :href="props.icon"></use>
        </svg>
      </div>
      <ElSpace direction="vertical" :size="4" alignment="start">
        <div :class="['static-label']">{{ props.title }}</div>
        <div :class="['static-text']"><slot></slot></div>
      </ElSpace>
    </ElSpace>
  </div>
</template>

<script lang="ts" setup>
import { ElSpace } from "element-plus";
import { onMounted, ref } from "vue";
const props = defineProps<{
  bgColor: string;
  lineColor: string;
  icon: string;
  title: string;
  height?: string;
  width?: string;
}>();
const svgRef = ref<SVGElement | null>(null);
const replaceUseWithSymbol = async () => {
  if (!svgRef.value) return;
  const symbols = document.querySelectorAll("symbol");
  const symbolElement = Array.from(symbols).find((symbol) => {
    return symbol.id === props.icon.replace(/^#/, "");
  });
  if (symbolElement) {
    const svg = svgRef.value;
    svg.innerHTML = symbolElement.innerHTML;
  }
};
onMounted(() => {
  replaceUseWithSymbol();
});
</script>

<style lang="scss" scoped>
@import "@/assets/variables.scss";
.data-box {
  display: flex;
  flex-direction: column;
}
.icon-box {
  // height: 30px;
  // width: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20%;
}
.static-text {
  // font-size: 20px;
  // font-weight: bold;
  // color: #292929;
  font-family: DIN Alternate;
  font-size: 24px;
  font-weight: bold;
  line-height: 22px;
  letter-spacing: 0em;
  color: $font-title-color;
  text-wrap: nowrap;
}
.statistic-icon {
  height: 48px;
  width: 48px;
}
.static-label {
  text-wrap: nowrap;
  font-size: 12px;
  font-weight: normal;
  line-height: 22px;
  letter-spacing: 0em;
  color: $font-gray3-color;
}
</style>
