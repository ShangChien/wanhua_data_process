<template>
  <ElDialog
    :lock-scroll="true"
    :show-close="true"
    v-model="dialogVisible"
    :title="props.title"
    width="500"
    :before-close="props.handleOK"
  >
    <template #default>
      <ElScrollbar max-height="400px">
        <div :class="['pr-3']">
          <ElDescriptions
            v-for="item in props.descList"
            :column="1"
            :title="item.title"
          >
            <ElDescriptionsItem
              v-for="detail in item.desc"
              :label="detail.label"
              >{{ detail.value }}</ElDescriptionsItem
            >
          </ElDescriptions>
        </div>
      </ElScrollbar>
    </template>
  </ElDialog>
</template>

<script lang="ts" setup>
import {
  ElDescriptions,
  ElDescriptionsItem,
  ElDialog,
  ElScrollbar,
} from "element-plus";
import { onMounted, ref } from "vue";
const props = defineProps<{
  handleOK: any;
  handleCancel: any;
  title: string;
  descList: {
    title: string;
    desc: {
      label: string;
      value: string;
    }[];
  }[];
}>();
const dialogVisible = ref<boolean>(false);
onMounted(() => {
  dialogVisible.value = true;
});
</script>

<style lang="scss" scoped></style>
