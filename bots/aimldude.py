"""

Could this be simpler? Unlikely.
SDC 1/25/2012

To make use of multiple sessions, you use the optional sessionID parameter (supported by the respond(), getPredicate() and setPredicate() Kernel methods). The session ID can be anything: a string containing the user's name, an IRC channel name, an IP address...so long as it uniquely idenitifies the conversation. So, if you're having a conversation with two users, Alice and Bob, and you receive some new input from Bob, you'd make the following call:

response = Kernel.respond(input, "Bob")
<srai>call me <star/></srai>  My name is <bot name="name"/>.

"""

import aiml
k = aiml.Kernel()
k.setBotPredicate("name","doorbot")
k.setPredicate("name","shithead")
k.learn("std-startup.xml")
k.respond("load aiml b")



while True: print k.respond(raw_input("> "))
