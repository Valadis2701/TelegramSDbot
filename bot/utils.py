import pprint
import telebot

pprint_handle = pprint.PrettyPrinter(indent=4)

def pp(obj):
    pprint_handle.pprint(obj)


def print_message(message, prefix=''):
    pprint_handle = pprint.PrettyPrinter(indent=4)
    attributes = vars(message)
    for attr, value in attributes.items():
        if isinstance(value, telebot.types.Message):
            print_message(value, prefix=f'{prefix}{attr}.')
        elif isinstance(value, (list, dict, telebot.types.Message)):
            print(f'>>>{prefix}{pp(attr)}:')
            pp(value)
        else:
            print(f'|||{prefix}{pp(attr)}: {pp(value)}')