import caldav

def get_principal(username, leg_token):
    client = caldav.DAVClient(url="https://caldav.yandex.ru/", username=username, password=leg_token)
    principal = client.principal()
    return principal

my_principal = get_principal("<user_email>", "<token>")