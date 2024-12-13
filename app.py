from flask import Flask, render_template, request, flash
import requests
import os
import math

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Untuk flash messages

# Endpoint Google Books API
GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"

def get_books_data(keyword, search_type='all', page=1):
    """
    Fungsi untuk mengambil data buku dari Google Books API
    """
    try:
        start_index = (page - 1) * 20
        
        # Menyesuaikan query berdasarkan tipe pencarian
        if search_type == 'isbn':
            query = f'isbn:{keyword}'
        elif search_type == 'title':
            query = f'intitle:{keyword}'
        elif search_type == 'author':
            query = f'inauthor:{keyword}'
        else:
            query = keyword

        params = {
            'q': query,
            'maxResults': 20,
            'startIndex': start_index,
            'langRestrict': 'en'
        }

        response = requests.get(GOOGLE_BOOKS_API, params=params)
        response.raise_for_status()
        
        data = response.json()
        books = data.get('items', [])
        total_items = data.get('totalItems', 0)
        total_pages = math.ceil(total_items / 20)  # Menghitung total halaman
        
        # Ekstrak dan standardisasi data buku
        processed_books = []
        for book in books:
            volume_info = book.get('volumeInfo', {})
            
            # Dapatkan ISBN
            isbn = ''
            for identifier in volume_info.get('industryIdentifiers', []):
                if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                    isbn = identifier.get('identifier')
                    break

            processed_book = {
                'title': volume_info.get('title', 'Judul tidak tersedia'),
                'authors': volume_info.get('authors', ['Penulis tidak tersedia']),
                'description': volume_info.get('description', 'Deskripsi tidak tersedia'),
                'isbn': isbn,
                'publisher': volume_info.get('publisher', 'Penerbit tidak tersedia'),
                'published_date': volume_info.get('publishedDate', 'Tanggal tidak tersedia'),
                'page_count': volume_info.get('pageCount', 'Tidak tersedia'),
                'categories': volume_info.get('categories', ['Kategori tidak tersedia']),
                'image_links': volume_info.get('imageLinks', {}),
                'info_link': volume_info.get('infoLink', '#')
            }
            processed_books.append(processed_book)

        return processed_books, total_items, total_pages
        
    except requests.RequestException as e:
        print(f"Error fetching data from Google Books API: {e}")
        return [], 0, 0

def get_pagination_range(current_page, total_pages):
    """
    Fungsi untuk menghitung range halaman yang akan ditampilkan
    """
    if total_pages <= 5:
        return range(1, total_pages + 1)
    
    if current_page <= 3:
        return range(1, 6)
    
    if current_page >= total_pages - 2:
        return range(total_pages - 4, total_pages + 1)
    
    return range(current_page - 2, current_page + 3)

@app.route('/', methods=['GET', 'POST'])
def search():
    books = []
    total_items = 0
    total_pages = 0
    page = 1
    keyword = ''
    search_type = 'all'

    if request.method == 'POST':
        keyword = request.form.get('keyword', '').strip()
        search_type = request.form.get('search_type', 'all')

        if not keyword:
            flash('Mohon masukkan kata kunci pencarian', 'error')
        else:
            books, total_items, total_pages = get_books_data(keyword, search_type, page)
            if not books:
                flash('Tidak ada buku yang ditemukan', 'info')

    pagination_range = get_pagination_range(page, total_pages)
    return render_template('index.html', 
                         books=books,
                         page=page,
                         keyword=keyword,
                         search_type=search_type,
                         total_items=total_items,
                         total_pages=total_pages,
                         pagination_range=pagination_range)

@app.route('/page/<int:page>')
def pagination(page):
    keyword = request.args.get('keyword', '')
    search_type = request.args.get('search_type', 'all')

    if not keyword:
        flash('Mohon masukkan kata kunci pencarian', 'error')
        return render_template('index.html', books=[], page=1)

    books, total_items, total_pages = get_books_data(keyword, search_type, page)
    
    if not books:
        flash('Tidak ada buku yang ditemukan', 'info')

    pagination_range = get_pagination_range(page, total_pages)
    return render_template('index.html',
                         books=books,
                         page=page,
                         keyword=keyword,
                         search_type=search_type,
                         total_items=total_items,
                         total_pages=total_pages,
                         pagination_range=pagination_range)

@app.template_filter('format_number')
def format_number(value):
    """
    Filter untuk memformat angka dengan pemisah ribuan
    """
    return "{:,}".format(value)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)