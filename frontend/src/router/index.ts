import {
  createRouter,
  createWebHashHistory,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";
import NProgress from "nprogress"; // progress bar
import "nprogress/nprogress.css";
import { clearCompList } from "@/components/modal/ModalContainer.vue";
export function mapModuleRouterList(
  modules: Record<string, unknown>
): RouteRecordRaw[] {
  const routerList: RouteRecordRaw[] = [];
  Object.keys(modules).forEach((key) => {
    // @ts-ignore
    const mod = modules[key].default || {};
    const modList = Array.isArray(mod) ? [...mod] : [mod];
    routerList.push(...modList);
  });
  return routerList;
}

const routeModules = import.meta.glob("./modules/*.ts", { eager: true });
export const fixedRouterList: RouteRecordRaw[] =
  mapModuleRouterList(routeModules);

const defaultRouterList = [
  {
    path: "/",
    name: "home",
    redirect: {
      name: import.meta.env.VITE_IS_BOHRIUM ? "dashboard" : "login",
    },
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/login/index.vue"),
  },
  {
    path: "/test",
    name: "test",
    component: () => import("@/views/test/index.vue"),
  },
  {
    path: "/401",
    name: "401",
    component: () => import("@/views/401/index.vue"),
  },
];
export const allRoutes = [...defaultRouterList, ...fixedRouterList];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: allRoutes,
  scrollBehavior() {
    return {
      el: "#app",
      top: 0,
      behavior: "smooth",
    };
  },
});
router.beforeEach((to, from, next) => {
  NProgress.start();
  next();
});
router.afterEach(() => {
  clearCompList();
  NProgress.done();
});
export default router;
