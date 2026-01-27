import { useRouter } from "vue-router";

export const useNavigation = () => {
  const router = useRouter();
  const jumpToTaskDetailPage = (taskId: string) => {
    router.push({
      name: "taskDetail",
      query: {
        taskId,
      },
    });
  };
  return {
    jumpToTaskDetailPage,
  };
};
