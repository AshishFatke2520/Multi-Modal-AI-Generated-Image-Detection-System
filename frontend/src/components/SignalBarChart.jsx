import React from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

const SignalBarChart = ({ signals }) => {
    const labels = ['Metadata', 'Artifacts', 'Classifier', 'Noise Patterns', 'Consistency'];

    // Convert decimal to percentages
    const fakeScores = [
        signals.metadata * 100 || 0,
        signals.artifacts * 100 || 0,
        signals.classifier * 100 || 0,
        (signals.artifacts * 0.8 + signals.classifier * 0.2) * 100 || 0,
        (signals.metadata * 0.9 + 0.1) * 100 || 0
    ];

    const realScores = fakeScores.map(score => 100 - score);

    const data = {
        labels,
        datasets: [
            {
                label: 'Real Probability (%)',
                data: realScores,
                backgroundColor: 'rgba(0, 255, 136, 0.5)',
                borderColor: '#00ff88',
                borderWidth: 1,
            },
            {
                label: 'AI / Fake Probability (%)',
                data: fakeScores,
                backgroundColor: 'rgba(255, 42, 42, 0.5)',
                borderColor: '#ff2a2a',
                borderWidth: 1,
            }
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    color: '#e0e6ed',
                    font: {
                        size: 13
                    }
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                    }
                }
            }
        },
        scales: {
            x: {
                stacked: false, // group instead of stack to compare side-by-side
                ticks: {
                    color: '#94a3b8'
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)'
                }
            },
            y: {
                stacked: false,
                max: 100,
                ticks: {
                    color: '#94a3b8'
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)'
                }
            }
        }
    };

    return (
        <div style={{ background: '#111625', padding: '1.5rem', borderRadius: '16px', marginTop: '2rem', border: '1px solid #1a2138' }}>
            <h3 style={{ textAlign: 'center', color: '#00f2ff', marginBottom: '1.5rem' }}>Metrics Comparison Breakdown</h3>
            <div style={{ height: '300px', width: '100%' }}>
                <Bar data={data} options={options} />
            </div>
        </div>
    );
};

export default SignalBarChart;
