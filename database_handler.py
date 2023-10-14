import sqlite3
import os
import time
import datetime
from texttable import Texttable


#This class is intended to handle the access to the database

# I have take this class from the internet, which was intended to connect to a MySql database, I have adapted to Sqlite
class bookDatabase:

    def __init__(self, database):
        self.database = database
        self.db_connection = None
        self.cursor = None

    def connect(self):
        try:
            self.db_connection = sqlite3.connect(self.database)
            self.cursor = self.db_connection.cursor()
            print("Connected to the database.")
        except Exception as e:
            print("Failed to connect to the database:", str(e))

    # This function executes the queries, and receives three parameters query(String), values(Tuple), CRUD(Boolean)
    # query: Is the SQL statement; 
    # values: Is thought to be a tuple which contains data to complement the query when booDatabase.execute_query() is called
    # CRUD: Is a boolean variable which indicates if the query has to be execute with a complement data variable (values) or not
    def execute_query(self, query, values, CRUD):
        if not self.db_connection:
            print("Unfornately there is no database connection, please run the program again...")
            return
        try:    
            if(CRUD):    
                self.cursor.execute(query, values)
                self.db_connection.commit()
                result = self.cursor.fetchall()
            else:
                self.cursor.execute(query)
                result = self.cursor.fetchall()
            return result
        except Exception as e:
            print("Failed to execute the query", str(e))
    # This function populate the database taking records from the books_data.txt
    def populate_db(self, author_list, book_list):
        if not self.db_connection:
            print("Please connect to the database first.")
            return

        try:
            self.cursor.executemany(''' INSERT INTO author (full_name) VALUES (?) ''', author_list)
            self.db_connection.commit()
            self.cursor.executemany(''' INSERT INTO book (id, title, year, stars, qty, id_author) VALUES (?,?,?,?,?,?) ''', book_list)
            self.db_connection.commit()
            return
        except Exception as e:
            print("populate_db - Failed to execute the query:", str(e))

    # This function closes the connection between the database and this program
    def close(self):
        if self.db_connection:
            self.cursor.close()
            self.db_connection.close()
            print("Connection closed.")

# End of the bookDatabase class

# This function retrives the data from the books_data.txt file and returns it into two lists (book_list) and (author_list)
def retriving_data():
    book_list = []    # To store the books
    author_list = []  # To store the authors
    aux_line = ""     # This is for making modification line by line
    f = open('data/books_data.txt','r') # Accessing to the file.
    for line in enumerate(f,1):
                    aux_line = line[1].split(",")
                    if line[0] < 22: # There are only 20 authors
                        author_tuple = (aux_line[0],)   # Author's full names
                        # Collecting all the author tuples
                        author_list.append(author_tuple)
                    else: 
                        # All the remaining lines in the file (variable f) are books.
                        aux_line[5] = str(aux_line[5]).replace("\n","") # Deleting \n from each line
                        book_tuple = (str(aux_line[0]), # Book id
                                    str(aux_line[1]), # Book title
                                    str(aux_line[2]), # Book published year
                                    int(aux_line[3]), # Book popularity (stars)
                                    int(aux_line[4]), # Book quantity (inventory)
                                    int(aux_line[5])) # Author's book (FK in Author Table)
                        book_list.append(book_tuple)
    f.close() # Closing the file
    return author_list, book_list
#This Function registers new books
def enter_new_book():
    os.system('cls' if os.name == 'nt' else 'clear') #Copied from internet to clear the screen
    id_book = validation_code(str(input("Please enter the code (four digits format 0000): ")))
    bookname = validation_name_book(str(input("Enter the name of the book: ")))
    year_publication = validation_year(input("Please, enter the year of the publication (four digits format 0000): "))
    print(popularity_aux)
    stars_book = validation_stars(input("\nFrom the list above, How popular do you think the book is?: "))
    qty_book = validation_qty(input("Please enter the number of books you have: "))
    os.system('cls' if os.name == 'nt' else 'clear') #Copied from internet
    print("Please, choose one of the following authors")
    result = db.execute_query('''SELECT id, full_name FROM author ORDER BY id''',"",False)
    id_name_author = listing_authors(result,True)
    if id_name_author == None:
        return
    else:
        print("\n Book to be registered: ")
        print("Code:       "+id_book)
        print("Title:      "+bookname)
        print("Published:  "+year_publication)
        print("Popularity: " + popularity[stars_book-1])
        print("Author:     " + id_name_author[1])
        if 'Y' == str(input("\nRegister this book: Y (yes) /N (no) ")).upper():
            db.execute_query(" INSERT INTO book (id, title, year, stars, qty, id_author) VALUES (?,?,?,?,?,?);",
                            (id_book, bookname, year_publication,stars_book,qty_book,int(id_name_author[0])),
                            True)
            print("Record successfully stored")
            time.sleep(2)
        else:
            print("No record was stored")
# This function validate the quantity of books to register based on the user input
def validation_qty(user_input):
    while True:
        try:
            return int(user_input)
        except Exception:
            print("Value entered is incorrect")
            time.sleep(2)
            user_input = input("\rPlease enter the number of books you have?: ")
#This function validates the popularity of a book based on the user input
def validation_stars(user_input):
    while True:
        try:
            if int(user_input) > 0 and int(user_input) < 6:
                return int(user_input)
        except Exception:
            print("Value entered is incorrect")
            time.sleep(2)
            user_input = input("\rFrom 1 to 5, How popular do you think the book is?: ")
#This function validates the year when the book was published based on the user input
def validation_year(user_input):
    date = datetime.datetime.now()
    year = date.year
    while True:
        try:
            if int(user_input) <= year:
                return user_input
            else:
                user_input = input("\n The year can not exceed the current date, please try again: ")
        except Exception:
            user_input = input("\rIncorrect format, please try again (four digits format 0000): ")  
#This function validates the name of a book, because titles must be unique based on the user input 
def validation_name_book(user_input):
    while True:
        result = db.execute_query(''' SELECT title FROM book WHERE title =? ''', (user_input,), True)
        if len(result) == 0:
            return user_input
        else:
            print("The name entered already exist                     ")
            time.sleep(2)
            user_input = str(input("Please enter a different name: "))      
#This function validates the code/ID of the book based on the user input
def validation_code(user_input):
    while True:
        if len(user_input) == 4 and user_input.isnumeric():
            result = db.execute_query(''' SELECT id FROM book WHERE id = ?''', (user_input,), True)
            if len(result) == 0:  #The entered code does not exist
                return user_input
            else:
                user_input = str(input(" \rCode already exist, please try again (four digits format 0000): "))        
        else:
            user_input = str(input(" \rIncorrect format, please try again (four digits format 0000): "))
#This function list the Authors and recibes two parameters
# query: is the statement(String) to be executed by bookDatabase.execute_query() function
# choose: is a boolean variable which indicates if we need to pick an author or just listing them
def listing_authors(result,choose):
    list_authors = [[' ID ',' Names']]  # The headers of the collunm
    id_authors = []                     # Id stored separately to search elements through it easily
    t = Texttable() 
    for id, line in result:
        list_authors.append([id,line])
        id_authors.append(id)
    t.add_rows(list_authors)
    print(t.draw())
    if choose:
        while True:
            id_entered = int(input("Please, enter the ID of the Author [Press 0 for a new author]: "))
            if id_entered == 0:
                enter_new_author()
                return None
            elif id_entered in id_authors:
                for id, line in result:
                    if id_entered == id:
                        id_authors = [id,line]
                        return id_authors
            else:            
                print("\rThe ID entered do not exist, please enter a different ID:              ")
# This function update an spcific book
def search_book():
    #Search submenu for books
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        user_choice = input('''\nWould you like to:
            1. See all books
            2. Search by year
            3. Search by Autor
            4. Search by popularity
            0. Back  <--
                    
            Enter selection: ''')
        
        if user_choice == '1':   # Logic to enter a new book
            result = db.execute_query('''SELECT book.id, book.title, book.year, book.stars, book.id_author, author.full_name FROM book INNER JOIN author ON book.id_author = author.id ORDER BY book.id;''',
                                      "", False)
            retriving_presenting_books(result)                        
        elif user_choice == '2': # Logic to search a book by year
            result = db.execute_query("SELECT year, COUNT(year) FROM book GROUP BY year;","",False)
            print("The years down below are counted in our system")
            print("\n*--------------------------*")
            for year, count in result:
                print ("    " + year + " - " + str(count) + " Title(s)")
                print("*--------------------------*")
            while True:
                year_input = validation_year(input("Please, enter the year of the publication (four digits format 0000): "))
                result = db.execute_query('''SELECT book.id, book.title, book.year, book.stars, book.id_author, author.full_name FROM book INNER JOIN author ON book.id_author = author.id WHERE book.year =? ORDER BY book.id;'''
                                              , (year_input,), True)
                if len(result) > 0:
                    retriving_presenting_books(result)
                    break
                else:
                    print("Wrong option, please enter again")
        elif user_choice == '3': # Logic to search a book by author
            while True:
                id_name_author = listing_authors("Please, enter the ID of the Author: ")
                result = db.execute_query('''SELECT book.id, book.title, book.year, book.stars, book.id_author, author.full_name FROM book INNER JOIN author ON book.id_author = author.id WHERE book.id_author =? ORDER BY book.id;'''
                                                , (id_name_author[0],), True)
                if len(result) > 0:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    retriving_presenting_books(result)
                    break
                else:
                    print("Wrong option, please enter again")
        elif user_choice == '4': # Logic to search a book by popularity
            os.system('cls' if os.name == 'nt' else 'clear')
            print(popularity_aux)
            while True:
                popularity_stars = validation_stars(input("\nChoose one of the options from the list above: "))            
                result = db.execute_query('''SELECT book.id, book.title, book.year, book.stars, book.id_author, author.full_name FROM book INNER JOIN author ON book.id_author = author.id WHERE book.stars =? ORDER BY book.id;'''
                                                , (popularity_stars,), True)
                if len(result) > 0:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    retriving_presenting_books(result)
                    break
                else:
                    print("Wrong option/There were not books with that popularity rate, please enter again")
                    time.sleep(2)
        elif user_choice == '0':
            # add logic here to quit appplication
            return
        else:
            os.system('cls' if os.name == 'nt' else 'clear') #Copied from internet
            print("\nOpps, wrong option\n")
            time.sleep(2)
#This function retrives the data and presents into a nice table
def retriving_presenting_books(data_set):
    list_books = [['ID','Title','Published','Popularity', 'Author']] 
    id_books = []                  # Id stored separately to search elements through it easily
    t = Texttable() 
    for line in data_set:
        list_books.append([line[0],
                           line[1],
                           line[2],
                           popularity[int(line[3])-1],
                           line[5]])
        id_books.append(line[0])
    t.add_rows(list_books)
    print(t.draw())
    id_entered = (input("\nPlease, enter the book ID to see more options: "))
    while True:
        if id_entered in id_books:
            for line in list_books:
                if line[0] == id_entered:
                            print("\nBOOK ID :   ",line[0])
                            print("Title:      ",line[1])
                            print("Published:  ",line[2])
                            print("Popularity: ",line[3])
                            print("Author:     ",line[4])
                            record_options(id_entered)
                            break
            break
        else:   
            message = "\rThe ID entered do not exist, please enter a different ID: "
            id_entered = input(message)
#This Function presents options for an specific book
def record_options(id_record):
    while True:
        try:
            user_input = int(input("\n  [1] Update    [2] Delete    [0] Cancel  [Chosse the option]: "))
            match user_input:
                case 1:
                    update_book_input = int(input('''\nWould you like to modify 
                                [1] Title
                                [2] Year of publication
                                [3] Popularity
                                [4] Number of items available
                                [5] Author
                                [0] Cancel
                                                 
                                Please choose one of the options: '''))
                    match update_book_input:
                        case 1:
                            new_value = validation_name_book(str(input("Enter the new name for the book: ")))
                            db.execute_query("UPDATE book SET title =? WHERE id=?;", (new_value,id_record),True)
                            print("Record successfully UPDATED")
                            break
                        case 2:
                            new_value = validation_year(input("Please, enter the year of the publication (four digits format 0000): "))
                            db.execute_query("UPDATE book SET year =? WHERE id=?;", (new_value,id_record), True)
                            print("Record successfully UPDATED")
                            break
                        case 3:
                            print("Please, choose the new popularity")
                            print(popularity_aux)
                            new_value = validation_stars(input("\nFrom the list above, How popular do you think the book is?: "))
                            db.execute_query("UPDATE book SET stars =? WHERE id=?;", (int(new_value),id_record), True)
                            print("Record successfully UPDATED")
                            break
                        case 4:
                            new_value = validation_qty(input("Please enter the number of books you have: "))
                            db.execute_query("UPDATE book SET qty =? WHERE id=?;", (int(new_value),id_record), True)
                            print("Record successfully UPDATED")
                            break
                        case 5:
                            print("Please, choose from the folowing list the new author: ")
                            new_value = listing_authors("Please, enter the ID of the Author")
                            db.execute_query("UPDATE book SET author_id =? WHERE id=?;", (int(new_value[0]),id_record), True)
                            print("Record successfully UPDATED")
                            break
                        case 0:
                            return
                case 2:
                    db.execute_query("DELETE FROM book WHERE id =?",(id_record,), True)
                    break
                case 0:
                    break
        except Exception:
            print("\nOpps, wrong option, please try again")

def enter_new_author():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(" NEW AUTHORS ")
    author_full_name = validate_author_name()
    print(author_full_name)    
    if 'Y' == str(input("\nRegister this author: Y (yes) /N (no) ")).upper():
        db.execute_query("INSERT INTO author (full_name) VALUES (?);", (author_full_name,),True)
        print("Author successfully stored")
        time.sleep(2)
    else:
        print("No record was stored")
#This function validates the name is not already in the database and return the input entered for saving it.
def validate_author_name():
    while True:
        full_name = input("Please enter the name of the Author: ")
        if not full_name:
            print("Please enter a name: ")
        else:
            aux_full_name = '%' + full_name + '%'
            result = db.execute_query("SELECT * FROM author WHERE full_name LIKE ?;", (aux_full_name,), True)
            if len(result) > 0:
                print("There were some similarities to your input: ")
                listing_authors(result,False)
                print("Please be aware the new author name must be different from the name(s) above...")
            if len(full_name) > 4:    
                return full_name
            else:
                print("\nInput too short to be considered a name, try again\n")

def search_author():
    result = db.execute_query('''SELECT id, full_name FROM author ORDER BY id''',"",False)
    id_name_author = listing_authors(result,True)
    print("\nID: " + str(id_name_author[0]) + " - Names: " + id_name_author[1])
    while True:
        option = input("\n[1] Update   [2] Delete   [0] Cancel   [Choose an option]: ")
        if option == '1':
            full_name = validate_author_name()
            print("\nCurrent name: ",id_name_author[1])           
            print("New name:       ",full_name)
            if 'Y' == str(input("\nUpdate this Author: Y (yes) /N (no) ")).upper():
                db.execute_query("UPDATE author SET full_name = ? WHERE id =?;", (full_name,id_name_author[0]),True)
                print("Author successfully updated")
                time.sleep(2)
                break
            else:
                print("No record was updated")
        elif option == '2':
            db.execute_query("DELETE FROM author WHERE id =?;", (id_name_author[0],),True)
            print("Author successfully deleted")
            time.sleep(2)
            break
        elif option == '0':
            break
        else: 
            print("Wrong option, please try again.")

def main_funtion():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        user_choice = 6
        try:
            user_choice = int(input('''\nWould you like to:
            1. Enter a book
            2. Search a book
            3. Enter an author
            4. Search an author
            0. Exit
                    
            Enter selection: '''))
        except:
            error_message = "\nINCORRECT INPUT - PLEASE TRY AGAIN."

        if user_choice == 1:   # Logic to enter a new book
            enter_new_book()
            os.system('cls' if os.name == 'nt' else 'clear') #Copied from internet
        elif user_choice == 2: # Logic Search a book
            search_book()
        elif user_choice == 3: # Logic to enter a new Author
            enter_new_author()
        elif user_choice == 4: # Logic to search an Author
            search_author()
        elif user_choice == 0:
            # add logic here to quit appplication
            print("\nThanks for using this system")
            quit()
        else:
            print(error_message)
            time.sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear') 

author_table = '''CREATE TABLE author (id INTEGER PRIMARY KEY,
                        full_name TEXT UNIQUE);'''
book_table = '''CREATE TABLE book (id TEXT,
                        title TEXT,
                        year TEXT,
                        stars INTEGER,
                        qty INTEGER,
                        id_author INTEGER,
                        FOREIGN KEY (id_author) REFERENCES author(id));'''
popularity = ['★','★★','★★★','★★★★','★★★★★']
popularity_aux = '''Popularity rate
                1. ★
                2. ★★ 
                3. ★★★ 
                4. ★★★★ 
                5. ★★★★★
                '''
db = bookDatabase('data/ebookstore')
db.connect()

db.execute_query(author_table,"",False)
db.execute_query(book_table,"",False)
author_list, book_list = retriving_data()
db.populate_db(author_list,book_list)
main_funtion()
db.close()







