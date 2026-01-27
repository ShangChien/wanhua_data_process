<!-- <template>
  <Editor
    api-key="tiphp71whqcnzvkcwj5ls1fe3hvqtvldcy49yjm93bytj7wd"
    :modelValue="modelValue"
    @update:modelValue="emit('update:modelValue', $event)"
    :init="init"
  ></Editor>
</template>
<script setup lang="ts">
import { onMounted } from "vue";
import tinymce from "tinymce/tinymce";
import "tinymce/models/dom";
import "tinymce/themes/silver/theme";
import Editor from "@tinymce/tinymce-vue";
import "tinymce/icons/default";
import "tinymce/plugins/image";
import "tinymce/plugins/link";
import "tinymce/plugins/code";
import "tinymce/plugins/table";
import "tinymce/plugins/lists";
import "tinymce/plugins/wordcount";

const { modelValue } = defineProps<{ modelValue: string }>();
const emit = defineEmits<{ (e: "update:modelValue", value: string) }>();

const init = {
  language_url: "/tinymce/langs/zh-Hans.js",
  language: "zh-Hans",
  skin_url: "/tinymce/skins/ui/oxide",
  height: 300,
  plugins: "link lists image code table wordcount",
  toolbar:
    "bold italic underline strikethrough | fontsizeselect | forecolor backcolor | alignleft aligncenter alignright alignjustify | bullist numlist | outdent indent blockquote | undo redo | link unlink image code | removeformat",
  branding: false,
  menubar: true,
  content_css: "/tinymce/skins/content/default/content.css",
};

onMounted(() => {
  tinymce.init({});
});
</script> -->
