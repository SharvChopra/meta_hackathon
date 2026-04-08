export async function fetchCurrentTicket() {
    const response = await fetch('/api/current');
    if (!response.ok) {
        console.error('Failed to fetch ticket');
        return null;
    }
    return await response.json();
}

export async function updateTicket(id, payload) {
    const response = await fetch('/api/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: id,
            ...payload
        })
    });

    if (!response.ok) {
        console.error('Failed to update ticket');
    }

    return await response.json();
}
