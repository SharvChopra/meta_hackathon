import React, { useState, useEffect } from 'react';
import { fetchCurrentTicket, updateTicket } from '../api';

function MediumDup() {
    const [ticket, setTicket] = useState(null);
    const [inputValue, setInputValue] = useState('');

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

    const handleClose = () => {
        updateTicket(ticket.id, {
            status: 'closed',
            linked_issue: parseInt(inputValue, 10)
        });
    };

    return (
        <div>
            <h1>{ticket.title}</h1>
            <p>{ticket.description}</p>

            <div style={{ marginTop: '20px' }}>
                <label htmlFor="input-duplicate-id">Duplicate Issue Number: </label>
                <input
                    type="number"
                    id="input-duplicate-id"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="e.g. 12"
                />
            </div>

            <div style={{ marginTop: '20px' }}>
                <button id="btn-close-duplicate" onClick={handleClose}>
                    Close as Duplicate
                </button>
            </div>
        </div>
    );
}

export default MediumDup;
