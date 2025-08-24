// Jinja2에서 주입한 rawData를 역순 정렬
const rawData = (window.rawData || []).slice().reverse();

const labels = rawData.map((r) => r.timestamp);
const counts = rawData.map((r) => r.count);

const cfg = {
  type: 'line',
  data: {
    labels,
    datasets: [
      {
        label: '인원 수',
        data: counts,
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76,175,80,.2)',
        tension: 0.2,
        fill: true,
        pointRadius: 3,
      },
    ],
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: true, position: 'top' },
      title: { display: true, text: '시간대별 동방 인원 수 변화' },
    },
    scales: {
      x: { title: { display: true, text: '측정 시각' } },
      y: {
        title: { display: true, text: '인원 수' },
        beginAtZero: true,
        suggestedMax: 10,
      },
    },
  },
};

new Chart(document.getElementById('peopleChart'), cfg);
