#!/usr/bin/env python3
"""
Re-implementation of the COBOL BOOKFORUM program.
Run from the cobol/ directory.
"""

import os

def read_fixed_records(filename, record_size):
    """Read all fixed-length records from a file."""
    if not os.path.exists(filename):
        return []
    with open(filename, 'rb') as f:
        data = f.read()
    records = []
    for i in range(0, len(data), record_size):
        rec = data[i:i+record_size]
        if len(rec) < record_size:
            rec = rec + b' ' * (record_size - len(rec))
        records.append(rec)
    return records

def write_fixed_records(filename, records):
    """Write fixed-length records to a file (overwrite)."""
    with open(filename, 'wb') as f:
        for rec in records:
            f.write(rec)

def parse_account(rec):
    return {
        'id': rec[0:4].decode('ascii', errors='ignore').rstrip(),
        'name': rec[4:24].decode('ascii', errors='ignore'),
        'balance': int(rec[24:34].decode('ascii', errors='ignore') or '0')
    }

def format_account(acc):
    id_ = acc['id'].ljust(4)[:4]
    name = acc['name'].ljust(20)[:20]
    bal = f"{acc['balance']:010d}"
    return (id_ + name + bal).encode('ascii')

def parse_book(rec):
    return {
        'id': rec[0:4].decode('ascii', errors='ignore').rstrip(),
        'title': rec[4:24].decode('ascii', errors='ignore'),
        'owner': rec[24:28].decode('ascii', errors='ignore').rstrip()
    }

def format_book(book):
    id_ = book['id'].ljust(4)[:4]
    title = book['title'].ljust(20)[:20]
    owner = book['owner'].ljust(4)[:4]
    return (id_ + title + owner).encode('ascii')

def parse_trans(rec):
    return {
        'book': rec[0:4].decode('ascii', errors='ignore').rstrip(),
        'amount': int(rec[4:14].decode('ascii', errors='ignore') or '0'),
        'seller': rec[14:18].decode('ascii', errors='ignore').rstrip(),
        'buyer': rec[18:22].decode('ascii', errors='ignore').rstrip()
    }

def format_trans(trans):
    book = trans['book'].ljust(4)[:4]
    amount = f"{trans['amount']:010d}"
    seller = trans['seller'].ljust(4)[:4]
    buyer = trans['buyer'].ljust(4)[:4]
    return (book + amount + seller + buyer).encode('ascii')

def main():
    # Paths relative to cobol/ directory
    input_path = 'src/INPUT.DAT'
    accounts_path = 'data/ACCOUNTS.DAT'
    books_path = 'data/BOOKS.DAT'
    trans_path = 'data/TRANSACTIONS.DAT'

    # Read input (expected 22 bytes, pad if short)
    input_recs = read_fixed_records(input_path, 22)
    if not input_recs:
        print("Error: Input file is empty")
        return
    irec = input_recs[0]
    buyer_id = irec[0:4].decode('ascii', errors='ignore').rstrip()
    seller_id = irec[4:8].decode('ascii', errors='ignore').rstrip()
    book_id = irec[8:12].decode('ascii', errors='ignore').rstrip()
    amount_str = irec[12:22].decode('ascii', errors='ignore').strip()
    try:
        amount = int(amount_str) if amount_str else 0
    except ValueError:
        amount = 0

    # Validate users and book
    buyer_found = False
    seller_found = False
    book_found = False
    valid_owner = False

    accounts = [parse_account(r) for r in read_fixed_records(accounts_path, 34)]
    for acc in accounts:
        if acc['id'] == buyer_id:
            buyer_found = True
        if acc['id'] == seller_id:
            seller_found = True

    books = [parse_book(r) for r in read_fixed_records(books_path, 28)]
    for book in books:
        if book['id'] == book_id:
            book_found = True
            if book['owner'] == seller_id:
                valid_owner = True

    print(" ")  # as in COBOL

    if buyer_found and seller_found and book_found and valid_owner:
        # Process transaction
        # Update accounts
        for acc in accounts:
            if acc['id'] == buyer_id:
                acc['balance'] -= amount
            if acc['id'] == seller_id:
                acc['balance'] += amount
        write_fixed_records(accounts_path, [format_account(a) for a in accounts])

        # Update book owner
        for book in books:
            if book['id'] == book_id:
                book['owner'] = buyer_id
        write_fixed_records(books_path, [format_book(b) for b in books])

        # Append transaction
        new_trans = {
            'book': book_id,
            'amount': amount,
            'seller': seller_id,
            'buyer': buyer_id
        }
        # Read existing, append
        existing = read_fixed_records(trans_path, 22)
        existing.append(format_trans(new_trans))
        write_fixed_records(trans_path, existing)

        print("Transaction completed successfully")
    else:
        print("Transaction failed due to validation errors")

if __name__ == '__main__':
    main()
