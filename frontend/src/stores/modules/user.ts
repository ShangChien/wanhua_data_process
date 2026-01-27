import { defineStore } from "pinia";
import { LocalStorageKeys } from "@/constants/storage";
import { jwtDecode, type JwtPayload } from "jwt-decode";

export type TabPageState = {
  token: null | string;
};

export const useUserStore = defineStore("userStore", {
  state(): TabPageState {
    return {
      token: null,
    };
  },
  getters: {
    userInfo(state): JwtPayload | null {
      if (state.token !== null) {
        try {
          const ret = jwtDecode(state.token);
          return ret;
        } catch (error) {
          return null;
        }
      }
      return null;
    },
  },
  actions: {
    setToken(token: string) {
      this.token = token;
      if (import.meta.env.VITE_IS_BOHRIUM) {
      } else localStorage.setItem(LocalStorageKeys.tokenKey, token);
    },
    resetToken() {
      this.token = null;
      localStorage.removeItem(LocalStorageKeys.tokenKey);
    },
    initToken() {
      if (import.meta.env.VITE_IS_BOHRIUM) {
      } else {
        const token = localStorage.getItem(LocalStorageKeys.tokenKey);
        if (token !== null) {
          this.token = token;
        }
      }
    },
  },
});
