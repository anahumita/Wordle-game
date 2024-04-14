import socket
import json
import threading
import echo_protocol as echo
import random

IP = '127.0.0.1'

leaderboard = {}

def create_report(expected, actual):
    report = ["none" for _ in range(len(expected))]
    for i in range(len(expected)):
        if expected[i] == actual[i]:
            report[i] = "green"
        elif actual[i] in expected:
            report[i] = "yellow"
    return report

def create_bad_guess_msg():
    return json.dumps({'type': 'bad_guess'})

def create_guessed_msg(expected, actual, player_name):
    global leaderboard
    if actual not in leaderboard:
        leaderboard[actual] = {'name': player_name, 'score': 0}
    leaderboard[actual]['score'] += 10
    return json.dumps({'type': 'guessed', 'value': create_report(expected, actual)})

def create_report_msg(expected, actual):
    return json.dumps({'type': 'report', 'value': create_report(expected, actual)})

def create_out_of_guesses_msg(expected, actual):
    return json.dumps({'type': 'out_of_guesses', 'value': create_report(expected, actual)})

def handle_client(client_socket, client_address):
    global leaderboard
    guesses = 0
    max_guesses = 6
    words = ['horse', 'house', 'canva', 'craps', 'scifi']
    word = random.choice(words)

    try:
        sock_wrapper = echo.SocketWrapper(client_socket)
        while True:
            msg = sock_wrapper.recv_msg()
            guesses += 1

            if not msg:
                print("Unexpected game exit.")
                break
            
            if len(msg) != len(word):
                bad_guess = create_bad_guess_msg()
                print(f'sending {bad_guess}')
                sock_wrapper.send_msg(bad_guess)
            elif msg == word:
                guessed = create_guessed_msg(word, msg, "Player")
                print(f'sending {guessed}')
                sock_wrapper.send_msg(guessed)
            elif guesses == max_guesses:
                out_of_guesses = create_out_of_guesses_msg(word, msg) 
                print(f'sending {out_of_guesses}')
                sock_wrapper.send_msg(out_of_guesses)
                break
            else:
                report = create_report_msg(word, msg)
                print(f'sending {report}')
                sock_wrapper.send_msg(report)
    except Exception as e:
        print(f"Error when handling client: {e}")
    finally:
        client_socket.close()
        print(f"Connection to client ({client_address[0]}:{client_address[1]}) closed")

if __name__ == "__main__":
    print("Welcome to Wordle Server!")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((IP, echo.PORT))
    sock.listen()

    while True:
        print("Ready to accept a client connection.")
        client_sock, addr = sock.accept()
        print(f"Accepted new client connection: {addr}")
        th = threading.Thread(target=handle_client, args=(client_sock, addr))
        th.start()
