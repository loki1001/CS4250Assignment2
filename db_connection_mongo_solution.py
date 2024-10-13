#-------------------------------------------------------------------------
# AUTHOR: Lokaranjan Munta
# FILENAME: db_connection_mongo_solution.py
# SPECIFICATION: The program has the operations to manage documents in a MongoDB collection. It has create, delete,
# update, and the creation of an inverted index. Each document has an id, text, title, date, and category. The text is
# cleaned of punctuation and word occurence is counted and stored in the document. The program also has a function to
# create an inverted index of the terms and their occurence across the different documents.
# FOR: CS 4250- Assignment #2
# TIME SPENT: how long it took you to complete the assignment
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

#importing some Python libraries
from pymongo import MongoClient
from datetime import datetime

def connectDataBase():
    # Create a database connection object using pymongo
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Assignment2"]
    return db

def createDocument(col, docId, docText, docTitle, docDate, docCat):
    # Check if document with the same _id exists
    if col.find_one({"_id": docId}):
        print(f"Document with ID {docId} exists. Not inserting.")
        return

    # Validate the date format
    try:
        date = datetime.strptime(docDate, "%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format for {docId}. Expected: YYYY-MM-DD.")
        return

    # create a dictionary (document) to count how many times each term appears in the document.
    # Use space " " as the delimiter character for terms and remember to lowercase them.
    words = docText.lower().split(" ")

    # NEED TO REMOVE PUNCTUATION
    clean_words = [''.join(char for char in word if char.isalnum()) for word in words]
    clean_words = [word for word in clean_words if word]

    term_count = {}
    for word in clean_words:
        term_count[word] = term_count.get(word, 0) + 1

    # create a list of dictionaries (documents) with each entry including a term, its occurrences, and its num_chars. Ex: [{term, count, num_char}]
    terms = []
    for term, count in term_count.items():
        terms.append({
            "term": term,
            "count": count,
            "num_chars": len(term)
        })

    #Producing a final document as a dictionary including all the required fields
    document = {
        "_id": docId,
        "title": docTitle,
        "text": docText,
        "num_chars": sum(len(term) for term in clean_words),
        "date": date,
        "category": docCat,
        "terms": terms
    }

    # Insert the document
    col.insert_one(document)
    print(f"Document with ID {docId} created.")

def deleteDocument(col, docId):
    # Delete the document from the database
    result = col.delete_one({"_id": docId})

    if result.deleted_count > 0:
        print(f"Document with ID {docId} deleted successfully")
    else:
        print(f"No document found with ID {docId}")

def updateDocument(col, docId, docText, docTitle, docDate, docCat):
    # Delete the document
    deleteDocument(col, docId)

    # Create the document with the same id
    createDocument(col, docId, docText, docTitle, docDate, docCat)

def getIndex(col):
    # Query the database to return the documents where each term occurs with their corresponding count. Output example:
    # {'baseball':'Exercise:1','summer':'Exercise:1,California:1,Arizona:1','months':'Exercise:1,Discovery:3', ...}
    # We are simulating an inverted index here in memory.
    inverted_index = {}

    '''
    pipeline = [
        {"$unwind": "$terms"},
        {"$group": {"_id": "terms.term", ""}}
    ]
    '''

    documents = col.find({})

    for document in documents:
        for term_detail in document["terms"]:
            term = term_detail["term"]
            count = term_detail["count"]
            category = document["title"]

            entry = f"{category}:{count}"

            if term in inverted_index:
                inverted_index[term].append(entry)
            else:
                inverted_index[term] = [entry]

    for term in inverted_index:
        inverted_index[term] = ','.join(inverted_index[term])

    return inverted_index

