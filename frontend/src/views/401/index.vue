<template>
  <div :class="['flex', 'flex-col', 'h-screen']">
    <header class="login-header">
      <img
        width="183"
        height="40"
        :class="['object-contain']"
        src="@/assets/img/logo.png"
        alt=""
      />
    </header>
    <div
      :class="['flex-1', 'h-0', 'w-full', 'flex', 'flex-col', 'items-center']"
    >
      <div :class="['text-h6', 'text-4xl']">
        <!-- 500 internal server error-->
        401 unauthorized access
      </div>
      <div :class="['text-label']">
        You are not authorized to access this page.
      </div>
      <div
        :class="[
          'flex',
          'my-16',
          'justify-center',
          'justify-center',
          'flex-1',
          'h-0',
        ]"
      >
        <img src="/401.png" alt="" :class="['object-contain']" />
      </div>
      <div :class="['mb-14']">
        <ElButton size="large" type="primary" @click="handleBack"
          >go to home</ElButton
        >
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ElButton } from "element-plus";
import { useRouter } from "vue-router";
const router = useRouter();
const handleBack = () => {
  if (import.meta.env.VITE_IS_BOHRIUM) router.push({ name: "taskManage" });
  else {
    router.push({
      name: "login",
    });
  }
};
</script>

<style lang="scss" scoped></style>
