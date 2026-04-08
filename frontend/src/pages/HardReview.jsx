import React, { useState, useEffect } from 'react';
import { fetchCurrentTicket, updateTicket } from '../api';

function HardReview() {
    const [ticket, setTicket] = useState(null);
    const [textareaValue, setTextareaValue] = useState('');

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

    const handleRequestChanges = () => {
        updateTicket(ticket.id, {
            status: 'changes_requested',
            comments: textareaValue
        });
    };

    const handleMerge = () => {
        updateTicket(ticket.id, {
            status: 'merged'
        });
    };

    return (
        <div>
            <h1>{ticket.title}</h1>
            <p>{ticket.description}</p>

            {ticket.code_snippet && (
                <div style={{ background: '#f4f4f4', padding: '15px', borderRadius: '5px', marginTop: '20px' }}>
                    <pre>
                        <code>
                            {ticket.code_snippet}
                        </code>
                    </pre>
                </div>
            )}

            <div style={{ marginTop: '20px' }}>
                <label htmlFor="input-review-comment" style={{ display: 'block', marginBottom: '10px' }}>Review Comments:</label>
                <textarea
                    id="input-review-comment"
                    value={textareaValue}
                    onChange={(e) => setTextareaValue(e.target.value)}
                    rows={5}
                    style={{ width: '100%', maxWidth: '500px' }}
                />
            </div>

            <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button
                    id="btn-request-changes"
                    onClick={handleRequestChanges}
                    style={{ background: 'red', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                >
                    Request Changes
                </button>
                <button
                    id="btn-merge-pr"
                    onClick={handleMerge}
                    style={{ background: 'green', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                >
                    Merge PR
                </button>
            </div>
        </div>
    );
}

export default HardReview;
