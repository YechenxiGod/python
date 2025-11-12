from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Book(db.Model):
    __tablename__ = 'Books'

    BookID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ISBN = db.Column(db.String(20), nullable=False)
    Title = db.Column(db.String(200), nullable=False)
    Author = db.Column(db.String(100), nullable=False)
    Publisher = db.Column(db.String(100))
    Category = db.Column(db.String(50))
    Status = db.Column(db.String(10), default='在架')
    CreateDate = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    borrow_records = db.relationship('BorrowRecord', backref='book', lazy=True)

    def to_dict(self):
        return {
            'bookID': self.BookID,
            'isbn': self.ISBN,
            'title': self.Title,
            'author': self.Author,
            'publisher': self.Publisher,
            'category': self.Category,
            'status': self.Status,
            'createDate': self.CreateDate.isoformat() if self.CreateDate else None
        }


class BorrowRecord(db.Model):
    __tablename__ = 'BorrowRecords'

    RecordID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    BookID = db.Column(db.Integer, db.ForeignKey('Books.BookID'), nullable=False)
    BorrowerName = db.Column(db.String(50), nullable=False)
    BorrowDate = db.Column(db.Date, nullable=False)
    ReturnDate = db.Column(db.Date)
    Notes = db.Column(db.String(200))

    def to_dict(self):
        return {
            'recordID': self.RecordID,
            'bookID': self.BookID,
            'borrowerName': self.BorrowerName,
            'borrowDate': self.BorrowDate.isoformat() if self.BorrowDate else None,
            'returnDate': self.ReturnDate.isoformat() if self.ReturnDate else None,
            'notes': self.Notes,
            'book': self.book.to_dict() if self.book else None
        }