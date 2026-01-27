import type { PageVO } from "@/types/page";
import { ref } from "vue";

const usePageVO = () => {
  const pageVO = ref<PageVO>({
    total: 0,
    currentPage: 1,
    pageSize: 20,
  });
  const paginationProp = {
    background: true,
    size: "small",
    layout: ["total", "->", "pager", "sizes", "jumper"].join(","),
    pageSizes: [20, 30, 40, 50],
  };
  return {
    pageVO,
    paginationProp,
  };
};

export default usePageVO;
