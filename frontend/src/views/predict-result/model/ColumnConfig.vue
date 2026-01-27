<template>
  <ElDrawer
    width="500"
    v-model="dialogVisible"
    :before-close="props.handleCancel"
  >
    <template #header>
      <h3>
        {{ $t("common.表格配置") }}
      </h3>
    </template>
    <template #default>
      <div :class="['flex', 'items-center']">
        <ElSpace>
          <ElCheckbox
            v-model="checkAll"
            :indeterminate="isIndeterminate"
            @change="handleCheckAllChange"
          >
            {{ $t("common.全选") }}
          </ElCheckbox>
          <ElButton type="primary" size="small" @click="handleResetExample">
            {{ $t("common.恢复默认") }}
          </ElButton>
        </ElSpace>
      </div>
      <div :class="['mt-8']">
        {{ $t("common.理化性质") }}
        <ElCheckboxGroup
          v-model="selectedKeys"
          :class="['w-full']"
          @change="handleSelectedChange"
        >
          <ElRow>
            <ElCol v-for="item in keyList" :span="8">
              <ElTooltip :content="$t(`task.${item}`)" placement="left">
                <ElCheckbox :label="item" :value="item"></ElCheckbox>
              </ElTooltip>
            </ElCol>
          </ElRow>
        </ElCheckboxGroup>
      </div>
    </template>
    <template #footer>
      <ElButton @click="props.handleCancel">
        {{ $t("common.取消") }}
      </ElButton>
      <ElButton @click="handleConfirm" type="primary">
        {{ $t("common.确认") }}
      </ElButton>
    </template>
  </ElDrawer>
</template>

<script lang="ts" setup>
import { physicochemicalPropertyList } from "@/constants/predict";
import {
  ElButton,
  ElCheckbox,
  ElDrawer,
  ElRow,
  ElCol,
  ElCheckboxGroup,
  type CheckboxValueType,
  ElSpace,
  ElTooltip,
} from "element-plus";
import { computed, onMounted, ref } from "vue";
const props = defineProps<{
  handleOK: any;
  handleCancel: any;
  currentSelectKeys: string[];
}>();
const keyList = [...physicochemicalPropertyList];
const dialogVisible = ref<boolean>(false);
const isIndeterminate = computed(() => {
  return (
    selectedKeys.value.length > 0 && selectedKeys.value.length < keyList.length
  );
});
onMounted(() => {
  dialogVisible.value = true;
});
const handleCheckAllChange = (val: CheckboxValueType): void => {
  selectedKeys.value = val ? keyList : [];
};
const handleResetExample = () => {
  selectedKeys.value = [
    "nHet",
    "nRigid",
    "nRot",
    "nRing",
    "MaxRing",
    "TotalCharge",
  ];
};

const handleConfirm = () => {
  props.handleOK(selectedKeys.value);
};
const handleSelectedChange = (val: CheckboxValueType[]): void => {
  const checkedCount = val.length;
  checkAll.value = checkedCount === keyList.length;
};
const selectedKeys = ref<string[]>([...props.currentSelectKeys]);
const checkAll = ref<boolean>(selectedKeys.value.length === keyList.length);
</script>

<style lang="scss" scoped></style>
