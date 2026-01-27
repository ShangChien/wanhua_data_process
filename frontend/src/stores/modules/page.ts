import { defineStore } from "pinia";

export type TabPageState = {
  hasMenu: boolean;
  menuCollapsed: boolean;
  hasNav: boolean;
  settingDrawerVisible: boolean;
};

export const useTabPageStore = defineStore("pageStore", {
  state(): TabPageState {
    return {
      hasMenu: false,
      menuCollapsed: true,
      hasNav: true,
      settingDrawerVisible: false,
    };
  },
  actions: {
    toggleTheme() {},
    toggleMenuCollapse() {
      this.menuCollapsed = !this.menuCollapsed;
    },
    toggleSettingDrawerVisible() {
      this.settingDrawerVisible = !this.settingDrawerVisible;
    },
    resetStore() {
      this.$reset();
    },
    updateStore(payload: Partial<TabPageState>) {
      this.$patch(payload);
    },
  },
});
