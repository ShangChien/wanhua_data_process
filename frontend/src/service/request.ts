import type { InternalAxiosRequestConfig } from "axios";
import axios from "axios";
import { ElMessage } from "element-plus";
import NProgress from "nprogress";
import { useUserStore } from "@/stores/modules/user";
import router from "@/router";
enum ResCode {
  success = 0,
  error = -1,
}
export type ResponseWrapper<T> = {
  data: T;
  code: ResCode;
  msg: string;
};

const AppAxios = axios.create({
  // withCredentials: true,
  // baseURL: "http://127.0.0.1:8000",
  // baseURL: import.meta.env.VITE_REQUEST_BASE_URL,
  baseURL: "/AIMSapi",
  // withCredentials: true,
});
AppAxios.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const userStore = useUserStore();
    if (userStore.token !== null) {
      config.headers.Authorization = `Bearer ${userStore.token}`;
    }
    return config;
  },
  (error) => {
    // do something
    return Promise.reject(error);
  }
);

AppAxios.interceptors.response.use(
  (response) => {
    NProgress.done();
    if (response.config.responseType === "arraybuffer") {
      try {
        const text = new TextDecoder("utf-8").decode(response.data);
        const json = JSON.parse(text);
        debugger;
        // 如果解析成功并且 code 是错误码，进入错误处理逻辑
        if (json.code === ResCode.error) {
          if (!response.config.ignoreDefaultErrorToast) {
            ElMessage.error({
              message: json.msg || "Response Error",
              duration: 5 * 1000,
            });
          }
          return Promise.reject(json);
        }
      } catch (e) {
        // 如果解析失败，直接返回原始响应
        return response;
      }
    }
    if (response.data.code === ResCode.error) {
      if (!response.config.ignoreDefaultErrorToast)
        ElMessage.error({
          message: response.data.msg || "Response Error",
          duration: 5 * 1000,
        });
      return Promise.reject(response);
    }
    return response;
  },
  (error) => {
    if (error.response.status === 401) {
      const userStore = useUserStore();
      ElMessage.error({
        message: "Unauthorized",
        duration: 5 * 1000,
      });
      userStore.resetToken();
      router.push({
        name: import.meta.env.VITE_IS_BOHRIUM ? "401" : "login",
      });
      // redirect to login page
      // removeToken();
      return Promise.reject(error);
    }
    ElMessage.error({
      message: error.msg || "Response Error",
      duration: 5 * 1000,
    });
    return Promise.reject(error);
  }
);
export default AppAxios;
