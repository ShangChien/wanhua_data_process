<template>
  <div v-for="item in compList" :key="item.key" id="modal-container">
    <component :is="item.component" v-bind="item.props"></component>
  </div>
</template>

<script lang="ts">
import { uniqueId } from "lodash";
import {
  defineComponent,
  markRaw,
  ref,
  watchEffect,
  type Component,
} from "vue";

interface ModalComponent {
  component: unknown;
  id: string;
  props: unknown;
}

export const compList = ref(new Set<ModalComponent>());
watchEffect(() => {
  if (compList.value.size > 1) {
    console.warn("可能存在未销毁的 modal，请注意");
  }
});
const ModalContainer = defineComponent<any>({
  name: "ModalContainer",
  setup() {
    return {
      compList,
    };
  },
});
export const clearCompList = () => {
  compList.value.clear();
};
export const popup = (comp: any, funcProps: Record<string, any>) => {
  return new Promise((resolve, reject) => {
    const compItem: ModalComponent = {
      component: markRaw(comp),
      id: uniqueId(),
      props: {},
    };
    const deleteSelf = () => {
      compList.value.delete(compItem);
    };
    const handleOK = (data: unknown) => {
      resolve(data);
      deleteSelf();
    };
    const handleCancel = (reason: unknown) => {
      reject(reason);
      deleteSelf();
    };
    compItem.props = {
      ...funcProps,
      handleOK,
      handleCancel,
    };
    compList.value.add(compItem);
  });
};
export default ModalContainer;
</script>

<style lang="scss" scoped></style>
