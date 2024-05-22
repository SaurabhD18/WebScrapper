import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [backgroundColor, setBackgroundColor] = useState('#9B2335');

    useEffect(() => {
      const colors = [
        '#FF6F61', '#6B5B95', '#88B04B', '#F7CAC9', '#92A8D1', '#955251', '#B565A7', '#009B77',
        '#DD4124', '#D65076', '#45B8AC', '#EFC050', '#5B5EA6', '#9B2335', '#DFCFBE', '#55B4B0',
        '#E15D44', '#7FCDCD', '#BC243C', '#C3447A', '#98B4D4'
    ];
        let index = 0;
        
        const changeBackgroundColor = () => {
            setBackgroundColor(colors[index]);
            index = (index + 1) % colors.length;
        };

        const intervalId = setInterval(changeBackgroundColor, 5000); // Change color every 5 seconds

        return () => clearInterval(intervalId); // Cleanup interval on component unmount
    }, []);

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await axios.post('http://127.0.0.1:5000/scrape', { url }, { responseType: 'blob' });
            const blob = new Blob([response.data], { type: 'application/zip' });
            const downloadUrl = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = 'audio_files.zip';
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (err) {
            setError('Failed to scrape the website. Please check the URL and try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App" style={{ backgroundColor }}>
            <header className="App-header">
                <h1>HG RSP WEB Audios Scraper</h1>
                <form onSubmit={handleSubmit}>
                    <label htmlFor="url">URL: </label>
                    <input
                        type="text"
                        id="url"
                        name="url"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        required
                    />
                    <br /><br />
                    <button type="submit" disabled={loading}>
                        {loading ? 'Scraping...' : 'Scrape'}
                    </button>
                </form>
                {error && <p className="error">{error}</p>}
            </header>
        </div>
    );
}

export default App;
