import twill

twill.execute_file("add_message.twill", initial_url="http://localhost:8008")
twill.execute_file("add_user.twill", initial_url="http://localhost:8008")
twill.execute_file("delete_message.twill", initial_url="http://localhost:8008")
twill.execute_file("msg_reply.twill", initial_url="http://localhost:8008")
