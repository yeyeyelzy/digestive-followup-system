<template>
  <div class="chat-page">
    <aside class="chat-sidebar">
      <div class="sidebar-title">聊天列表</div>
      <el-input
        v-model="conversationQuery"
        placeholder="搜索聊天对象"
        size="small"
        clearable
        prefix-icon="el-icon-search"
      />

      <div class="conversation-list">
        <div
          v-for="item in filteredConversationList"
          :key="item.conversationKey"
          class="conversation-item"
          :class="{
            active: activeConversation && activeConversation.conversationKey === item.conversationKey,
            'has-unread': item.unreadCount > 0
          }"
          @click="setActiveConversation(item.conversationKey)"
        >
          <div class="conversation-top">
            <span class="name">{{ item.displayName }}</span>
            <span class="time">{{ formatTime(item.lastTime) }}</span>
          </div>
          <div class="conversation-bottom">
            <span class="preview">{{ item.lastPreview || '暂无消息' }}</span>
            <el-badge v-if="item.unreadCount > 0" :value="item.unreadCount" class="unread-badge" />
          </div>
        </div>
      </div>
    </aside>

    <section class="chat-main">
      <header class="chat-header">
        <span>{{ activeConversation ? activeConversation.displayName : '请选择聊天对象' }}</span>
      </header>

      <div class="history-toolbar">
        <el-input
          v-model="historyKeyword"
          placeholder="按关键词查找聊天记录"
          size="small"
          clearable
          @change="applyHistoryFilter"
          @keyup.enter.native="applyHistoryFilter"
        />
        <el-date-picker
          v-model="historyDateRange"
          size="small"
          type="daterange"
          value-format="yyyy-MM-dd"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="applyHistoryFilter"
        />
        <el-button size="small" type="primary" @click="applyHistoryFilter">查找</el-button>
        <el-button size="small" @click="resetHistoryFilter">重置</el-button>
      </div>

      <div class="msg-box" ref="msgBox">
        <div
          v-for="msg in chatList"
          :key="msg.id"
          class="msg-row"
          :class="{ self: isSelfMessage(msg) }"
        >
          <div class="bubble">
            <template v-if="isAttachmentMessage(msg.content)">
              <template v-if="parseAttachment(msg.content).kind === 'image'">
                <a
                  :href="parseAttachment(msg.content).url"
                  target="_blank"
                  rel="noopener noreferrer"
                  @click.prevent="openAttachment(parseAttachment(msg.content))"
                >
                  <img class="msg-image" :src="parseAttachment(msg.content).url" :alt="parseAttachment(msg.content).name" />
                </a>
              </template>
              <template v-else-if="parseAttachment(msg.content).kind === 'video'">
                <video class="msg-video" controls :src="parseAttachment(msg.content).url"></video>
              </template>
              <template v-else>
                <a
                  :href="parseAttachment(msg.content).url"
                  target="_blank"
                  rel="noopener noreferrer"
                  @click.prevent="openAttachment(parseAttachment(msg.content))"
                >
                  {{ parseAttachment(msg.content).name }}
                </a>
              </template>
            </template>
            <template v-else>
              {{ msg.content }}
            </template>
            <div class="msg-time">{{ formatTime(msg.time) }}</div>
          </div>
        </div>
      </div>

      <div class="input-box">
        <el-upload
          class="upload-btn"
          :action="uploadUrl"
          :show-file-list="false"
          :http-request="uploadAttachment"
          accept="image/*,video/*,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.zip,.rar"
          :before-upload="beforeAttachmentUpload"
        >
          <el-button size="mini" icon="el-icon-paperclip">发送文件</el-button>
        </el-upload>
        <el-input
          v-model="contentText"
          placeholder="请输入消息"
          size="small"
          @keyup.enter.native="sendText"
        />
        <el-button type="primary" size="small" :disabled="!contentText || !activeConversation" @click="sendText">发送</el-button>
      </div>
    </section>
  </div>
</template>

<script>
import { listChat, addChat } from "@/api/system/chat";
import { listPatient } from "@/api/system/patient";
import { getToken } from "@/utils/auth";
import request from "@/utils/request";

const BLOCKED_PATIENT_NAMES = ["p0315161650", "chat_test"];

export default {
  name: "Chat",
  data() {
    return {
      loading: false,
      conversationQuery: "",
      historyKeyword: "",
      historyDateRange: [],
      contentText: "",
      chatList: [],
      rawChatList: [],
      conversationList: [],
      activeConversation: null,
      pollTimer: null,
      incomingSeenMap: {},
      initializedSeen: false,
      chatMode: "doctor",
      chatModeLocked: false,
      currentPatientId: null,
      currentUserId: null,
      uploadUrl: process.env.VUE_APP_BASE_API + "/common/upload",
    };
  },
  computed: {
    outgoingDirection() {
      return this.chatMode === "doctor" ? 1 : 2;
    },
    filteredConversationList() {
      const keyword = (this.conversationQuery || "").trim().toLowerCase();
      if (!keyword) {
        return this.conversationList;
      }
      return this.conversationList.filter((item) =>
        (item.displayName || "").toLowerCase().includes(keyword)
      );
    },
  },
  created() {
    this.initializeChat();
  },
  beforeDestroy() {
    this.stopPolling();
  },
  methods: {
    async initializeChat() {
      await this.loadCurrentUser();
      await this.refreshConversations(true);
      this.startPolling();
    },

    async loadCurrentUser() {
      try {
        const userResp = await request({ url: "/getInfo", method: "get" });
        const user = (userResp && userResp.user) || {};
        this.currentUserId = user.userId || null;
      } catch (e) {
        this.currentUserId = null;
      }
    },

    startPolling() {
      this.stopPolling();
      this.pollTimer = setInterval(() => {
        this.refreshConversations(false);
      }, 3000);
    },

    stopPolling() {
      if (this.pollTimer) {
        clearInterval(this.pollTimer);
        this.pollTimer = null;
      }
    },

    async refreshConversations(isFirstLoad) {
      try {
        this.loading = true;
        let patientRes = { rows: [] };
        try {
          patientRes = await listPatient({ pageNum: 1, pageSize: 500 });
        } catch (e) {
          patientRes = { rows: [] };
        }
        const chatRes = await listChat({ pageNum: 1, pageSize: 3000 });

        const patients = (patientRes.rows || []).filter(
          (p) => !BLOCKED_PATIENT_NAMES.includes(p.patientName)
        );
        const chatRows = (chatRes.rows || []).filter(
          (c) => !BLOCKED_PATIENT_NAMES.includes(c.patientName)
        );

        this.chatMode = this.resolveChatMode(chatRows);
        this.currentPatientId = this.chatMode === "patient" ? this.currentUserId : null;

        const nextConversationList = this.chatMode === "doctor"
          ? this.buildDoctorConversationList(patients, chatRows)
          : this.buildPatientConversationList(chatRows);

        nextConversationList.sort((a, b) => this.getTimestamp(b.lastTime) - this.getTimestamp(a.lastTime));

        this.conversationList = nextConversationList;
        this.initializedSeen = true;

        if (!this.activeConversation && this.conversationList.length) {
          const routeName = this.$route.params.patientName;
          const target = this.conversationList.find((x) => x.displayName === routeName) || this.conversationList[0];
          this.setActiveConversation(target.conversationKey, true);
        } else if (this.activeConversation) {
          const updated = this.conversationList.find((x) => x.conversationKey === this.activeConversation.conversationKey);
          if (updated) {
            this.activeConversation = updated;
            this.rawChatList = updated.messages || [];
            this.applyHistoryFilter();
            this.markActiveConversationAsRead();
          }
        }

        if (!isFirstLoad) {
          this.notifyNewIncoming(nextConversationList);
        }
      } finally {
        this.loading = false;
      }
    },

    notifyNewIncoming(nextConversationList) {
      nextConversationList.forEach((item) => {
        if (this.activeConversation && item.conversationKey === this.activeConversation.conversationKey) {
          return;
        }
        if (item.unreadCount > 0) {
          this.$notify({
            title: "新消息",
            message: `${item.displayName} 有 ${item.unreadCount} 条未读消息`,
            type: "warning",
            duration: 2000,
          });
        }
      });
    },

    buildDoctorConversationList(patients, chatRows) {
      const patientRows = (patients || []).filter((p) => p && p.patientId != null);
      const conversationPatients = [];
      const added = new Set();

      patientRows.forEach((p) => {
        const pid = String(p.patientId);
        if (!added.has(pid)) {
          conversationPatients.push({ patientId: p.patientId, patientName: p.patientName || "" });
          added.add(pid);
        }
      });

      // 当患者主列表接口为空时，回退到聊天记录中的患者维度，避免左侧无会话。
      if (!conversationPatients.length) {
        (chatRows || []).forEach((row) => {
          const pid = row && row.patientId != null ? String(row.patientId) : "";
          if (!pid || added.has(pid)) {
            return;
          }
          const pname = String(row.patientName || "").trim();
          if (!pname || BLOCKED_PATIENT_NAMES.includes(pname)) {
            return;
          }
          conversationPatients.push({ patientId: row.patientId, patientName: pname });
          added.add(pid);
        });
      }

      return conversationPatients.map((patient) => {
        const pid = String(patient.patientId);
        const key = `p:${pid}`;
        const messages = (chatRows || [])
          .filter((row) => String(row.patientId || "") === pid)
          .sort((a, b) => this.getTimestamp(a.time) - this.getTimestamp(b.time));

        const last = messages.length ? messages[messages.length - 1] : null;
        const lastIncomingId = this.getLastIncomingId(messages);
        if (!this.initializedSeen && lastIncomingId > 0) {
          this.incomingSeenMap[key] = lastIncomingId;
        }
        const seen = this.incomingSeenMap[key] || 0;
        const unreadCount = this.countIncomingAfter(messages, seen);

        return {
          conversationKey: key,
          displayName: patient.patientName || `患者${pid}`,
          patientId: patient.patientId,
          patientName: patient.patientName || "",
          doctorId: last && last.doctorId ? last.doctorId : 1,
          doctorName: last && last.doctorName ? last.doctorName : "陈亮",
          lastTime: last ? last.time : null,
          lastPreview: last ? this.previewContent(last.content) : "",
          unreadCount,
          messages,
        };
      });
    },

    buildPatientConversationList(chatRows) {
      const ownRows = (chatRows || []).filter((row) => {
        if (this.currentPatientId == null) {
          return true;
        }
        return String(row.patientId || "") === String(this.currentPatientId);
      });

      const grouped = {};
      ownRows.forEach((row) => {
        const key = row.doctorId != null ? `d:${row.doctorId}` : `dname:${row.doctorName || "医生"}`;
        if (!grouped[key]) {
          grouped[key] = [];
        }
        grouped[key].push(row);
      });

      return Object.keys(grouped).map((groupKey) => {
        const messages = grouped[groupKey].sort((a, b) => this.getTimestamp(a.time) - this.getTimestamp(b.time));
        const last = messages.length ? messages[messages.length - 1] : null;
        const lastIncomingId = this.getLastIncomingId(messages);
        if (!this.initializedSeen && lastIncomingId > 0) {
          this.incomingSeenMap[groupKey] = lastIncomingId;
        }
        const seen = this.incomingSeenMap[groupKey] || 0;
        const unreadCount = this.countIncomingAfter(messages, seen);
        const doctorName = (last && last.doctorName) || "医生";

        return {
          conversationKey: groupKey,
          displayName: doctorName,
          patientId: this.currentPatientId || (last ? last.patientId : null),
          patientName: last ? last.patientName : "",
          doctorId: last ? last.doctorId : 1,
          doctorName,
          lastTime: last ? last.time : null,
          lastPreview: last ? this.previewContent(last.content) : "",
          unreadCount,
          messages,
        };
      });
    },

    resolveChatMode(chatRows) {
      if (!this.currentUserId) {
        return "doctor";
      }
      let asDoctor = 0;
      let asPatient = 0;
      (chatRows || []).forEach((row) => {
        if (String(row.doctorId || "") === String(this.currentUserId)) {
          asDoctor += 1;
        }
        if (String(row.patientId || "") === String(this.currentUserId)) {
          asPatient += 1;
        }
      });
      return asPatient > asDoctor ? "patient" : "doctor";
    },

    setActiveConversation(conversationKey, skipRefresh) {
      const target = this.conversationList.find((item) => item.conversationKey === conversationKey);
      if (!target) {
        return;
      }
      this.activeConversation = target;
      this.rawChatList = target.messages || [];
      this.applyHistoryFilter();
      this.markActiveConversationAsRead();
      this.$nextTick(() => this.scrollToBottom());
      if (!skipRefresh) {
        this.refreshConversations(false);
      }
    },

    markActiveConversationAsRead() {
      if (!this.activeConversation) {
        return;
      }
      const lastIncomingId = this.getLastIncomingId(this.rawChatList);
      if (lastIncomingId > 0) {
        this.incomingSeenMap[this.activeConversation.conversationKey] = lastIncomingId;
      }
      this.conversationList = this.conversationList.map((item) => {
        if (item.conversationKey === this.activeConversation.conversationKey) {
          return { ...item, unreadCount: 0 };
        }
        return item;
      });
    },

    applyHistoryFilter() {
      const keyword = (this.historyKeyword || "").trim().toLowerCase();
      const start = this.historyDateRange && this.historyDateRange.length ? this.historyDateRange[0] : null;
      const end = this.historyDateRange && this.historyDateRange.length ? this.historyDateRange[1] : null;

      this.chatList = (this.rawChatList || []).filter((row) => {
        const text = String(row.content || "").toLowerCase();
        if (keyword && !text.includes(keyword)) {
          return false;
        }

        if (start || end) {
          const ts = this.getTimestamp(row.time);
          if (!ts) {
            return false;
          }
          if (start) {
            const s = this.getTimestamp(`${start} 00:00:00`);
            if (ts < s) {
              return false;
            }
          }
          if (end) {
            const e = this.getTimestamp(`${end} 23:59:59`);
            if (ts > e) {
              return false;
            }
          }
        }

        return true;
      });

      this.$nextTick(() => this.scrollToBottom());
    },

    resetHistoryFilter() {
      this.historyKeyword = "";
      this.historyDateRange = [];
      this.applyHistoryFilter();
    },

    async sendText() {
      const text = (this.contentText || "").trim();
      if (!this.activeConversation || !text) {
        return;
      }

      await addChat({
        patientId: this.activeConversation.patientId,
        patientName: this.activeConversation.patientName,
        doctorId: this.activeConversation.doctorId || 1,
        doctorName: this.activeConversation.doctorName || "陈亮",
        content: text,
        direction: this.outgoingDirection,
      });

      this.contentText = "";
      await this.refreshConversations(false);
      this.$nextTick(() => this.scrollToBottom());
    },

    beforeAttachmentUpload(file) {
      if (!this.activeConversation) {
        this.$modal.msgError("请先选择聊天对象");
        return false;
      }
      const maxSizeMb = 50;
      const isValid = file.size / 1024 / 1024 <= maxSizeMb;
      if (!isValid) {
        this.$modal.msgError(`上传文件大小不能超过 ${maxSizeMb} MB`);
      }
      return isValid;
    },

    async uploadAttachment(option) {
      const file = option && option.file;
      if (!file) {
        this.handleAttachmentError();
        return;
      }

      const formData = new FormData();
      formData.append("file", file);

      try {
        const res = await request({
          url: "/common/upload",
          method: "post",
          data: formData,
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: "Bearer " + getToken(),
          },
        });
        await this.handleAttachmentSuccess(res, file);
        if (option.onSuccess) {
          option.onSuccess(res, file);
        }
      } catch (e) {
        this.handleAttachmentError();
        if (option.onError) {
          option.onError(e);
        }
      }
    },

    async handleAttachmentSuccess(res, file) {
      if (!this.activeConversation) {
        this.$modal.msgError("请先选择聊天对象");
        return;
      }
      if (!res || res.code !== 200 || !res.fileName) {
        this.$modal.msgError((res && res.msg) || "文件上传失败");
        return;
      }

      const url = this.toAbsoluteFileUrl(res.fileName);
      const mime = file.type || "application/octet-stream";
      const payload = `[FILE]${file.name}|${url}|${mime}`;

      await addChat({
        patientId: this.activeConversation.patientId,
        patientName: this.activeConversation.patientName,
        doctorId: this.activeConversation.doctorId || 1,
        doctorName: this.activeConversation.doctorName || "陈亮",
        content: payload,
        direction: this.outgoingDirection,
      });

      await this.refreshConversations(false);
      this.$nextTick(() => this.scrollToBottom());
    },

    handleAttachmentError() {
      this.$modal.msgError("文件上传失败，请稍后重试");
    },

    isAttachmentMessage(content) {
      if (typeof content !== "string") {
        return false;
      }
      const text = content.trim();
      if (!text) {
        return false;
      }
      if (/^\[file\]/i.test(text)) {
        return true;
      }
      if (/^https?:\/\//i.test(text) || text.startsWith("/profile/upload/") || text.startsWith("/dev-api/profile/upload/")) {
        return true;
      }
      return false;
    },

    parseAttachment(content) {
      if (!this.isAttachmentMessage(content)) {
        return { kind: "text", name: "", url: "", mime: "" };
      }

      const text = String(content || "").trim();
      let name = "附件";
      let url = "";
      let mime = "application/octet-stream";

      if (/^\[file\]/i.test(text)) {
        const raw = text.replace(/^\[file\]/i, "");
        const parts = raw.split("|");
        const p0 = (parts[0] || "").trim();
        const p1 = (parts[1] || "").trim();
        const p2 = (parts[2] || "").trim();

        const p0IsUrl = /^https?:\/\//i.test(p0) || p0.startsWith("/profile/upload/") || p0.startsWith("/dev-api/profile/upload/");
        const p1IsUrl = /^https?:\/\//i.test(p1) || p1.startsWith("/profile/upload/") || p1.startsWith("/dev-api/profile/upload/");

        if (p0IsUrl && !p1IsUrl) {
          // 兼容历史格式: [file]url|文件名
          url = p0;
          name = p1 || "附件";
          mime = p2 || "application/octet-stream";
        } else {
          // 新格式: [FILE]文件名|url|mime
          name = p0 || "附件";
          url = p1;
          mime = p2 || "application/octet-stream";
        }
      } else {
        // 兼容历史消息：content 仅保存了文件 URL/相对路径。
        url = this.toAbsoluteFileUrl(text);
        const clean = String(text).split("?")[0];
        const seg = clean.split("/").pop() || "文件";
        name = decodeURIComponent(seg);
      }

      if (url) {
        url = this.toAbsoluteFileUrl(url);
      }

      if (!mime || mime === "application/octet-stream") {
        const ext = (name.split(".").pop() || "").toLowerCase();
        if (["png", "jpg", "jpeg", "gif", "bmp", "webp"].includes(ext)) {
          mime = `image/${ext === "jpg" ? "jpeg" : ext}`;
        } else if (["mp4", "webm", "ogg", "mov", "avi", "mkv"].includes(ext)) {
          mime = "video/mp4";
        }
      }

      let kind = "file";
      if (mime.startsWith("image/")) {
        kind = "image";
      } else if (mime.startsWith("video/")) {
        kind = "video";
      }
      return { name, url, mime, kind };
    },

    previewContent(content) {
      if (this.isAttachmentMessage(content)) {
        const file = this.parseAttachment(content);
        return `[附件] ${file.name}`;
      }
      return String(content || "");
    },

    resolveFileAccessUrl(path) {
      const raw = String(path || "").trim();
      if (!raw) {
        return "";
      }

      if (/^https?:\/\//i.test(raw)) {
        return raw;
      }

      const protocol = window.location.protocol;
      const host = window.location.hostname || "127.0.0.1";
      const backendOrigin = `${protocol}//${host}:8080`;

      if (raw.startsWith("/dev-api/")) {
        return `${backendOrigin}${raw.replace(/^\/dev-api/, "")}`;
      }

      if (raw.startsWith("/profile/")) {
        return `${backendOrigin}${raw}`;
      }

      const normalized = this.toAbsoluteFileUrl(raw);
      if (/^https?:\/\//i.test(normalized)) {
        return normalized;
      }
      if (normalized.startsWith("/dev-api/")) {
        return `${backendOrigin}${normalized.replace(/^\/dev-api/, "")}`;
      }
      if (normalized.startsWith("/profile/")) {
        return `${backendOrigin}${normalized}`;
      }
      return normalized;
    },

    openAttachment(attachment) {
      const rawUrl = attachment && attachment.url ? attachment.url : "";
      const finalUrl = this.resolveFileAccessUrl(rawUrl);
      if (!finalUrl) {
        this.$modal.msgError("附件链接无效");
        return;
      }
      const win = window.open(finalUrl, "_blank");
      if (!win) {
        window.location.href = finalUrl;
      }
    },

    toAbsoluteFileUrl(path) {
      if (!path) {
        return "";
      }
      if (/^https?:\/\//i.test(path)) {
        return path;
      }
      if (path.startsWith("/dev-api/")) {
        return path;
      }
      const base = process.env.VUE_APP_BASE_API || "";
      if (base && path.startsWith(base + "/")) {
        return path;
      }
      return `${base}${path}`;
    },

    formatTime(value) {
      if (!value) {
        return "";
      }
      const d = new Date(value);
      if (Number.isNaN(d.getTime())) {
        return String(value);
      }
      const mm = String(d.getMonth() + 1).padStart(2, "0");
      const dd = String(d.getDate()).padStart(2, "0");
      const hh = String(d.getHours()).padStart(2, "0");
      const mi = String(d.getMinutes()).padStart(2, "0");
      return `${mm}-${dd} ${hh}:${mi}`;
    },

    getTimestamp(value) {
      if (!value) {
        return 0;
      }
      const d = new Date(value);
      const t = d.getTime();
      return Number.isNaN(t) ? 0 : t;
    },

    getLastIncomingId(messages) {
      if (!messages || !messages.length) {
        return 0;
      }
      let maxId = 0;
      messages.forEach((m) => {
        if (this.isIncomingMessage(m) && Number(m.id) > maxId) {
          maxId = Number(m.id);
        }
      });
      return maxId;
    },

    countIncomingAfter(messages, seenId) {
      if (!messages || !messages.length) {
        return 0;
      }
      return messages.filter((m) => this.isIncomingMessage(m) && Number(m.id) > Number(seenId || 0)).length;
    },

    isSelfMessage(msg) {
      if (!msg) {
        return false;
      }

      const direction = Number(msg.direction);
      if (this.chatMode === "doctor") {
        // 医生端：direction=1 视为医生发送，显示在右侧。
        return direction === 1;
      }

      // 患者端：兼容历史数据，direction=2 或 0 视为患者发送，显示在右侧。
      if (direction === 2 || direction === 0) {
        return true;
      }
      if (direction === 1) {
        return false;
      }

      return Number(msg.direction) === this.outgoingDirection;
    },

    isIncomingMessage(msg) {
      return !!msg && !this.isSelfMessage(msg);
    },

    scrollToBottom() {
      const box = this.$refs.msgBox;
      if (box) {
        box.scrollTop = box.scrollHeight;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.chat-page {
  display: flex;
  height: calc(100vh - 84px);
  min-height: 620px;
}

.chat-sidebar {
  width: 280px;
  background: #f5f8fa;
  border-right: 1px solid #e4e7ed;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;

  .sidebar-title {
    font-weight: 700;
    color: #2c3e50;
  }

  .conversation-list {
    overflow-y: auto;
    flex: 1;
  }

  .conversation-item {
    border: 1px solid #e4e7ed;
    background: #fff;
    border-radius: 8px;
    padding: 8px;
    margin-bottom: 8px;
    cursor: pointer;

    &.active {
      border-color: #409eff;
      background: #ecf5ff;
    }

    &.has-unread {
      border-color: #f56c6c;
      background: #fff5f5;

      .name {
        color: #f56c6c;
      }
    }

    .conversation-top {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .name {
        font-weight: 600;
        color: #303133;
      }

      .time {
        font-size: 12px;
        color: #909399;
      }
    }

    .conversation-bottom {
      margin-top: 6px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 6px;

      .preview {
        color: #606266;
        font-size: 12px;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }

      .unread-badge {
        flex-shrink: 0;
      }
    }
  }
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fafafa;

  .chat-header {
    height: 48px;
    padding: 0 16px;
    display: flex;
    align-items: center;
    background: #80cd8d;
    color: #fff;
    font-size: 16px;
    font-weight: 700;
  }

  .history-toolbar {
    display: flex;
    gap: 8px;
    padding: 10px 12px;
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
  }

  .msg-box {
    flex: 1;
    overflow-y: auto;
    padding: 14px;

    .msg-row {
      display: flex;
      margin-bottom: 12px;

      &.self {
        justify-content: flex-end;

        .bubble {
          background: #80cd8d;
          color: #fff;
        }
      }

      .bubble {
        max-width: 70%;
        padding: 8px 10px;
        border-radius: 8px;
        background: #fff;
        word-break: break-word;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);

        .msg-time {
          margin-top: 6px;
          font-size: 11px;
          opacity: 0.8;
        }

        .msg-image {
          max-width: 260px;
          max-height: 220px;
          border-radius: 6px;
          display: block;
        }

        .msg-video {
          width: 280px;
          max-width: 100%;
          border-radius: 6px;
          display: block;
        }
      }
    }
  }

  .input-box {
    padding: 10px 12px;
    border-top: 1px solid #e4e7ed;
    background: #fff;
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 8px;
    align-items: center;

    .upload-btn {
      display: inline-block;
    }
  }
}

@media (max-width: 960px) {
  .chat-page {
    height: auto;
    min-height: auto;
    flex-direction: column;
  }

  .chat-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
    max-height: 300px;
  }

  .chat-main .history-toolbar {
    flex-wrap: wrap;
  }
}
</style>
