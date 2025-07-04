import mysql.connector
from datetime import datetime

#Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="passwordmysql",
    database="libmansys"
)

cursor = db.cursor()

'''#Adding initial data to the tables
#Adding initial books
books = [
    ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", 5),
    ("The Hobbit", "J.R.R. Tolkien", 3),
    ("1984", "George Orwell", 4),
    ("To Kill a Mockingbird", "Harper Lee", 2),
    ("The Catcher in the Rye", "J.D. Salinger", 3)
] '''

'''for book in books:
    #Checking if the book already exists
    cursor.execute("SELECT * FROM books WHERE title = %s", (book[0],))
    if cursor.fetchone() is None:  # If the book does not exist
        cursor.execute('''
            #INSERT INTO books (title, author, available_copies)
           # VALUES (%s, %s, %s)
           #''', book)
           #     print(f"Added book: {book[0]}")
   #else:
        #print(f"Book already exists: {book[0]}") 

'''Add initial members
# members = [
#     ("Alice Smith", "alice@example.com"),
#     ("Bob Johnson", "bob@example.com"),
#     ("Charlie Brown", "charlie@example.com")
# ]

# for member in members:
#     cursor.execute('''
#         INSERT INTO members (name, email)
#         VALUES (%s, %s)
#     ''', member) '''

''' Adding initial transactions (borrowing books)
transactions = [
    (1, 1, '2024-11-01'),  # Alice borrowed "Harry Potter"
    (2, 2, '2024-11-05'),  # Bob borrowed "The Hobbit"
    (3, 3, '2024-11-10')   # Charlie borrowed "1984"
]

for transaction in transactions:
    cursor.execute('''
       # INSERT INTO transactions (book_id, member_id, borrow_date)
       # VALUES (%s, %s, %s)
    #''', transaction)

'''#Committing all changes to the database
db.commit()

print("Initial data has been inserted into the tables.") '''


#fetch 
'''cursor.execute("SELECT * FROM books")
books = cursor.fetchall()
for book in books:
    print(book) '''


'''#update
cursor.execute('''
    #UPDATE books
    #SET available_copies = %s
    #WHERE title = %s
''', (8, "1984"))
db.commit()
print("Book updated successfully.") '''

'''#delete
#Deleting transactions related to the book first
cursor.execute('''
   # DELETE t FROM transactions t
   # JOIN books b ON t.book_id = b.book_id
   # WHERE b.title = %s
''', ("1984",))  # Replace with the title of the book you're deleting
db.commit()


#Then delete the book
cursor.execute('''
   # DELETE FROM books
   # WHERE title = %s
''', ("1984",))  # Replace with the title of the book you're deleting
db.commit()
print("Book deleted successfully.")


'''
''' #input

choice = input("Enter 1 to add a book, 2 to view books: ")

if choice == "1":
    title = input("Enter book title: ")
    author = input("Enter author name: ")
    copies = int(input("Enter available copies: "))
    cursor.execute('''
       # INSERT INTO books (title, author, available_copies)
      #  VALUES (%s, %s, %s)
   # ''', (title, author, copies))
 #  db.commit()
  #'''  print("Book added successfully.")
'''elif choice == "2":
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    for book in books:
        print(book)
else:
    print("Invalid choice.")

'''
#Adding a new member
def add_member():
    name = input("Enter member name: ")
    email = input("Enter member email: ")

    #Check if email already exists in the members table
    cursor.execute("SELECT * FROM members WHERE email = %s", (email,))
    existing_member = cursor.fetchone()
    
    if existing_member:
        print(f"Error: The email {email} is already registered. Please use a different email.")
        return

    try:
        cursor.execute(''' 
            INSERT INTO members (name, email)
            VALUES (%s, %s)
        ''', (name, email))
        db.commit()

        #Retrieve the auto-generated member_id
        member_id = cursor.lastrowid
        print(f"Member added successfully! Your Member ID is {member_id}. Please note it for future use.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")



#Borrowing a book
def borrow_book():
    try:
        #Display all books with available copies
        cursor.execute("SELECT book_id, title, author, available_copies FROM books WHERE available_copies > 0")
        books = cursor.fetchall()
        
        if not books:
            print("No books are currently available for borrowing.")
            return
        
        print("\nAvailable Books:")
        for book in books:
            print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Available Copies: {book[3]}")

        #Prompt user for inputs
        book_id = int(input("\nEnter the Book ID of the book you want to borrow: "))
        member_id = int(input("Enter your Member ID: "))

        #Validate member ID
        cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
        member = cursor.fetchone()
        if not member:
            print("Member ID not found. Please try again.")
            return

        #Check if the selected book exists and is available
        cursor.execute("SELECT * FROM books WHERE book_id = %s AND available_copies > 0", (book_id,))
        book = cursor.fetchone()
        if not book:
            print("Book ID not found or the book is no longer available.")
            return

        #Proceed with borrowing
        borrow_date = datetime.now().date()
        cursor.execute('''
            INSERT INTO transactions (book_id, member_id, borrow_date)
            VALUES (%s, %s, %s)
        ''', (book_id, member_id, borrow_date))

        cursor.execute('''
            UPDATE books
            SET available_copies = available_copies - 1
            WHERE book_id = %s
        ''', (book_id,))

        db.commit()
        print(f"\nBook '{book[1]}' borrowed successfully by Member ID {member_id}.")
    
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    except ValueError:
        print("Invalid input. Please enter numeric IDs.")

#Returning a book
def return_book():
    try:
        #Prompt the user for their Member ID
        member_id = int(input("Enter your Member ID: "))

        #Validate the Member ID
        cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
        member = cursor.fetchone()
        if not member:
            print("Member ID not found. Please try again.")
            return

        #Fetch books borrowed by the member that have not been returned
        cursor.execute('''
            SELECT t.transaction_id, b.book_id, b.title, b.author, t.borrow_date
            FROM transactions t
            JOIN books b ON t.book_id = b.book_id
            WHERE t.member_id = %s AND t.return_date IS NULL
        ''', (member_id,))
        borrowed_books = cursor.fetchall()

        if not borrowed_books:
            print("You have no books to return.")
            return

        #Display the borrowed books
        print("\nBooks you have borrowed:")
        for book in borrowed_books:
            print(f"Transaction ID: {book[0]}, Book ID: {book[1]}, Title: {book[2]}, Author: {book[3]}, Borrow Date: {book[4]}")

        #Prompt the user to select a transaction to return
        transaction_id = int(input("\nEnter the Transaction ID of the book you are returning: "))

        #Check if the selected Transaction ID is valid
        valid_transaction_ids = [book[0] for book in borrowed_books]
        if transaction_id not in valid_transaction_ids:
            print("Invalid Transaction ID. Please try again.")
            return

        #Record the return date and update available copies
        return_date = datetime.now().date()
        cursor.execute('''
            UPDATE transactions
            SET return_date = %s
            WHERE transaction_id = %s
        ''', (return_date, transaction_id))

        cursor.execute('''
            UPDATE books
            SET available_copies = available_copies + 1
            WHERE book_id = (SELECT book_id FROM transactions WHERE transaction_id = %s)
        ''', (transaction_id,))

        db.commit()
        print("Book returned successfully.")
    
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    except ValueError:
        print("Invalid input. Please enter numeric values.")

#Search feature to search for books
def search_books():
    search_query = input("Enter book title or author: ").lower()  # Convert user input to lowercase
    cursor.execute(''' 
        SELECT * FROM books WHERE LOWER(title) LIKE %s OR LOWER(author) LIKE %s
    ''', ('%' + search_query + '%', '%' + search_query + '%'))
    books_found = cursor.fetchall()

    if books_found:
        print("Search Results:\n")
        for book in books_found:
            print(f"Book ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Available Copies: {book[3]}\n")
    else:
        print("No books found with that title or author.")

def view_members():
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()

    if members:
        print("\nMembers List:")
        for member in members:
            print(f"Member ID: {member[0]}")
            print(f"Name: {member[1]}")
            print(f"Email: {member[2]}\n")
    else:
        print("No members found.")

#Look up member ID by email
def lookup_member_id():
    email = input("Enter your email to find your Member ID: ")
    cursor.execute('''
        SELECT member_id, name FROM members WHERE email = %s
    ''', (email,))
    member = cursor.fetchone()
    
    if member:
        print(f"Member ID for {member[1]} is {member[0]}")
    else:
        print("No member found with that email.")

#Command menu loop
while True:
    print("\nLibrary Management System")
    print("1. Add Book")
    print("2. View Books")
    print("3. Add Member")
    print("4. Borrow Book")
    print("5. Return Book")
    print("6. Search Books")
    print("7. Look Up Member ID")
    print("8. to view members")
    print("9. Exit")
    
    choice = input("Enter your choice: ")
    
    if choice == "1":
        title = input("Enter book title: ")
        author = input("Enter author name: ")
        copies = int(input("Enter available copies: "))
        cursor.execute("SELECT * FROM books WHERE title = %s", (title,))
        if cursor.fetchone() is None:
            cursor.execute('''
            INSERT INTO books (title, author, available_copies)
            VALUES (%s, %s, %s)
        ''', (title, author, copies))
            db.commit()
            print("Book added successfully.")
        else:
            print("Book already exists.")

    elif choice == "2":
       cursor.execute("SELECT * FROM books")
       books = cursor.fetchall()  # Fetch all rows from the query result
       if books:  # Check if there are books in the table
            print("\nBooks in Library:")
            for book in books:
                 print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Available Copies: {book[3]}")
       else:
        print("\nNo books available in the library.")
    
    elif choice == "3":
        add_member()
    elif choice == "4":
        borrow_book()
    elif choice == "5":
        return_book()
    elif choice == "6":
        search_books()
    elif choice == "7":
        lookup_member_id()
    elif choice == '8':  
        view_members()
    elif choice == "9":
        print("Exiting...")
        break
    else:
        print("Invalid choice. Please try again.")

