<template>
  <ElForm
    ref="formRef"
    :class="['item-container']"
    :model="formData"
    :rules="formRules"
    label-width="0"
    hide-required-asterisk
  >
    <ElFormItem prop="account">
      <ElInput
        v-model="formData.account"
        size="large"
        clearable
        :placeholder="`请输入账号`"
      >
        <template #prefix>
          <Icon icon="mingcute:user-2-fill"></Icon>
        </template>
      </ElInput>
    </ElFormItem>

    <ElFormItem prop="password">
      <ElInput
        type="password"
        size="large"
        show-password
        v-model="formData.password"
        clearable
        :placeholder="`请输入密码`"
        @keydown.enter.native="handleSubmit"
      >
        <template #prefix>
          <Icon icon="material-symbols:lock-outline"></Icon>
        </template>
      </ElInput>
    </ElFormItem>

    <div class="check-container remember-pwd">
      <ElCheckbox class="check-tip">记住密码</ElCheckbox>
      <span class="tip">忘记密码</span>
    </div>
    <ElFormItem class="btn-container">
      <ElButton class="login-btn" type="primary" @click="handleSubmit">
        登陆
      </ElButton>
    </ElFormItem>
    <div
      :class="['flex', 'items-center', 'justify-between', 'switch-container']"
    >
      <div :class="['tip', '!cursor-default']">其他登陆方式</div>
      <ElTooltip effect="dark" content="使用 Bohrium 账号登陆" placement="top">
        <ElButton link @click="loginByBohrium">
          <img
            src="/bohrium.png"
            width="34"
            height="34"
            :class="['object-contain']"
            alt=""
          />
        </ElButton>
      </ElTooltip>
    </div>
  </ElForm>
</template>

<script lang="ts" setup>
import { login } from "@/service/api/user";
import { useUserStore } from "@/stores/modules/user";
import { Icon } from "@iconify/vue/dist/iconify.js";
import {
  ElButton,
  ElCheckbox,
  ElForm,
  ElFormItem,
  ElInput,
  ElTooltip,
  type FormInstance,
} from "element-plus";
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const userStore = useUserStore();

const getInitFormData = () => ({
  account: "",
  password: "",
  checked: false,
});
const formRules = {
  account: [
    {
      required: true,
      message: "请输入账号",
      trigger: ["blur", "change"],
    },
  ],
  password: [
    {
      required: true,
      message: "请输入密码",
      trigger: ["blur", "change"],
    },
  ],
};
const formData = ref(getInitFormData());
const formRef = ref<FormInstance>();
const handleSubmit = () => {
  if (!formRef.value) return;
  formRef.value.validate((valid) => {
    if (valid) {
      const loginFormData = new FormData();
      loginFormData.append("username", formData.value.account);
      loginFormData.append("password", formData.value.password);

      login(loginFormData).then((res) => {
        userStore.setToken(res.data.data);
        router.push({
          name: "dashboard",
        });
      });
    }
  });
};
const loginByBohrium = () => {
  // const url =
  //   "https://platform.dp.tech/login?business=Bohrium&lang=zh-cn&redirect=http://localhost:3000/";
  const baseUrl = "https://platform.dp.tech/login";
  const url = new URL(baseUrl);
  const searchParams = new URLSearchParams({
    business: "UniQSAR",
    lang: "zh-cn",
    redirect: `${window.location.protocol}//${window.location.host}`,
  });
  url.search = searchParams.toString();
  window.location.href = url.toString();
};
</script>

<style lang="scss" scoped>
@import url(./style.scss);
</style>
