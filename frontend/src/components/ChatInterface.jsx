import { useState } from 'react';

const ChatInterface = () => {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setIsLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/query?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            setResponse(data.response);
        } catch (error) {
            console.error('Error:', error);
            setResponse('Error fetching response');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-4">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Ask something..."
                        className="w-full p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={isLoading}
                    />
                </div>
                <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                    {isLoading ? (
                        <div className="flex items-center justify-center">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                            <span className="ml-2">Loading...</span>
                        </div>
                    ) : (
                        'Send'
                    )}
                </button>
            </form>

            {response && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h2 className="font-semibold mb-2">Response:</h2>
                    <p className="whitespace-pre-wrap">{response}</p>
                </div>
            )}
        </div>
    );
};

export default ChatInterface;