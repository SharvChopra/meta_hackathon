import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import EasyTriage from './pages/EasyTriage';
import MediumDup from './pages/MediumDup';
import HardReview from './pages/HardReview';

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<div style={{ padding: '20px', fontFamily: 'sans-serif' }}><h1>RL UI Ready</h1><p>Agent will navigate to specific endpoints to begin task.</p></div>} />
                <Route path="/issues/easy" element={<EasyTriage />} />
                <Route path="/issues/medium" element={<MediumDup />} />
                <Route path="/pulls/hard" element={<HardReview />} />
                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
