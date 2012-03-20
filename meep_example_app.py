import meeplib
import traceback
import cgi
import meepcookie
import Cookie

from jinja2 import Environment, FileSystemLoader

def initialize():
    # load pickle file
    meeplib.load_state()

    # create a default user
    u = meeplib.User('test', 'foo')

    # create a thread
    t = meeplib.Thread('Test Thread')

    # create a single message
    m = meeplib.Message('This is my message!', u)

    # save the message in the thread
    t.add_post(m)

    # done.

env = Environment(loader=FileSystemLoader('templates'))

def render_page(filename, **variables):
    template = env.get_template(filename)
    x = template.render(**variables)
    return str(x)

class MeepExampleApp(object):
    """
    WSGI app object.
    """
    def index(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/html')])
        # get cookie if there is one
        try:
            cookie = Cookie.SimpleCookie(environ["HTTP_COOKIE"])
            username = cookie["username"].value
        except:
            print "session cookie not set! defaulting username"
            username = ''

        user = meeplib.get_user(username)
        if user is None:
            return [ render_page('login.html') ]
        elif user is not None:
            return [ render_page('index.html', username=username) ]

    def create_user(self, environ, start_response):
        # get cookie if there is one
        try:
            cookie = Cookie.SimpleCookie(environ["HTTP_COOKIE"])
            username = cookie["username"].value
        except:
            username = ''
        
        user = meeplib.get_user(username)
        if user is not None:
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/'))
            start_response("302 Found", headers)
            return ["You must be logged out to use that feature."]

        headers = [('Content-type', 'text/html')]

        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        try:
            username = form['username'].value
        except KeyError:
            username = ''

        try:
            password = form['password'].value
        except KeyError:
            password = ''

        s=[]

        ##if we have username and password
        if username != '':
            user = meeplib.get_user(username)
            ## user already exists
            if user is not None:
                s.append('''Creation Failed! <br>
                    User already exists, please use a different username.<p>''')
            ## user doesn't exist but they messed up the passwords
            elif password == '':
                s.append('''Creation Failed! <br>
                    Please fill in the Password field<p>''')
            else:
                u = meeplib.User(username, password)
                meeplib.save_state()
                ## send back a redirect to '/'
                k = 'Location'
                v = '/'
                headers.append((k, v))
                cookie_name, cookie_val = meepcookie.make_set_cookie_header('username',username)
                headers.append((cookie_name, cookie_val))

        start_response('302 Found', headers)

        s.append(render_page("create_user.html", username=username))
        return [''.join(s)]

    def login(self, environ, start_response):
        try:
            cookie = Cookie.SimpleCookie(environ["HTTP_COOKIE"])
            username = cookie["username"].value
            #print "Username = %s" % username
        except:
            #print "session cookie not set! defaulting username"
            username = ''

        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        returnStatement = "logged in"
        try:
            username = form['username'].value
        except KeyError:
            username = None
        try:
            password = form['password'].value
        except KeyError:
            password = None
        k = 'Location'
        v = '/'

        # set content-type
        headers = [('Content-type', 'text/html')]

        # Test whether variable is defined to be None
        if username is not None:
             if password is not None:
                 if meeplib.check_user(username, password) is True:
                     new_user = meeplib.User(username, password)
                     meeplib.set_curr_user(username)
                     # set the cookie to the username string
                     cookie_name, cookie_val = meepcookie.make_set_cookie_header('username',username)
                     headers.append((cookie_name, cookie_val))
                 else:
                     returnStatement = """<p>Invalid user.  Please try again.</p>"""

             else:      
                 returnStatement = """<p>password was not set. User could not be created</p>"""
        else:
            returnStatement = """<p>username was not set. User could not be created</p>"""

        print """isValidafter: %s """ %(meeplib.check_user(username, password),)

       
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "no such content"    

    def logout(self, environ, start_response):
        # does nothing
        headers = [('Content-type', 'text/html')]

        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))

        cookie_name, cookie_val = meepcookie.make_set_cookie_header('username','')
        headers.append((cookie_name, cookie_val))

        start_response('302 Found', headers)
        
        return "no such content"

    def list_messages(self, environ, start_response):
        threads = meeplib.get_all_threads()
        
        # get cookie if there is one
        try:
            cookie = Cookie.SimpleCookie(environ["HTTP_COOKIE"])
            username = cookie["username"].value
            #print "Username = %s" % username
        except:
            #print "session cookie not set! defaulting username"
            username = ''
        
        user = meeplib.get_user(username)
        s = []
        if threads:
            s.append(render_page("list_messages.html", threads=threads, user=user))
        else:
            s.append("There are no threads to display.<p>")

        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)

        return ["".join(s)]

    def add_thread(self, environ, start_response):
        # get cookie if there is one
        try:
            cookie = Cookie.SimpleCookie(environ["HTTP_COOKIE"])
            username = cookie["username"].value
            #print "Username = %s" % username
        except:
            #print "session cookie not set! defaulting username"
            username = ''
        
        user = meeplib.get_user(username)
        if user is None:
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/'))
            start_response("302 Found", headers)
            return ["You must be logged in to use that feature."]

        headers = [('Content-type', 'text/html')]

        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        try:
            title = form['title'].value
        except KeyError:
            title = ''
        try:
            message = form ['message'].value
        except KeyError:
            message = ''

        s = []

        # title and message are non-empty
        if title == '' and message == '':
            pass
        elif title == '' and message != '':
            s.append("Title was empty.<p>")
        elif title != '' and message == '':
            s.append("Message was empty. <p>")
        elif title != '' and message != '':
            new_message = meeplib.Message(message, user)
            t = meeplib.Thread(title)
            t.add_post(new_message)
            meeplib.save_state()
            headers.append(('Location','/m/list'))
            
        start_response("302 Found", headers)

        # doesn't get executed if we had valid input and created a thread
        s.append(render_page("add_message.html", title=title, message=message))

        return ["".join(s)]


    def delete_message_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        print form

        thread_id = int(form['thread_id'].value)
        
        post_id = int(form['post_id'].value)

        t = meeplib.get_thread(thread_id)
        post = t.get_post(post_id)
        t.delete_post(post)

        meeplib.save_state()

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)

        return["post deleted"]
        
    def reply(self, environ, start_response):
          # get cookie if there is one
        try:
            cookie = Cookie.SimpleCookie(environ["HTTP_COOKIE"])
            username = cookie["username"].value
            #print "Username = %s" % username
        except:
            #print "session cookie not set! defaulting username"
            username = ''
        
        user = meeplib.get_user(username)
        if user is None:
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/'))
            start_response("302 Found", headers)
            return ["You must be logged in to use that feature."]

        headers = [('Content-type', 'text/html')]

        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        thread_id = int(form['thread_id'].value)
        t = meeplib.get_thread(thread_id)
        
        s = []

        try:
            post = form['post'].value
        except KeyError:
            post = ''

        # post is non-empty
        if post != '':
            new_message = meeplib.Message(post, user)
            t.add_post(new_message)
            meeplib.save_state()
            headers.append(('Location','/m/list'))

        start_response("302 Found", headers)

        # doesn't get executed unless we had invalid input
        s.append(render_page("reply.html", thread=t))
        return ["".join(s)]
    
    def __call__(self, environ, start_response):
        # store url/function matches in call_dict
        call_dict = { '/': self.index,
                      '/create_user': self.create_user,
                      '/login': self.login,
                      '/logout': self.logout,
                      '/m/list': self.list_messages,
                      '/m/add_thread': self.add_thread,
                      '/m/delete_action': self.delete_message_action,
                      '/m/reply': self.reply,
                      }

        # see if the URL is in 'call_dict'; if it is, call that function.
        url = environ['PATH_INFO']
        fn = call_dict.get(url)

        if fn is None:
            start_response("404 Not Found", [('Content-type', 'text/html')])
            return ["Page not found."]

        try:
            # allows us to trace the threads and users during every call	
            # especially useful under nose if a test fails
	
            """print "Threads: "
            for key in meeplib._threads:
                print "k: ", key
                print "v: ", meeplib._threads[key].title
            print "Users: "
            for key in meeplib._user_ids:
                print "k: ", key
                print "v: ", meeplib._user_ids[key].username"""

            return fn(environ, start_response)
        except:
            tb = traceback.format_exc()
            print tb
            x = "<h1>Error!</h1><pre>%s</pre>" % (tb,)

            status = '500 Internal Server Error'
            start_response(status, [('Content-type', 'text/html')])
            return [x]
