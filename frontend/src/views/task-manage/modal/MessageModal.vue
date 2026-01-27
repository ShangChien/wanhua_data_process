<template>
  <ElDialog
    :before-close="props.handleCancel"
    v-model="dialogVisible"
    :title="$t('common.确认删除')"
    width="500"
  >
    <span>
      {{ $t("task.确认删除任务", { id: props.taskData.run_id }) }}
    </span>
    <template #footer>
      <div class="dialog-footer">
        <ElButton @click="props.handleCancel">
          {{ $t("common.取消") }}
        </ElButton>
        <ElButton
          :loading="confirmBtnLoading"
          type="primary"
          @click="handleConfirm"
        >
          {{ $t("common.确认") }}
        </ElButton>
      </div>
    </template>
  </ElDialog>
</template>

<script lang="ts" setup>
// import { modalHOF } from "@/components/modal/ModalContainer.vue";
import { deleteTask } from "@/service/api/task";
import { ElDialog, ElButton } from "element-plus";
import { defineComponent, onMounted, ref } from "vue";
const dialogVisible = ref<boolean>(false);
const props = defineProps<{
  taskData: any;
  handleOK: any;
  handleCancel: any;
}>();

onMounted(() => {
  dialogVisible.value = true;
});
const confirmBtnLoading = ref<boolean>(false);
const handleConfirm = () => {
  confirmBtnLoading.value = true;
  deleteTask({ run_id: props.taskData.run_id })
    .then(() => {
      props.handleOK();
    })
    .finally(() => {
      confirmBtnLoading.value = false;
    });
};
</script>

<style lang="scss" scoped></style>
