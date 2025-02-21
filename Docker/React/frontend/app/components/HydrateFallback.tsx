import React from 'react';
import '../HydrateFallback.css';

export default function HydrateFallback(): React.ReactElement {
    return (
        <div className="loading-overlay">
            <div className="loading-container">
                <div className="spinner"></div>
                <div className="loading-text">Chargement en cours...</div>
            </div>
        </div>
    );
};
