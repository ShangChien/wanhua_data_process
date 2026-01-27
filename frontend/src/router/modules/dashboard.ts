import Layout from "@/components/layout/index.vue";
import type { RouteRecordRaw } from "vue-router";
import TaskManage from "@/views/task-manage/index.vue";
import TaskDetail from "@/views/task-detail/index.vue";
import PredictResult from "@/views/predict-result/index.vue";
const routeRecordList: RouteRecordRaw[] = [
  {
    path: "/dashboard",
    component: Layout,
    name: "dashboard",
    redirect: {
      name: "taskManage",
    },
    children: [
      {
        path: "task-manage",
        name: "taskManage",
        component: TaskManage,
      },
      {
        path: "create-task",
        name: "createTask",
        component: () => import("@/views/create-task/index.vue"),
        meta: {
          breadcrumb: [
            { name: "common.任务管理", path: "taskManage" },
            { name: "common.创建任务", path: "createTask" },
          ],
        },
      },
      {
        path: "task-detail",
        name: "taskDetail",
        component: TaskDetail,
        meta: {
          breadcrumb: [
            { name: "common.任务管理", path: "taskManage" },
            { name: "common.训练任务详情", path: "taskDetail" },
          ],
        },
      },
      {
        path: "task-predict",
        name: "taskPredict",
        component: () => import("@/views/task-predict/index.vue"),
        meta: {
          breadcrumb: [
            { name: "common.任务管理", path: "taskManage" },
            { name: "common.创建预测任务", path: "taskPredict" },
          ],
        },
      },
      {
        path: "predict-result",
        name: "predictResult",
        component: PredictResult,
        meta: {
          breadcrumb: [
            { name: "common.任务管理", path: "taskManage" },
            { name: "common.预测任务详情", path: "predictResult" },
          ],
        },
      },
    ],
  },
];

export default routeRecordList;
