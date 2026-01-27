<template>
  <ElDialog
    :model-value="visible"
    :title="$t('common.收费提醒标题')"
    width="600px"
    @close="handleClose"
  >
    <div class="charging-notification">
      <div class="content">
        <p class="main-text">{{ $t("common.收费提醒内容") }}</p>

        <div class="details-section">
          <h4>{{ $t("common.收费详情标题") }}</h4>
          <ul class="details-list">
            <li>{{ $t("common.任务创建收费说明") }}</li>
            <li>{{ $t("common.模型清理周期说明") }}</li>
            <li>{{ $t("common.数据安全提醒") }}</li>
          </ul>
        </div>

        <p class="contact-info">{{ $t("common.联系客服") }}</p>
      </div>
    </div>
  </ElDialog>
</template>

<script lang="ts" setup>
import { ElDialog, ElButton, ElIcon } from "element-plus";
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps<{
  visible: boolean;
}>();
const { t } = useI18n();

const emit = defineEmits<{
  resolve: [];
  reject: [];
}>();

const handleClose = () => {
  //   visible.value = false;
  emit("resolve");
};

const handleViewDetails = () => {
  // 可以跳转到详细的收费说明页面或打开另一个弹窗
  //   visible.value = false;
  emit("resolve");
};
</script>

<style scoped>
.charging-notification {
  padding: 20px 0;
}

.icon-wrapper {
  text-align: center;
  margin-bottom: 20px;
}

.content {
  text-align: left;
}

.main-text {
  font-size: 16px;
  color: #303133;
  margin-bottom: 20px;
  line-height: 1.6;
}

.details-section {
  background-color: #fdf6ec;
  border: 1px solid #fcdcb8;
  border-radius: 6px;
  padding: 16px;
  margin: 20px 0;
}

.details-section h4 {
  color: #e6a23c;
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

.details-list {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.details-list li {
  color: #606266;
  font-size: 14px;
  line-height: 1.8;
  margin-bottom: 8px;
  position: relative;
  padding-left: 16px;
}

.details-list li::before {
  content: "•";
  color: #e6a23c;
  font-weight: bold;
  position: absolute;
  left: 0;
}

.contact-info {
  color: #909399;
  font-size: 14px;
  text-align: center;
  margin-top: 20px;
  margin-bottom: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
