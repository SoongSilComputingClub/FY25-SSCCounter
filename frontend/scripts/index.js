// ---- state ------------------------------------------------------------
let socket = null;

// ---- utils ------------------------------------------------------------
const qs = (sel) => document.querySelector(sel);

const formatNow = () =>
  new Date().toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

const wsUrl = (path) => {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${location.host}${path}`;
};

// ---- UI updates -------------------------------------------------------
function updateClock() {
  const nowEl = qs('#now');
  if (nowEl) nowEl.textContent = `📅 현재 시각: ${formatNow()}`;
}

function setLoading(isLoading) {
  const loader = qs('#loader');
  if (!loader) return;
  loader.style.display = isLoading ? 'block' : 'none';

  const btn = qs('#btn-count');
  if (btn) btn.disabled = isLoading;
}

function showResultText(text) {
  const result = qs('#result');
  if (result) result.textContent = text;
}

function showTimestamp() {
  const ts = qs('#timestamp');
  if (ts) ts.textContent = `🕒 확인 시각: ${formatNow()}`;
}

// ---- actions ----------------------------------------------------------
function connectWebSocket() {
  socket = new WebSocket(wsUrl('/v2/ws/client'));

  socket.addEventListener('message', (event) => {
    setLoading(false);
    try {
      const data = JSON.parse(event.data);
      if (data.error) {
        showResultText(`❌ ${data.error}`);
        return;
      }
      showResultText(
        `동방에 현재 ${data.count}명 있습니다. (추론 시간: ${data.inference_time}초)`,
      );
      showTimestamp();
    } catch (err) {
      showResultText(`❌ 응답 파싱 실패: ${err}`);
    }
  });

  socket.addEventListener('error', (err) => {
    console.error('WebSocket error', err);
    setLoading(false);
    showResultText('❌ 서버와의 통신 중 오류가 발생했습니다.');
  });
}

function requestCount() {
  setLoading(true);
  showResultText('');
  const ts = qs('#timestamp');
  if (ts) ts.textContent = '';

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send('capture');
  } else {
    setLoading(false);
    showResultText('❌ 서버와의 연결이 불안정합니다.');
  }
}

function goToLogs() {
  location.href = '/logs';
}

// ---- bootstrap --------------------------------------------------------
window.addEventListener('load', () => {
  updateClock();
  setInterval(updateClock, 1000);

  connectWebSocket();

  qs('#btn-count')?.addEventListener('click', requestCount);
  qs('#btn-logs')?.addEventListener('click', goToLogs);
});
