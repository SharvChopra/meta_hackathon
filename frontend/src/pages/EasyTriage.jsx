import React, { useState, useEffect } from 'react';
import { fetchCurrentTicket, updateTicket } from '../api';

function EasyTriage() {
    const [ticket, setTicket] = useState(null);

    useEffect(() => {
        async function loadTicket() {
            const data = await fetchCurrentTicket();
            setTicket(data);
        }
        loadTicket();
    }, []);

    if (!ticket) {
        return <div>Loading...</div>;
    }

    const handleLabel = (labelName) => {
        updateTicket(ticket.id, { status: labelName });
    };

    return (
        <div>
            <h1>{ticket.title}</h1>
            <p>{ticket.description}</p>
            <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button id="btn-bug" onClick={() => handleLabel('bug')}>Bug</button>
                <button id="btn-docs" onClick={() => handleLabel('docs')}>Docs</button>
                <button id="btn-enhancement" onClick={() => handleLabel('enhancement')}>Enhancement</button>
            </div>
        </div>
    );
}

export default EasyTriage;
