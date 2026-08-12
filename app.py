from flask import Flask, jsonify, request
import sqlite3
import os

app = Flask(__name__)

# Путь к вашей базе данных на Amvera (в постоянном хранилище)
DB_PATH = '/data/your-database.db'  # поменяйте на имя вашего файла

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # чтобы возвращать данные как словари
    return conn

# 1. Список всех таблиц
@app.route('/api/tables')
def get_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return jsonify({'tables': tables})

# 2. Все данные из конкретной таблицы (с пагинацией)
@app.route('/api/table/<table_name>')
def get_table_data(table_name):
    # Пагинация: page и limit (по умолчанию 100 записей на страницу)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 100, type=int)
    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()

    # Проверяем, существует ли таблица (чтобы избежать SQL-инъекций)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': f'Table "{table_name}" not found'}), 404

    # Получаем общее количество строк
    cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`;")
    total = cursor.fetchone()['count']

    # Получаем данные с пагинацией
    cursor.execute(f"SELECT * FROM `{table_name}` LIMIT ? OFFSET ?;", (limit, offset))
    rows = cursor.fetchall()
    conn.close()

    # Преобразуем строки в список словарей
    data = [dict(row) for row in rows]

    return jsonify({
        'table': table_name,
        'page': page,
        'limit': limit,
        'total': total,
        'total_pages': (total + limit - 1) // limit,
        'data': data
    })

@app.route('/dashboard')
def dashboard():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>База данных онлайн</title>
        <style>
            body { font-family: Arial; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>📊 Мониторинг базы данных</h1>
        <div id="tables"></div>
        <hr>
        <div id="data"></div>

        <script>
            async function loadTables() {
                const res = await fetch('/api/tables');
                const json = await res.json();
                const div = document.getElementById('tables');
                div.innerHTML = '<h3>Таблицы:</h3> ' + json.tables.map(t => 
                    `<button onclick="loadTable('${t}')">${t}</button>`
                ).join(' ');
            }

            async function loadTable(name, page=1) {
                const res = await fetch(`/api/table/${name}?page=${page}`);
                const json = await res.json();
                const div = document.getElementById('data');
                if (json.error) {
                    div.innerHTML = `<p>Ошибка: ${json.error}</p>`;
                    return;
                }
                let html = `<h3>Таблица: ${json.table} (всего ${json.total} записей, страница ${json.page}/${json.total_pages})</h3>`;
                if (json.data.length === 0) {
                    html += '<p>Нет данных</p>';
                } else {
                    const cols = Object.keys(json.data[0]);
                    html += '<table><tr>' + cols.map(c => `<th>${c}</th>`).join('') + '</tr>';
                    json.data.forEach(row => {
                        html += '<tr>' + cols.map(c => `<td>${row[c] ?? ''}</td>`).join('') + '</tr>';
                    });
                    html += '</table>';
                }
                if (json.total_pages > 1) {
                    html += '<div>';
                    for (let i = 1; i <= json.total_pages; i++) {
                        html += `<button onclick="loadTable('${json.table}', ${i})">${i}</button>`;
                    }
                    html += '</div>';
                }
                div.innerHTML = html;
            }

            loadTables();
        </script>
    </body>
    </html>
    '''