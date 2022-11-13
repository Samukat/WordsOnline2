from app import app

if __name__ == "__main__":
    app.secret_key = 'super secret key for wordsOnline'

    app.debug = False
    app.run(host="", port=80)


#pipreqs C:\Users\Sam\Desktop\coding\WordsOnline\newFlask\WordsOnline 
#for requirements
