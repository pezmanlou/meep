import unittest
import meeplib

# note:
#
# functions start within test_ are discovered and run
#       between setUp and tearDown;
# setUp and tearDown are run *once* for *each* test_ function.

class TestMeepLib(unittest.TestCase):
    def setUp(self):
        meeplib._reset()
        u = meeplib.User('foo', 'bar')
        t = meeplib.Thread('the title')
        m = meeplib.Message('the content', u)
        t.add_post(m)

    def test_for_message_existence(self):
        x = meeplib.get_all_threads()[0]
        y = x.get_all_posts()

        print "message: %s" %(x.title,)
        assert len(y) >= 1
        assert x.title == 'test title FOO'
        assert y[0].post == 'this is my message'


    def test_message_ownership(self):
        x = meeplib.get_all_users()
        assert len(x) == 1
        u = x

        t = meeplib.get_all_threads()[0]
        x = t.get_all_posts()
        assert len(x) >= 1
        m = x
        print "mauthor: %s" %(m[0],)

    def test_get_next_user(self):
        x = meeplib._get_next_user_id()
        assert x != None

    def tearDown(self):
        meeplib._reset()

        assert len(meeplib._messages) == 0
        assert len(meeplib._users) == 0
        assert len(meeplib._user_ids) == 0

if __name__ == '__main__':
    unittest.main()
