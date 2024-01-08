from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import json

app = Flask(__name__)
CORS(app)

# Замените значения на свои параметры подключения к базе данных PostgreSQL
db_params = {
    'dbname': 'byecoins',
    'user': 'quango',
    'host': 'localhost',
    'port': '5432',
}

def execute_query(query, params=None):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    connection.close()
    return result

@app.route('/API', methods=['GET'])
def get_orders():
    # Получаем параметры запроса из URL
    transaction_type = request.args.get('transaction_type')
    crypto_type = request.args.get('crypto_type')
    amount = request.args.get('amount')
    currency = request.args.get('currency')
    payment_method = request.args.get('payment_method')
    sort_by_online = request.args.get('online_sort')
    sort_by_price = request.args.get('price_sort')

    # Подготавливаем условия для фильтрации
    conditions = []
    params = {}

    if transaction_type:
        conditions.append("transaction_type = %(transaction_type)s")
        params['transaction_type'] = transaction_type

    if crypto_type:
        conditions.append("crypto_type = %(crypto_type)s")
        params['crypto_type'] = crypto_type

    if currency:
        conditions.append("currency = %(currency)s")
        params['currency'] = currency

    if payment_method:
        conditions.append("payment_method = %(payment_method)s")
        params['payment_method'] = payment_method

    if amount:
        conditions.append("min_amount <= %(amount)s AND %(amount)s <= max_amount")
        params['amount'] = float(amount)

    if sort_by_online:
        if sort_by_online.lower() == 'true':
            conditions.append("online_status = true")
        # elif sort_by_online.lower() == 'false':
        #     conditions.append("online_status = false")
        # else:
        #     return jsonify({'error': 'Invalid value for online_sort'})

    # Создаем запрос с условиями, если они есть
    query = """
        SELECT 
            orders.order_id,
            orders.transaction_type,
            orders.crypto_type,
            users.avatar_link,
            users.nickname as user_nickname,
            ratings.rated_good,
            ratings.rated_bad,
            orders.online_status,
            orders.price,
            orders.min_amount,
            orders.max_amount,
            orders.payment_method,
            orders.currency,
            orders.comment
        FROM orders
        LEFT JOIN ratings ON orders.rating_id = ratings.rating_id
        LEFT JOIN users ON orders.user_id = users.user_id
    """
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Добавляем сортировку по цене по умолчанию
    default_sort = " ORDER BY price ASC"

    if sort_by_price:
        if sort_by_price.lower() == 'true':
            query += " ORDER BY price ASC"
        elif sort_by_price.lower() == 'false':
            query += " ORDER BY price DESC"
        else:
            return jsonify({'error': 'Invalid value for sort_by_price'})

    else:
        query += default_sort

    # Выполняем запрос с параметрами
    orders = execute_query(query, params)

    # Преобразование результата в формат JSON
    orders_json = []
    for order in orders:
        order_dict = {
            'order_id': order[0],
            'transaction_type': order[1],
            'crypto_type': order[2],
            'avatar_link': order[3],
            'user_nickname': order[4],
            'rated_good': order[5],
            'rated_bad': order[6],
            'online_status': float(order[7]),
            'price': float(order[8]),
            'min_amount': float(order[9]),
            'max_amount': order[10],
            'payment_method': order[11],
            'currency': order[12],
            'comment': order[13],
        }
        orders_json.append(order_dict)

    return jsonify({'orders': orders_json})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
