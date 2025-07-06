/* global Chart */
document.addEventListener('DOMContentLoaded', function () {
    const STATUS_LABELS = JSON.parse(document.getElementById('status-labels').textContent);
    const STATUS_COUNTS = JSON.parse(document.getElementById('status-counts').textContent);
    const STATUS_AMOUNTS = JSON.parse(document.getElementById('status-amounts').textContent);

    if (STATUS_LABELS && STATUS_COUNTS && STATUS_AMOUNTS) {
        const ctx = document.getElementById('statusChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: STATUS_LABELS,
                datasets: [
                    {
                        label: 'Số lượng đề xuất',
                        data: STATUS_COUNTS,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Tổng tiền (VNĐ)',
                        data: STATUS_AMOUNTS,
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Số lượng đề xuất' }
                    },
                    y1: {
                        beginAtZero: true,
                        position: 'right',
                        title: { display: true, text: 'Tổng tiền (VNĐ)' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }
});