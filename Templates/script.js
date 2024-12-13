// Fungsi untuk mengambil berita dari Detik.com News API
async function fetchNews() {
    const apiKey = '32b84c9994db41dca9495990753d9258'; // Ganti dengan API Key Anda
    const url = `https://newsapi.org/v2/everything?q=tesla&from=2024-09-30&sortBy=publishedAt&apiKey=32b84c9994db41dca9495990753d9258`;

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        displayNews(data);
    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
    }
}

// Fungsi untuk menampilkan berita di halaman
function displayNews(newsData) {
    const newsContainer = document.getElementById('news-container');
    newsContainer.innerHTML = ''; // Kosongkan kontainer sebelum menambahkan berita baru

    newsData.articles.forEach(article => {
        const newsItem = document.createElement('div');
        newsItem.classList.add('news-item');
        newsItem.innerHTML = `
            <h3>${article.title}</h3>
            <p>${article.description}</p>
            <a href="${article.url}" target="_blank">Baca Selengkapnya</a>
        `;
        newsContainer.appendChild(newsItem);
    });
}

// Panggil fungsi fetchNews saat halaman dimuat
window.onload = fetchNews;