<template>
  <ElDialog
    :lock-scroll="true"
    :show-close="true"
    v-model="dialogVisible"
    :title="$t('common.反馈给 DP')"
    width="700"
    :before-close="props.handleCancel"
  >
    <template #default>
      <div>
        <ElForm
          label-width="120"
          :model="formData"
          :rules="formRules"
          ref="formRef"
          scroll-to-error
        >
          <ElFormItem :label="$t('common.反馈类型')" prop="feedType">
            <ElRadioGroup v-model="formData.feedType">
              <ElRadio :value="FeedType.CONFUSION">
                {{ $t("common.困惑与建议") }}
              </ElRadio>
              <ElRadio :value="FeedType.BUG">
                {{ $t("common.Bug 缺陷") }}
              </ElRadio>
              <ElRadio :value="FeedType.PURCHASE">
                {{ $t("common.购买咨询") }}
              </ElRadio>
              <ElRadio :value="FeedType.OTHER">
                {{ $t("common.其他") }}
              </ElRadio>
            </ElRadioGroup>
          </ElFormItem>
          <template v-if="formData.feedType !== FeedType.OTHER">
            <ElFormItem :label="$t('common.标题')" prop="title">
              <ElInput
                :placeholder="$t('common.请输入标题')"
                v-model="formData.title"
              />
            </ElFormItem>
            <ElFormItem :label="$t('common.联系方式')" prop="contact">
              <ElInput
                :placeholder="$t('common.请输入联系方式')"
                v-model="formData.contact"
              />
            </ElFormItem>
            <ElFormItem :label="$t('common.反馈内容')" prop="content">
              <ElInput
                type="textarea"
                rows="4"
                :placeholder="$t('common.请输入反馈内容')"
                v-model="formData.content"
              />
            </ElFormItem>
          </template>
          <template v-else>
            <ElFormItem label=" ">
              <div
                :class="['flex', 'flex-col', 'justify-center', 'items-center']"
              >
                {{ $t("common.如有其他问题，可联系我们") }}
                <img src="/qsar.jpg" width="250" height="250" alt="" />
              </div>
            </ElFormItem>
          </template>
        </ElForm>
      </div>
    </template>
    <template #footer>
      <div class="dialog-footer">
        <ElButton @click="props.handleCancel">
          {{ $t("common.取消") }}
        </ElButton>
        <ElButton
          :loading="confirmBtnLoading"
          type="primary"
          @click="handleSubmit"
        >
          {{ $t("common.确认") }}
        </ElButton>
      </div>
    </template>
  </ElDialog>
</template>

<script lang="ts" setup>
import {
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElRadioGroup,
  ElRadio,
  ElButton,
  ElMessage,
} from "element-plus";
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import emailjs from "@emailjs/browser";
import { useUserStore } from "@/stores/modules/user";
const { t } = useI18n();
const formRef = ref();
const props = defineProps<{
  handleOK: any;
  handleCancel: any;
}>();
enum FeedType {
  CONFUSION = "CONFUSION",
  BUG = "BUG",
  PURCHASE = "PURCHASE",
  OTHER = "OTHER",
}
const formData = ref<{
  feedType: FeedType;
  title: string;
  contact: string;
  content: string;
}>({
  feedType: FeedType.CONFUSION,
  title: "",
  contact: "",
  content: "",
});
const formRules = {
  feedType: [
    {
      required: true,
      message: t("common.请选择反馈类型"),
      trigger: ["change", "blur"],
    },
  ],
  title: [
    {
      required: true,
      message: t("common.请输入标题"),
      trigger: ["change", "blur"],
    },
  ],
  contact: [
    {
      required: true,
      message: t("common.请输入联系方式"),
      trigger: ["change", "blur"],
    },
  ],
  content: [
    {
      required: true,
      message: t("common.请输入反馈内容"),
      trigger: ["change", "blur"],
    },
  ],
};
const dialogVisible = ref<boolean>(false);
onMounted(() => {
  dialogVisible.value = true;
});

const confirmBtnLoading = ref<boolean>(false);
const userStore = useUserStore();
const handleSubmit = () => {
  formRef.value.validate((valid: boolean) => {
    if (!valid) {
      return;
    } else {
      if (formData.value.feedType === FeedType.OTHER) {
        dialogVisible.value = false;
        props.handleOK();
      } else {
        confirmBtnLoading.value = true;
        emailjs
          .send(
            "service_6kouf5v",
            "template_ozxhvu7",
            {
              from_name: userStore.userInfo?.sub,
              message: formData.value.content,
              to_name: "DP",
              title: formData.value.title,
              contact: formData.value.contact,
              type: formData.value.feedType,
              content: formData.value.content,
            },
            "7xk8wAHAJQa6sT_FS"
          )
          .then(
            (result) => {
              ElMessage.success(t("common.提交成功"));
              props.handleOK();
            },
            (error) => {
              console.log(error.text);
            }
          )
          .finally(() => {
            confirmBtnLoading.value = false;
            dialogVisible.value = false;
          });
      }
    }
  });
};
</script>

<style lang="scss" scoped></style>
