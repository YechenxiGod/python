from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Book, BorrowRecord
from config import Config
from datetime import datetime, date
from sqlalchemy import func, text
import traceback

app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
db.init_app(app)
CORS(app)


def init_database():
    """初始化数据库"""
    try:
        with app.app_context():
            # 测试连接
            db.session.execute(text('SELECT 1'))
            print("✓ 数据库连接成功")

            # 创建表
            db.create_all()
            print("✓ 数据库表创建成功")

            # 插入示例数据（可选）
            if Book.query.count() == 0:
                sample_books = [
                    Book(ISBN='9787115546081', Title='软件工程', Author='张三', Publisher='清华大学出版社',
                         Category='计算机'),
                    Book(ISBN='9787121361972', Title='Java编程思想', Author='李四', Publisher='电子工业出版社',
                         Category='计算机'),
                    Book(ISBN='9787544291170', Title='百年孤独', Author='加西亚·马尔克斯', Publisher='南海出版公司',
                         Category='文学')
                ]
                db.session.bulk_save_objects(sample_books)
                db.session.commit()
                print("✓ 示例数据插入成功")

    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        print(traceback.format_exc())


# 初始化数据库
init_database()


# 路由定义
@app.route('/')
def hello():
    return jsonify({"message": "个人图书收藏管理系统 API", "status": "运行正常"})


@app.route('/api/books', methods=['GET'])
def get_all_books():
    """获取所有图书"""
    try:
        books = Book.query.all()
        return jsonify([book.to_dict() for book in books])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """根据ID获取图书"""
    try:
        book = Book.query.get_or_404(book_id)
        return jsonify(book.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/books', methods=['POST'])
def add_book():
    """添加新图书"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "没有提供数据"}), 400

        required_fields = ['isbn', 'title', 'author']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"字段 '{field}' 是必需的"}), 400

        book = Book(
            ISBN=data['isbn'],
            Title=data['title'],
            Author=data['author'],
            Publisher=data.get('publisher'),
            Category=data.get('category'),
            Status=data.get('status', '在架')
        )

        db.session.add(book)
        db.session.commit()

        return jsonify(book.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """更新图书信息"""
    try:
        book = Book.query.get_or_404(book_id)
        data = request.get_json()

        if 'isbn' in data:
            book.ISBN = data['isbn']
        if 'title' in data:
            book.Title = data['title']
        if 'author' in data:
            book.Author = data['author']
        if 'publisher' in data:
            book.Publisher = data['publisher']
        if 'category' in data:
            book.Category = data['category']
        if 'status' in data:
            book.Status = data['status']

        db.session.commit()
        return jsonify(book.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """删除图书"""
    try:
        book = Book.query.get_or_404(book_id)

        # 检查是否有未归还的借阅记录
        active_records = BorrowRecord.query.filter_by(BookID=book_id, ReturnDate=None).first()
        if active_records:
            return jsonify({"error": "该图书有未归还的借阅记录，无法删除"}), 400

        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "图书删除成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/api/books/search', methods=['GET'])
def search_books():
    """搜索图书"""
    try:
        keyword = request.args.get('keyword', '')
        if not keyword:
            books = Book.query.all()
        else:
            books = Book.query.filter(
                (Book.Title.like(f'%{keyword}%')) |
                (Book.Author.like(f'%{keyword}%'))
            ).all()

        return jsonify([book.to_dict() for book in books])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/books/stats/summary', methods=['GET'])
def get_summary_stats():
    """获取概要统计"""
    try:
        total_books = Book.query.count()
        borrowed_books = Book.query.filter_by(Status='借出').count()
        available_books = total_books - borrowed_books

        return jsonify({
            'totalBooks': total_books,
            'borrowedBooks': borrowed_books,
            'availableBooks': available_books
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/books/stats/category', methods=['GET'])
def get_category_stats():
    """获取分类统计"""
    try:
        result = db.session.execute(
            text("SELECT Category, COUNT(*) FROM Books GROUP BY Category")
        )

        stats = []
        for row in result:
            stats.append({
                'category': row[0] or '未分类',
                'count': row[1]
            })

        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("启动图书管理系统后端...")
    print("服务地址: http://localhost:5000")
    print("API文档: http://localhost:5000/")
    app.run(debug=True, host='0.0.0.0', port=5000)