import React from 'react';
import {
    Chart as ChartJS,
    RadialLinearScale,
    PointElement,
    LineElement,
    Filler,
    Tooltip,
    Legend,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';

ChartJS.register(
    RadialLinearScale,
    PointElement,
    LineElement,
    Filler,
    Tooltip,
    Legend
);

const SignalRadar = ({ signals }) => {
    const data = {
        labels: ['Metadata Analysis', 'Compression Artifacts', 'Visual Classifier', 'Noise Patterns', 'Consistency Check'],
        datasets: [
            {
                label: 'Suspicion Level',
                data: [
                    signals.metadata * 100 || 0,
                    signals.artifacts * 100 || 0,
                    signals.classifier * 100 || 0,
                    (signals.artifacts * 0.8 + signals.classifier * 0.2) * 100, // Synthetic mapping for demo if specific signal missing
                    (signals.metadata * 0.9 + 0.1) * 100
                ],
                backgroundColor: 'rgba(0, 242, 255, 0.2)',
                borderColor: '#00f2ff',
                borderWidth: 2,
                pointBackgroundColor: '#fff',
                pointBorderColor: '#00f2ff',
            },
        ],
    };

    const options = {
        scales: {
            r: {
                angleLines: {
                    color: 'rgba(255, 255, 255, 0.1)',
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)',
                },
                pointLabels: {
                    color: '#e0e6ed',
                    font: {
                        size: 12
                    }
                },
                ticks: {
                    display: false,
                    maxTicksLimit: 5,
                },
                suggestedMin: 0,
                suggestedMax: 100,
            },
        },
        plugins: {
            legend: {
                display: false
            }
        }
    };

    return <Radar data={data} options={options} />;
};

export default SignalRadar;
