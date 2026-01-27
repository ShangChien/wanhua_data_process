<template>
  <div>
    <header class="login-header">
      <ElSpace class="logo">
        <img
          width="183"
          height="40"
          :class="['object-contain']"
          src="@/assets/img/logo.png"
          alt=""
        />
      </ElSpace>
    </header>
    <main>
      <div class="login-container">
        <div class="title-container">
          <!-- <h1 class="title margin-no">登陆到</h1> -->
          <h1 class="title">Uni QSAR</h1>
          <div class="sub-title">
            <p class="tip">
              {{ actionType == "register" ? "已有账号?" : "没有账号吗?" }}
            </p>
            <p class="tip" @click="switchType">
              &nbsp;{{ actionType == "register" ? " 登陆" : "注册新账号" }}
            </p>
          </div>
        </div>
        <LoginForm v-if="actionType === 'login'" />
        <RegisterForm v-else />
      </div>
    </main>
    <footer class="footer">
      Copyright @ 2024 Uni-QSAR All Rights Reserved
    </footer>
  </div>
</template>

<script lang="ts" setup>
import { getQSARToken, getQSARTokenByApp } from "@/service/api/user";
import { useUserStore } from "@/stores/modules/user";
import { ElSpace } from "element-plus";
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import LoginForm from "./LoginForm.vue";
import RegisterForm from "./RegisterForm.vue";
const userStore = useUserStore();
const route = useRoute();

type ActionType = "login" | "register";
const router = useRouter();
const actionType = ref<ActionType>("login");
const switchType = () => {
  actionType.value = actionType.value === "login" ? "register" : "login";
};
const jumpToDashboard = () => {
  const url = new URL(window.location.href);
  const queryParams = url.searchParams;
  const urlToken = queryParams.get("token") ?? "";
  if (urlToken) {
    userStore.setToken(urlToken);
    getQSARToken().then((res) => {
      userStore.setToken(res.data.data);
      router.push({ name: "dashboard" });
    });
  }
};
jumpToDashboard();
</script>

<style lang="scss" scoped>
@import "@/assets/variables.scss";
.login-header {
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(5px);
  color: #000000e6;
  height: 56px;
  .logo {
    font-size: 28px;
    letter-spacing: -1px;
    font-style: italic;
    font-weight: 600;
  }
}
.login-wrapper {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-size: cover;
  background-position: 100%;
  position: relative;
}

.login-container {
  position: absolute;
  top: 22%;
  left: 5%;
  min-height: 500px;
}

.title-container {
  .title {
    color: #000000e6;

    margin-top: 36px;

    &.margin-no {
      margin-top: 0;
    }
  }

  .sub-title {
    margin-top: 16px;

    .tip {
      font-size: 14px;
      display: inline-block;
      margin-right: 8px;

      &:first-child {
        color: #0009;
      }

      &:last-child {
        color: $primary-color;
        cursor: pointer;
      }
    }
  }
}
.footer {
  position: absolute;
  left: 5%;
  bottom: 64px;
  color: rgba(0, 0, 0, 0.6);
}
@media screen and (height <= 700px) {
  .footer {
    display: none;
  }
}
</style>
