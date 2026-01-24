const apiBaseInput = document.getElementById("apiBase");
const saveApiButton = document.getElementById("saveApi");
const chartStatus = document.getElementById("chartStatus");
const chartSummary = document.getElementById("chartSummary");
const createChartButton = document.getElementById("createChart");
const confirmLockButton = document.getElementById("confirmLock");
const chatLog = document.getElementById("chatLog");
const sendMessageButton = document.getElementById("sendMessage");
const messageInput = document.getElementById("messageInput");
const conversationSummary = document.getElementById("conversationSummary");

const registerEmail = document.getElementById("registerEmail");
const registerPassword = document.getElementById("registerPassword");
const registerName = document.getElementById("registerName");
const registerButton = document.getElementById("registerButton");
const loginEmail = document.getElementById("loginEmail");
const loginPassword = document.getElementById("loginPassword");
const loginButton = document.getElementById("loginButton");
const logoutButton = document.getElementById("logoutButton");
const authStatus = document.getElementById("authStatus");

const prefTone = document.getElementById("prefTone");
const prefLength = document.getElementById("prefLength");
const savePrefs = document.getElementById("savePrefs");
const prefStatus = document.getElementById("prefStatus");
const profileInfo = document.getElementById("profileInfo");
const guideSteps = document.querySelectorAll(".guide-step");
const suggestionButtons = document.querySelectorAll(".suggestion");

const userIdInput = document.getElementById("userId");
const birthDateInput = document.getElementById("birthDate");
const birthTimeInput = document.getElementById("birthTime");
const birthLocationInput = document.getElementById("birthLocation");
const genderSelect = document.getElementById("gender");

const toneSelect = document.getElementById("toneSelect");

const getApiBase = () => {
  return localStorage.getItem("aetheria_api_base") || apiBaseInput.value;
};

const setApiBase = (value) => {
  localStorage.setItem("aetheria_api_base", value);
  apiBaseInput.value = value;
};

const getToken = () => localStorage.getItem("aetheria_token");
const setToken = (token) => {
  if (token) {
    localStorage.setItem("aetheria_token", token);
  } else {
    localStorage.removeItem("aetheria_token");
  }
};

const setUserId = (value) => {
  userIdInput.value = value || "";
};

const addMessage = (text, type = "ai") => {
  const div = document.createElement("div");
  div.className = `msg ${type}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
};

const setGuideStep = (step) => {
  guideSteps.forEach((item) => {
    item.classList.toggle("active", item.dataset.step === String(step));
  });
};

const renderSummary = (data) => {
  if (!data) {
    chartSummary.classList.add("empty");
    chartSummary.textContent = "這裡會顯示命盤重點與鎖盤狀態";
    return;
  }
  chartSummary.classList.remove("empty");
  chartSummary.innerHTML = `
    <div class="summary-block">
      <strong>狀態：</strong>${data.statusText}
    </div>
    <div class="summary-block">
      <strong>命宮：</strong>${data.mainPalace || "-"}
    </div>
    <div class="summary-block">
      <strong>主星：</strong>${data.mainStars || "-"}
    </div>
    <div class="summary-block">
      <strong>關鍵宮位：</strong>${data.keyPalaces || "-"}
    </div>
  `;
};

const extractSummary = (structure, lockInfo) => {
  if (!structure) {
    return null;
  }
  const main = structure["命宮"] || {};
  const mainStars = (main["主星"] || []).join("、");
  const keyPalaces = ["官祿宮", "財帛宮", "夫妻宮"]
    .map((name) => {
      const palace = (structure["十二宮"] || {})[name];
      if (!palace) return null;
      const stars = (palace["主星"] || []).join("、");
      return `${name}:${stars || "-"}`;
    })
    .filter(Boolean)
    .join(" / ");
  return {
    statusText: lockInfo,
    mainPalace: main["宮位"] || "-",
    mainStars,
    keyPalaces,
  };
};

const scrollToSection = (id) => {
  const target = document.getElementById(id);
  if (target) target.scrollIntoView({ behavior: "smooth" });
};

const bindScrollButtons = () => {
  document.querySelectorAll("[data-scroll]").forEach((btn) => {
    btn.addEventListener("click", () => scrollToSection(btn.dataset.scroll));
  });
};

saveApiButton.addEventListener("click", () => {
  setApiBase(apiBaseInput.value.trim());
});

const init = () => {
  const saved = localStorage.getItem("aetheria_api_base");
  if (saved) apiBaseInput.value = saved;
  renderSummary(null);
  addMessage("你好，我是 Aetheria。請先建立並確認命盤，我會用溫暖專業的方式回應你。", "ai");
  if (conversationSummary) {
    conversationSummary.textContent = "對話摘要會顯示在這裡";
  }
  setGuideStep(1);
  updateAuthStatus();
  bindScrollButtons();
};

const postJson = async (path, payload, method = "POST") => {
  const token = getToken();
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${getApiBase()}${path}`,
    {
      method,
      headers,
      body: JSON.stringify(payload),
    }
  );
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || data.error || "API 失敗");
  }
  return data;
};

const getJson = async (path) => {
  const token = getToken();
  const headers = {};
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${getApiBase()}${path}`, { headers });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || data.error || "API 失敗");
  }
  return data;
};

const updateAuthStatus = async () => {
  const token = getToken();
  if (!token) {
    authStatus.textContent = "尚未登入";
    profileInfo.textContent = "請先登入";
    profileInfo.classList.add("empty");
    setGuideStep(1);
    return;
  }
  try {
    const data = await getJson("/api/profile");
    authStatus.textContent = `已登入：${data.profile.display_name || data.profile.email}`;
    profileInfo.classList.remove("empty");
    profileInfo.innerHTML = `
      <div><strong>User ID：</strong>${data.profile.user_id}</div>
      <div><strong>Email：</strong>${data.profile.email}</div>
      <div><strong>顯示名稱：</strong>${data.profile.display_name || "-"}</div>
    `;
    setUserId(data.profile.user_id);
    if (data.preferences) {
      if (data.preferences.tone) prefTone.value = data.preferences.tone;
      if (data.preferences.response_length) prefLength.value = data.preferences.response_length;
    }
    if (prefTone.value) toneSelect.value = prefTone.value;
    setGuideStep(2);
  } catch (error) {
    authStatus.textContent = "登入狀態失效，請重新登入";
    setToken(null);
    setGuideStep(1);
  }
};

createChartButton.addEventListener("click", async () => {
  const payload = {
    user_id: userIdInput.value.trim(),
    birth_date: birthDateInput.value.trim(),
    birth_time: birthTimeInput.value.trim(),
    birth_location: birthLocationInput.value.trim(),
    gender: genderSelect.value,
  };

  if (!payload.user_id || !payload.birth_date || !payload.birth_time || !payload.birth_location) {
    chartStatus.textContent = "請先完整填寫使用者資料";
    return;
  }

  chartStatus.textContent = "命盤分析中...";
  try {
    const data = await postJson("/api/chart/initial-analysis", payload);
    chartStatus.textContent = "命盤已生成，等待確認鎖盤";
    const summary = extractSummary(data.structure, "待確認");
    renderSummary(summary);
    addMessage("我已完成命盤分析，若內容符合，請按下『確認鎖盤』。", "ai");
    setGuideStep(2);
  } catch (error) {
    chartStatus.textContent = `命盤生成失敗：${error.message}`;
  }
});

registerButton.addEventListener("click", async () => {
  try {
    const data = await postJson("/api/auth/register", {
      email: registerEmail.value.trim(),
      password: registerPassword.value.trim(),
      display_name: registerName.value.trim(),
      consents: { terms_accepted: true, data_usage_accepted: true },
    });
    setToken(data.token);
    authStatus.textContent = "註冊成功，已登入";
    await updateAuthStatus();
  } catch (error) {
    authStatus.textContent = `註冊失敗：${error.message}`;
  }
});

loginButton.addEventListener("click", async () => {
  try {
    const data = await postJson("/api/auth/login", {
      email: loginEmail.value.trim(),
      password: loginPassword.value.trim(),
    });
    setToken(data.token);
    await updateAuthStatus();
  } catch (error) {
    authStatus.textContent = `登入失敗：${error.message}`;
  }
});

logoutButton.addEventListener("click", async () => {
  try {
    await postJson("/api/auth/logout", {});
  } catch (error) {
    // ignore
  }
  setToken(null);
  authStatus.textContent = "已登出";
  profileInfo.textContent = "請先登入";
  profileInfo.classList.add("empty");
});

savePrefs.addEventListener("click", async () => {
  try {
    await postJson("/api/profile", {
      preferences: {
        tone: prefTone.value,
        response_length: prefLength.value,
      },
    }, "PATCH");
    prefStatus.textContent = "偏好已更新";
  } catch (error) {
    prefStatus.textContent = `偏好更新失敗：${error.message}`;
  }
});

suggestionButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const suggestion = btn.dataset.suggestion;
    if (suggestion) {
      messageInput.value = suggestion;
      messageInput.focus();
    }
  });
});

confirmLockButton.addEventListener("click", async () => {
  const user_id = userIdInput.value.trim();
  if (!user_id) {
    chartStatus.textContent = "請先填寫使用者 ID";
    return;
  }
  chartStatus.textContent = "鎖盤確認中...";
  try {
    const data = await postJson("/api/chart/confirm-lock", { user_id });
    chartStatus.textContent = `命盤已鎖定（${data.locked_at || "完成"}）`;
    const summary = extractSummary(
      { ...JSON.parse(JSON.stringify({ "命宮": {}, "十二宮": {} })) },
      "已確認鎖盤"
    );
    renderSummary(summary);
    addMessage("命盤已鎖定完成。我會以此為基礎回答你接下來的問題。", "ai");
    setGuideStep(3);
  } catch (error) {
    chartStatus.textContent = `鎖盤失敗：${error.message}`;
  }
});

sendMessageButton.addEventListener("click", async () => {
  const user_id = userIdInput.value.trim();
  const message = messageInput.value.trim();

  if (!user_id) {
    addMessage("請先填寫使用者 ID 並完成鎖盤。", "ai");
    return;
  }
  if (!message) return;

  addMessage(message, "user");
  messageInput.value = "";

  const payload = {
    user_id,
    message,
    tone: toneSelect.value,
  };

  try {
    const data = await postJson("/api/chat/message", payload);
    const reply = data.reply || data.answer || data.message || "已收到";
    addMessage(reply, "ai");
    if (conversationSummary && data.conversation_summary) {
      conversationSummary.textContent = data.conversation_summary;
    }
  } catch (error) {
    addMessage(`抱歉，剛剛連線失敗：${error.message}`);
  }
});

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendMessageButton.click();
  }
});

init();
