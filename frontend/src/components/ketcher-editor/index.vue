<template>
  <div>
    <iframe
      ref="iframeRef"
      :class="['w-[500px]', 'h-[500px]', 'border-0', editorLoading && 'hidden']"
      src="/ketcher-standalone/index.html"
    ></iframe>
    <ElSkeleton animated :loading="editorLoading">
      <template #template>
        <ElSkeletonItem variant="rect" :class="['w-[500px]', 'h-[500px]']" />
      </template>
    </ElSkeleton>
  </div>
</template>

<script lang="ts" setup>
import { ElSkeleton, ElSkeletonItem } from "element-plus";
import { onMounted, onUnmounted, ref } from "vue";
const props = defineProps<{
  value?: string;
  id?: string;
}>();
const emit = defineEmits(["change", "update:value"]);
const editorLoading = ref<boolean>(true);
const iframeRef = ref<HTMLIFrameElement>();
let ketcherInstance: any = null;
function getCurrentSmile() {
  if (!ketcherInstance) {
    return Promise.reject("ketcherInstance is not ready");
  }
  return ketcherInstance.getSmiles();
}
let timer: NodeJS.Timeout;
const handleEditorChange = () => {
  getCurrentSmile().then((smiles: string) => {
    emit("update:value", smiles);
    emit("change", smiles);
  });
};
onMounted(() => {
  const iframeDOM = iframeRef.value;
  timer = setInterval(() => {
    if ((iframeDOM && (iframeDOM.contentWindow as any)).ketcher) {
      ketcherInstance = (iframeDOM!.contentWindow as any).ketcher;
      editorLoading.value = false;
      ketcherInstance.editor.subscribe("change", handleEditorChange);
      if (props.value) {
        ketcherInstance.setMolecule(props.value);
      }
      clearInterval(timer);
    }
  }, 300);
});
onUnmounted(() => {
  if (timer) clearInterval(timer);
  if (ketcherInstance) {
    ketcherInstance.editor.unsubscribe("change", handleEditorChange);
  }
});
defineExpose({ getCurrentSmile });
</script>

<style lang="scss" scoped></style>
