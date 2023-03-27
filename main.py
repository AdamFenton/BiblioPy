from urllib.request import urlopen,urlretrieve
import json
from pathlib import Path
import os 
import shutil
import pandas as pd


class Library(object):

    ''' Class that contains the entire collection of books and the 
    class methods that are specific to all books'''

    def __init__(self):
        self.books = self.get_books()


    def reset(self):
        ''' A small reset function that redinitialises the class. This function
            is called when a new book is added because, if a new book is added 
            to the library, the self.books attribute needs to be updated to 
            contain this new book.
        '''
        self.__init__()

    
    def get_books(self):
        ''' Return the Title column of the library dataframe in markdown format
            for pretty terminal printing. This function is called when initalising
            the class (and reinitialising it) for setting the value of the 
            self.books attribute
        '''
        lib = pd.read_csv('library.csv',sep='#',names=['Author','Title'])
        if len(lib['Title']) == 0:
            return "Your library is empty! Add some books!"
        lib.index = lib.index + 1 # Change index to start at 1 to maintain count
        return lib.to_markdown()
        
                 
            
    def addBook(self,isbn):

        ''' Create new instance of Book class and run the barcode_lookup 
        method.'''
        if len(str(isbn)) != 13:
            print('The ISBN provided (%s) is not EAN-13...skipping' % isbn)
        else:  
            book = Book(isbn)
            book.barcode_lookup()
            print(book.title,book.author)
            if book.author is not None:
                with open('templates/book_thumbnails.html','a') as HTML_file:
                    HTML_file.write(book.HTML_string+'\n')
                with open('library.csv', 'a') as library_database:
                    author_and_title = book.author + "#" + book.title + "\n"
                    library_database.write(author_and_title)
                self.sort_library()
        
        
        

    def sort_library(self):
        ''' Reorder the html file (for viewing on the web) and the library csv
            file so that they are in alphabetical order by author's 
            surname.          
        '''
        self.reset()
        with open('templates/book_thumbnails.html','r') as html_infile:  
            A = sorted(html_infile.readlines(), key = lambda x: x.split('thumbnails/')[1].split('_')[0])
        with open('templates/book_thumbnails.html','w') as html_outfile:  
            for idx in range(len(A)):
                html_outfile.write(A[idx])
        with open('library.csv','r') as csv_infile:  
            B = sorted(csv_infile.readlines(), key = lambda x: x.split('#')[0].split(' ')[1])
        with open('library.csv','w') as csv_outfile:  
            for idx in range(len(B)):
                csv_outfile.write(B[idx])






class Book:

    '''Umbrella class for all books. Contains the lookup function that uses
    google's API to fetch book information and thumbnails.
    
    If lookup fails (invalid ISBN), the __getattr__ funtion returns None for
    book details rather than breaking code. eg:
    
    Succcessful use case:
        book1 = Book('9781444720723') # Real book 
        book1.barcode_lookup()
        book1.title --> prints The Shining
        
    Unsuccessful use case:
        book2 = Book('0000000000000') # Not a real book
        book2.barcode_lookup()
        book2.title --> prints None'''

    
    def __init__(self,isbn):
        self.isbn = isbn

    def barcode_lookup(self):

        ''' Use google's API to lookup the ISBN of a book and return its
            title, author(s), publication date, page count and genre(s).
        '''

        Path("%s/static/thumbnails/" % os.getcwd()).mkdir(parents=True, exist_ok=True )
        api = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
        resp = urlopen(api + str(self.isbn))
        book_data = json.load(resp)

        try:
            volume_info = book_data["items"][0]["volumeInfo"]
            author = volume_info["authors"]
            if len(author) > 1:
                self.author = author[0]
            else:
                self.author = author[0]
            self.title = volume_info['title']
            self.published = volume_info['publishedDate']
            self.pages = volume_info['pageCount']
            self.surname = self.author.split(' ')[1].replace("'","")
            self.thumbnail_file = '{}_{}.jpeg'.format(self.surname,self.isbn)
            self.HTML_string = "<a href = 'book/{}'><img src='/static/thumbnails/{}'/>".format(self.isbn, self.thumbnail_file)
   
            try:
                self.genre = volume_info['categories']
            except:
                self.genre = None

        except:
           pass

        try:
            image = book_data['items'][0]["volumeInfo"]['imageLinks']['thumbnail']
            urlretrieve(image, "static/thumbnails/{}".format(self.thumbnail_file))
        except:
          shutil.copyfile('static/images/unknownCover.jpg', "static/thumbnails/{}".format(self.thumbnail_file))
        print(self.HTML_string)
        
    def __getattr__(self, item):
        '''If an attribute for an instance cannot be found, return None'''
        return None


# library = Library()

# library.addBook('9781784160593')
