<template>
  <div
    :style="{
      width: props.width + 'px',
      height: props.height + 'px',
    }"
  >
    <ElSkeleton v-if="imgLoading" animated>
      <template #template>
        <ElSkeletonItem
          variant="image"
          :style="{
            width: props.width + 'px',
            height: props.height + 'px',
          }"
        />
      </template>
    </ElSkeleton>
    <img
      v-if="!loadError"
      :class="['object-contain', 'cursor-pointer', 'w-full', 'h-full']"
      :style="{
        visibility: imgLoading ? 'hidden' : 'visible',
      }"
      :src="props.src"
      @load="handleImageLoad"
      @error="handleImageError"
      @click="() => handlePreview(props.src)"
    />
    <img
      v-else
      :class="['object-contain', 'w-full', 'h-full']"
      src="/errorImage.png"
      :alt="$t('common.加载失败')"
    />
  </div>
</template>
<script lang="ts" setup>
import { ref } from "vue";
import { popup } from "../modal/ModalContainer.vue";
import ImageViewer from "@/components/img-viewer/index.vue";
import { ElSkeleton, ElSkeletonItem, vLoading } from "element-plus";
const loadError = ref(false);
const imgLoading = ref(true);
const emit = defineEmits(["handleImgLoad"]);

const props = defineProps<{
  src: string;
  width?: string;
  height?: string;
}>();
const handleImageError = () => {
  loadError.value = true;
  imgLoading.value = false;
};
const handleImageLoad = () => {
  imgLoading.value = false;
  emit("handleImgLoad");
};
const handlePreview = (src: string) => {
  if (loadError.value) return;
  popup(ImageViewer, {
    imgSrc: src,
  })
    .then((res) => {})
    .catch(() => {});
};
</script>

<style lang="scss" scoped></style>
