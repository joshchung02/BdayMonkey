import discord
import pickle
import "token.py"

async def send_message(message, response, is_private):
    try:
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def run_bot():
    client = discord.Client(intents=discord.Intents.all())
    CC = '-' # Command Char: Character to use commands

    # Bot going online
    @client.event
    async def on_ready():
        print(f"{client.user} is now running!")

    # When a message is sent by anyone
    @client.event
    async def on_message(message):
        if message.author == client.user:
            # Infinite loop protection
            return

        user_message = str(message.content)

        if user_message[0] != CC:
            # Command not used, do nothing
            return
        else:
            # Command used
            user_message = user_message[1:] # Get rid of command character
            message_parts = user_message.split(' ') # Get an array of the different parts of the message

            # MONKEY COMMAND (make monkey sounds)
            if user_message == "monkey":
                response = "ooh ooh ah ah!"
                await send_message(message, response, is_private=False)

            if user_message == "help":
                # help command (provides instructions for using the bot)
                response = f"```Commands:\n{CC}add name [M/D, M/DD, MM/D, MM/DD]: Add a birthday\n{CC}remove name: Remove a birthday\n{CC}display: Display all birthdays\n{CC}monkey: monkey```"
                await send_message(message, response, is_private=False)
            elif user_message == "display":
                # display command (display all birthdays)
                try:
                    with open('birthday_list.pkl', 'rb') as birthday_pickle:
                        birthday_list = pickle.load(birthday_pickle)
                        if len(birthday_list) == 0:
                            response = "The birthday list is empty!"
                            await send_message(message, response, is_private=False)
                            return
                except EOFError:
                    response = "The birthday list is empty!"
                    await send_message(message, response, is_private=False)
                
                response = ""
                for name in birthday_list:
                    response += f"{name}: {birthday_list[name]}" + '\n'
                await send_message(message, response, is_private=False)
            
            # add command (add a birthday)
            if message_parts[0] == "add" and len(message_parts) == 3:
                name = message_parts[1]
                birthday = message_parts[2]

                # make sure birthday is a valid date (MM/DD)
                if not validate_birthday(birthday):
                    response = "Birthday is invalid!"
                    await send_message(message, response, is_private=False)
                    return

                if len(birthday) == 3:
                    birthday = '0' + birthday[0] + birthday[1] + '0' + birthday[2]
                elif len(birthday) == 4 and birthday[1] == '/':
                    birthday = '0' + birthday
                elif len(birthday) == 4 and birthday[2] == '/':
                    birthday = birthday[0:3] + '0' + birthday[3]

                try:
                    with open('birthday_list.pkl', 'rb') as birthday_pickle:
                        birthday_list = pickle.load(birthday_pickle)
                except EOFError:
                    birthday_list = {}
                
                # Add new birthday and pickle
                if name not in birthday_list:
                    # Insert sorted
                    dictAsList = [(k, v) for k, v in birthday_list.items()]  # Temporarily convert dict to list
                    inserted = False
                    for i in range(len(dictAsList)):
                        if cmp_birthdays(birthday, dictAsList[i][1]):
                            dictAsList.insert(i, (name, birthday))
                            inserted = True
                            break
                    if not inserted:
                        dictAsList.append((name, birthday))
                    # Convert list back to dict
                    newDict = {}
                    for a, b in dictAsList:
                        newDict[a] = b
                    birthday_list = newDict

                    with open('birthday_list.pkl', 'wb') as birthday_pickle:
                        pickle.dump(birthday_list, birthday_pickle)

                    response = f"{name}'s birthday has been added"
                    await send_message(message, response, is_private=False)
                else:
                    response = "No repeated names allowed"
                    await send_message(message, response, is_private=False)
                    return

            # remove command (remove a birthday)
            if message_parts[0] == "remove" and len(message_parts) == 2:
                name = message_parts[1]

                # load the birthday list
                try:
                    with open('birthday_list.pkl', 'rb') as birthday_pickle:
                        birthday_list = pickle.load(birthday_pickle)
                except EOFError:
                    response = "The birthday list is empty, no birthday to remove"
                    await send_message(message, response, is_private=False)

                # remove birthday using name as key
                error_msg = "Not found, nothing removed"
                popped = birthday_list.pop(name, error_msg)  # Remove from list
                if popped == error_msg:
                    await send_message(message, error_msg, is_private=False)
                    return
                with open('birthday_list.pkl', 'wb') as birthday_pickle:
                    pickle.dump(birthday_list, birthday_pickle)
                
                response = f"{name}'s birthday has been removed"
                await send_message(message, response, is_private=False)

    client.run(TOKEN)

def validate_birthday(birthday) -> bool:
    if len(birthday) < 3 or len(birthday) > 5:
        return False
    elif len(birthday) == 3 and birthday[1] != '/':
        return False
    elif len(birthday) == 4 and birthday[1] != '/' and birthday[2] != '/':
        return False
    elif len(birthday) == 5 and birthday[2] != '/':
        return False

    m_and_d = birthday.split('/')

    try:
        month = int(m_and_d[0])
    except ValueError:
        return False
    try:
        day = int(m_and_d[1])
    except ValueError:
        return False

    day_max = [None, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if month < 1 or month > 12:
        return False
    elif day < 1 or day > day_max[month]:
        return False
    else:
        return True

# Define a function that will determine which birthday comes first
# True = first bday <= second bday, False = first bday > second bday
def cmp_birthdays(bday1, bday2):
    m_and_d1 = bday1.split('/')
    m_and_d2 = bday2.split('/')
    m1 = int(m_and_d1[0])    # Month of first birthday
    d1 = int(m_and_d1[1])    # Day of first birthday
    m2 = int(m_and_d2[0])    # Month of second birthday
    d2 = int(m_and_d2[1])    # Day of first birthday

    if m1 == m2:
        if d1 <= d2:
            return True
        else:
            return False
    elif m1 < m2:
        return True
    else:
        return False

if __name__ == "__main__":
    run_bot()
