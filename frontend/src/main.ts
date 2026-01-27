import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "@/assets/main.scss";
import VxeTable from "vxe-table";
import "vxe-table/lib/style.css";
import VxeUI from "vxe-pc-ui";
import "vxe-pc-ui/lib/style.css";
import NProgress from "nprogress";
import i18n from "./locale";
import "viewerjs/dist/viewer.css";
import VueViewer from "v-viewer";
import VueVirtualScroller from "vue-virtual-scroller";
import "vue-virtual-scroller/dist/vue-virtual-scroller.css";

// document.cookie = "appAccessKey=sk-a10f66d9e76047de87e62c8a2865368f;path=/";
// document.cookie = "clientName=uni-aims-uuid1724472302;path=/";

NProgress.configure({ showSpinner: false });
const app = createApp(App);
app.use(createPinia());
app.use(VueViewer);
app.use(router);
app.use(VxeUI);
app.use(VxeTable);
app.use(i18n);
app.use(VueVirtualScroller);
app.mount("#app");
