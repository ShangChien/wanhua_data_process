<template>
  <ElForm
    ref="formRef"
    :class="['item-container']"
    :model="formData"
    :rules="formRules"
    label-width="0"
    hide-required-asterisk
  >
    <template v-if="registerType == 'phone'">
      <ElFormItem prop="phone">
        <ElInput
          v-model="formData.phone"
          :maxlength="11"
          size="large"
          placeholder="请输入您的手机号"
        >
          <template #prefix>
            <Icon icon="streamline:phone-mobile-phone"></Icon>
          </template>
        </ElInput>
      </ElFormItem>
    </template>

    <template v-if="registerType === 'email'">
      <ElFormItem prop="email">
        <ElInput
          v-model="formData.email"
          type="text"
          size="large"
          placeholder="请输入您的邮箱"
        >
          <template #prefix>
            <Icon icon="ic:baseline-email"></Icon>
          </template>
        </ElInput>
      </ElFormItem>
    </template>

    <template v-if="registerType === 'username'">
      <ElFormItem prop="username">
        <ElInput
          v-model.trim="formData.username"
          type="text"
          size="large"
          placeholder="请输入用户名"
        >
          <template #prefix>
            <Icon icon="ic:baseline-email"></Icon>
          </template>
        </ElInput>
      </ElFormItem>
    </template>

    <ElFormItem prop="password">
      <ElInput
        v-model="formData.password"
        size="large"
        clearable
        placeholder="请输入登录密码"
      >
        <template #prefix>
          <Icon icon="material-symbols:lock-outline"></Icon>
        </template>
      </ElInput>
    </ElFormItem>

    <template v-if="registerType == 'phone'">
      <ElFormItem class="verification-code" name="verifyCode">
        <ElInput
          class="code-input"
          v-model="formData.verifyCode"
          size="large"
          placeholder="请输入验证码"
        />
        <ElButton
          class="code-button"
          size="large"
          :disabled="countDown > 0"
          @click="handleCounter"
        >
          {{ countDown == 0 ? "发送验证码" : `${countDown}秒后可重发` }}
        </ElButton>
      </ElFormItem>
    </template>

    <!-- <ElFormItem class="check-container" prop="checked">
      <ElCheckbox v-model="formData.checked">我已阅读并同意 </ElCheckbox>
      &nbsp;<span class="tip">服务协议</span> 和 &nbsp;<span class="tip"
        >隐私声明</span
      >
    </ElFormItem> -->

    <ElFormItem class="btn-container">
      <ElButton class="login-btn" @click="onSubmit" type="primary">
        注册
      </ElButton>
    </ElFormItem>

    <!-- <div class="switch-container">
      <span class="tip" @click="switchType">{{
        registerType === "phone" ? "使用邮箱注册" : "使用手机号注册"
      }}</span>
    </div> -->
  </ElForm>
</template>

<script lang="ts" setup>
import { Icon } from "@iconify/vue";
import {
  ElButton,
  ElCheckbox,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  type FormInstance,
  type FormRules,
} from "element-plus";
import { ref } from "vue";

import { register } from "@/service/api/user";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/modules/user";

type RegisterType = "phone" | "email" | "username";

const router = useRouter();

const formRef = ref<FormInstance>();
const getInitFormData = () => ({
  phone: "",
  email: "",
  username: "",
  password: "",
  verifyCode: "",
  checked: "",
});
const registerType = ref<RegisterType>("username");
const formData = ref(getInitFormData());

const validateUsername = (rule: any, value: string, callback: any) => {
  if (value.includes("_")) {
    callback(new Error("用户名不可以包含下划线"));
  } else {
    callback();
  }
};

const formRules = {
  phone: [
    { required: true, message: "手机号必填", trigger: ["blur", "change"] },
  ],
  email: [{ required: true, message: "邮箱必填", trigger: ["blur", "change"] }],
  username: [
    {
      required: true,
      trigger: ["blur", "change"],
      validator: validateUsername,
    },
  ],
  password: [
    { required: true, message: "密码必填", trigger: ["blur", "change"] },
  ],
  verifyCode: [
    { required: true, message: "验证码必填", trigger: ["blur", "change"] },
  ],
};
const userStore = useUserStore();
const onSubmit = () => {
  if (!formRef.value) return;
  formRef.value.validate((valid) => {
    if (valid) {
      {
        const params = new FormData();
        params.append("username", formData.value.username);
        params.append("password", formData.value.password);
        register(params).then((res) => {
          userStore.setToken(res.data.data);
          ElMessage.success("注册成功");
          router.push({ name: "dashboard" });
        });
      }
    }
  });
};
const switchType = () => {
  registerType.value = registerType.value === "email" ? "phone" : "email";
};
const countDown: number = 0;
const handleCounter = () => {};
</script>

<style lang="scss" scoped>
@import url(./style.scss);
</style>
