<template>
  <ElImageViewer
    :close-on-press-escape="false"
    @close="props.handleOK"
    v-if="viewerVisible"
    :url-list="[props.imgSrc]"
  />
</template>

<script lang="ts" setup>
import { ElImageViewer } from "element-plus";
import { onMounted, ref } from "vue";
const props = defineProps<{
  imgSrc: any;
  handleOK: any;
  handleCancel: any;
}>();
const viewerVisible = ref(false);
onMounted(() => {
  viewerVisible.value = true;
});
</script>

<style lang="scss" scoped></style>
