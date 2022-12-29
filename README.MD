Role-assigning bot for the UWF Engineering Server.

/createclass <Class number> <Class name>
Creates a new class role. This role will be used to assign students to a class. Creates a new channel and voice chat for the class, hidden from the rest of the server. Role will be named by class number, while channels will be created by the class name. Class number will be passed as a string, while class name will be passed as a string with spaces, and requires quotes.

/addclass <Class number> 
Ran by a student, assigns them the role for a class. This allows them to see the class channel and voice chat. Uses the number of the class.

/removeclass <Class number>
Ran by a student, removes the role for a class from them. This removes their access to the class channel and voice chat. Uses the number of the class.

/deleteclass <Class number>
Deletes a class role. This role will be removed from all students, and the class channel and voice chat will be deleted. Uses the number of the class.