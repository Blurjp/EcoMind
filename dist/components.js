function createElement(tag, className, textContent) {
  const element = document.createElement(tag);
  if (className)
    element.className = className;
  if (textContent)
    element.textContent = textContent;
  return element;
}
function createSection(title) {
  const section = createElement("div", "section");
  const header = createElement("h3", "section-title", title);
  section.appendChild(header);
  return section;
}
function createDataRow(label, value) {
  const row = createElement("div", "data-row");
  const labelEl = createElement("span", "data-label", label);
  const valueEl = createElement("span", "data-value", value);
  row.appendChild(labelEl);
  row.appendChild(valueEl);
  return row;
}
function createList(items) {
  const list = createElement("div", "data-list");
  items.forEach((item) => {
    list.appendChild(createDataRow(item.label, item.value));
  });
  return list;
}
function showLoading(container) {
  container.innerHTML = '<div class="loading">Loading...</div>';
}
function showError(container, message) {
  container.innerHTML = `<div class="error">Error: ${message}</div>`;
}
function sendMessage(type, data) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ type, ...data }, (response) => {
      if (chrome.runtime.lastError) {
        resolve({
          success: false,
          error: chrome.runtime.lastError.message
        });
      } else {
        resolve(response || { success: false, error: "No response" });
      }
    });
  });
}
function formatMetric(value, unit, decimals = 3) {
  return `${value.toFixed(decimals)} ${unit}`;
}
function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString();
}
export {
  sendMessage as a,
  showError as b,
  createElement as c,
  createSection as d,
  formatMetric as e,
  formatDate as f,
  createDataRow as g,
  createList as h,
  showLoading as s
};
