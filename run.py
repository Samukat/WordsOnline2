from app import app

if __name__ == "__main__":
    app.secret_key = ''

    app.debug = True
    app.run()


#pipreqs C:\Users\Sam\Desktop\coding\WordsOnline\newFlask\WordsOnline 
#for requirements pipreqs --force C:\Users\Sam\Desktop\coding\WordsOnline\newFlask\WordsOnline 
