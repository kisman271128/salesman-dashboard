// netlify/functions/gemini.js
exports.handler = async (event) => {
    if (event.httpMethod !== 'POST') return { statusCode: 405, body: 'Method Not Allowed' };

    const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
    if (!GEMINI_API_KEY) return {
        statusCode: 500,
        body: JSON.stringify({ error: 'GEMINI_API_KEY belum diset di environment variables' })
    };

    try {
        const payload = JSON.parse(event.body);
        const model   = payload.model || 'gemini-2.0-flash';
        delete payload.model;

        const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${GEMINI_API_KEY}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'User-Agent': 'SalesmanApp/1.0' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        return {
            statusCode: response.status,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify(data)
        };
    } catch (err) {
        return { statusCode: 500, body: JSON.stringify({ error: err.message }) };
    }
};
