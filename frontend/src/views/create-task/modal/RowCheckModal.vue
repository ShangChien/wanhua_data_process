<!-- <template>
  <ElDialog width="800" title="编辑" v-model="modalVisible">
    <ElForm :model="formData" label-width="auto">
      <ElFormItem label="smiles" :prop="fileStore.baseOptions.smiles_col">
        <ElInput v-model="formData[fileStore.baseOptions.smiles_col]" />
      </ElFormItem>
      <ElFormItem
        v-for="(item, index) in fileStore.baseOptions.target_cols"
        :key="item"
        :label="`target ${index + 1}`"
        :prop="item"
      >
        <ElInput v-model="formData[item]" />
      </ElFormItem>
    </ElForm>
    <template #footer>
      <ElButton @click="modalVisible = false">取消</ElButton>
      <ElButton type="primary" @click="handleConfirm">确认</ElButton>
    </template>
  </ElDialog>
</template>

<script lang="ts" setup>
import { useFileStore } from '@/stores/modules/file'
import { ElButton, ElForm, ElInput, ElFormItem, ElDialog } from 'element-plus'
import { isEmpty } from 'lodash'
import { onMounted, ref } from 'vue'
const props = defineProps<{ data: any }>()
const fileStore = useFileStore()

const modalVisible = defineModel('visible', { type: Boolean, default: false })

const formData = ref<any>({})
onMounted(() => {
  if (!isEmpty(props.data)) {
    formData.value[fileStore.baseOptions.smiles_col] = props.data[fileStore.baseOptions.smiles_col]
    for (let i = 0; i < fileStore.baseOptions.target_cols.length; i++) {
      const targetKey = fileStore.baseOptions.target_cols[i]
      formData.value[targetKey] = props.data[targetKey]
    }
  }
})
const handleConfirm = () => {
  modalVisible.value = false
}
</script>

<style lang="scss" scoped></style> -->

<template>
  <div></div>
</template>

<script lang="ts" setup></script>

<style lang="scss" scoped></style>
