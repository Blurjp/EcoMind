export function createElement<T extends HTMLElement>(
  tag: string,
  className?: string,
  textContent?: string
): T {
  const element = document.createElement(tag) as T;
  if (className) element.className = className;
  if (textContent) element.textContent = textContent;
  return element;
}

export function createButton(
  text: string,
  className: string,
  onClick: () => void
): HTMLButtonElement {
  const button = createElement<HTMLButtonElement>('button', className, text);
  button.addEventListener('click', onClick);
  return button;
}

export function createSection(title: string): HTMLElement {
  const section = createElement('div', 'section');
  const header = createElement('h3', 'section-title', title);
  section.appendChild(header);
  return section;
}

export function createDataRow(label: string, value: string): HTMLElement {
  const row = createElement('div', 'data-row');
  const labelEl = createElement('span', 'data-label', label);
  const valueEl = createElement('span', 'data-value', value);
  row.appendChild(labelEl);
  row.appendChild(valueEl);
  return row;
}

export function createList(
  items: Array<{ label: string; value: string; title?: string }>
): HTMLElement {
  const list = createElement('div', 'data-list');
  items.forEach((item) => {
    const row = createDataRow(item.label, item.value);
    if (item.title) {
      row.setAttribute('title', item.title);
      row.style.cursor = 'help';
    }
    list.appendChild(row);
  });
  return list;
}

export function showLoading(container: HTMLElement): void {
  container.innerHTML = '<div class="loading">Loading...</div>';
}

export function showError(container: HTMLElement, message: string): void {
  const errorDiv = createElement('div', 'error');
  // Use textContent instead of innerHTML to prevent XSS
  errorDiv.textContent = `Error: ${message}`;
  container.innerHTML = '';
  container.appendChild(errorDiv);
}

export function sendMessage<T = any>(
  type: string,
  data?: any
): Promise<{ success: boolean; data?: T; error?: string }> {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ type, ...data }, (response) => {
      if (chrome.runtime.lastError) {
        resolve({
          success: false,
          error: chrome.runtime.lastError.message,
        });
      } else {
        resolve(response || { success: false, error: 'No response' });
      }
    });
  });
}

export function formatMetric(value: number, unit: string, decimals = 3): string {
  return `${value.toFixed(decimals)} ${unit}`;
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString();
}