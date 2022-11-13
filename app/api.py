from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.sql import text
from json import dumps
import flask_jsonpify
import time
import datetime
#import encoder
from app import app, encoder



db_connect = create_engine("")


def preventTimeOut(func):
    def wrapper(*args, **kwargs):
        #retry on timeout (once)
        try:
            x = func(*args, **kwargs)
        except sqlalchemy.exc.OperationalError as e:
            print(e)
            time.sleep(1)
            x = func(*args, **kwargs)
        except Exception as e:
            print(e)
            time.sleep(1)
            x = func(*args, **kwargs)
        return x
    return wrapper
  

@preventTimeOut
def get_channel_ID(ch_name):
    conn = db_connect.connect()
    queryString = text("select id from wordsonline where channel = :ch_name")

    try:
        query = conn.execute(queryString, {"ch_name":ch_name})
    except sqlalchemy.exc.OperationalError as e:
        print(e)
        query = conn.execute(queryString, {"ch_name":ch_name})

    result = [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
    conn.close()

    if len(result) > 0:
        return {'id': result[0]['id'],
            'enid': encoder.encode(result[0]['id'])
        }
    else:
        return None

@preventTimeOut
def check_auth(encoded_ch_ID=None, ch_name=None, viewPass=None, editPass=None):
    if ch_name == None and encoded_ch_ID== None:
        raise TypeError("check_auth() takes exactly one channel identifier (0 given)")
    if ch_name != None and encoded_ch_ID != None:
        raise TypeError("check_auth() takes exactly one channel identifier (2 given)")


    conn = db_connect.connect()
    if ch_name != None:
        queryString = text("select pass, viewPass from wordsonline where channel = :ch_name")
        query = conn.execute(queryString, {"ch_name":ch_name})
    else:
        queryString = text("select pass, viewPass from wordsonline where id = :ch_ID")
        query = conn.execute(queryString, {"ch_ID":encoder.decode(encoded_ch_ID)})
    conn.close()
    

    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}

    if len(result['data']) == 0:
        return True

    if (result['data'][0]['viewPass'] != None):
        if (result['data'][0]['pass'] == editPass and editPass != None):
            return True
        elif (result['data'][0]['viewPass'] != viewPass):
            return False

    if (result['data'][0]['pass'] != None):
        if (result['data'][0]['pass'] != editPass):
            return False

    return True

@preventTimeOut  
def get_channel_name(encoded_ch_ID):
    conn = db_connect.connect()
    queryString = text("select channel from wordsonline where id = :ch_ID")
    query = conn.execute(queryString, {"ch_ID":encoder.decode(encoded_ch_ID)})

    result = [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]
    conn.close()

    if len(result) > 0:
        return result[0]
    else:
        return None

@preventTimeOut
def get_words(encoded_ch_ID=None, ch_name=None, viewPass=None, editPass=None):
    if ch_name == None and encoded_ch_ID== None:
        raise TypeError("get_words() takes exactly one channel identifier (0 given)")
    if ch_name != None and encoded_ch_ID != None:
        raise TypeError("get_words() takes exactly one channel identifier (2 given)")


    conn = db_connect.connect()
    if ch_name != None:
        queryString = text("select * from wordsonline where channel = :ch_name")
        query = conn.execute(queryString, {"ch_name":ch_name})
    else:
        queryString = text("select * from wordsonline where id = :ch_ID")
        query = conn.execute(queryString, {"ch_ID":encoder.decode(encoded_ch_ID)})
    conn.close()
    

    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}

    if len(result['data']) == 0:
        return {'data':[]}


    result['data'][0]['enid'] = encoder.encode(result['data'][0]['id'])

    if (result['data'][0]['viewPass'] != None):
        if (result['data'][0]['pass'] == editPass and editPass != None):
            return result
        elif (result['data'][0]['viewPass'] != viewPass):
            result['data'][0].pop('viewPass')
            result['data'][0].pop('words')
            result['data'][0].pop('lastedit')
            result['data'][0]['permission'] = "No view access"
            result['data'][0].pop('pass')
            return result

    if (result['data'][0]['pass'] != None):
        if (result['data'][0]['pass'] != editPass):
            result['data'][0]['permission'] = "No edit access"
            result['data'][0].pop('pass')
            return result


    #result['data'][0].pop('pass')
    return result

@preventTimeOut  
def save_values(encoded_ch_ID=None, ch_name=None, editPass=None, viewPass=None, neweditPass=None, newviewPass=None, words=None):
    if ch_name == None and encoded_ch_ID== None:
        raise TypeError("get_words() takes exactly one channel identifier (0 given)")
    if ch_name != None and encoded_ch_ID != None:
        raise TypeError("get_words() takes exactly one channel identifier (2 given)")

    if len(words) > 5000:
        raise ValueError("words are too long")
    
    if len(newviewPass) > 50 or len(neweditPass) > 50:
        raise ValueError("passwords are too long")

    if len(ch_name) > 50:
        raise ValueError("channel name is too long")

    conn = db_connect.connect()
    if ch_name != None:
        queryString = text("select id, channel, pass, viewPass from wordsonline where channel = :ch_name")
        query = conn.execute(queryString, {"ch_name":ch_name})
    else:
        queryString = text("select id, channel, pass, viewPass from wordsonline where id = :ch_ID")
        query = conn.execute(queryString, {"ch_ID":encoder.decode(encoded_ch_ID)})

    result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
    if len(result['data']) == 0 and ch_name == None:
        conn.close()
        return {'result':"failed, no channel name provided"}
    elif (ch_name == None):
        ch_name = result['data'][0]['channel']

    
    if len(result['data']) == 0 and words == None:
        conn.close()
        return {'result':"failed, no initial words provided for new channel"}

    if (len(result['data']) == 0
        or (result['data'][0]['pass'] == None and result['data'][0]['viewPass'] == None)
        or (result['data'][0]['pass'] == editPass and editPass != None) 
        or (result['data'][0]['pass'] == None and result['data'][0]['viewPass'] == viewPass)):

        if (words != None):
            # query = conn.execute("INSERT INTO wordsonline (channel, words) VALUES('{0}', '{1}') ON DUPLICATE KEY UPDATE words = '{1}';".format(ch_name, words))
            queryString = text("INSERT INTO wordsonline (channel, words, lastedit) VALUES(:ch_name, :words, :dt) ON DUPLICATE KEY UPDATE words = :words, lastedit = :dt;")
            
            query = conn.execute(queryString, {"ch_name":ch_name, "words":words, "dt":str(datetime.datetime.now()) })
        
        if ((neweditPass != None or newviewPass != None)):
            query = "update wordsonline set "
            if neweditPass != None:
                if (neweditPass == ""):
                    query += "pass = NULL"
                else:
                    query += "pass = :neweditPass"#.format(neweditPass)
                if neweditPass != None:
                    query += ","


            if newviewPass != None:
                if (newviewPass == ""):
                    query += "viewPass = NULL"
                else:
                    query += " viewPass = :newviewPass"#.format(newviewPass)
                       
            query += ", lastedit = :dt where channel = :ch_name"#.format(ch_name)

            queryResult = conn.execute(text(query),{"neweditPass":neweditPass,"newviewPass":newviewPass,"ch_name":ch_name,"dt":str(datetime.datetime.now())})
    else:
        conn.close()
        return {'result':"failed, permission error"}

    conn.close()
    return {'result':"success", 'channel':ch_name}
    


if __name__ == "__main__":


    print(save_values(ch_name="test3", words="view only3", neweditPass="editpassword"))
    print(save_values(ch_name="oliver", neweditPass="sexy"))
    print(save_values(ch_name="test", newviewPass="true"))

    # print(get_channel_ID("acc"))
    # print(get_channel_ID("acdfghc"))
    # print()
    # print(get_channel_name("Lv"))
    # print(get_channel_name("Dq"))
    # print()
    # #print(get_words())
    # #print(get_words("Fd", "test"))
    # print(get_words("Fd"))
    
    # print(get_words("Dq"))
    # print(get_words(ch_name="snotes", editPass="test"))

    # print(get_words(ch_name="test", viewPass="test2"))
    # print(save_values(ch_name="test", words="wowowowowowowowow"))
    # print(save_values(ch_name="test", words="wowowowowowowowow", viewPass="test2"))
    
    # print(save_values(ch_name="test",words="very cool"))
