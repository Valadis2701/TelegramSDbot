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

def is_image_completely_black(image_data):
    black_px_pattern = b"\x00" * 300
    consecutive_count = 0

    for i in range(len(image_data)):
        if image_data[i:i + 300] == black_px_pattern:
            consecutive_count += 1
        else:
            consecutive_count = 0

        if consecutive_count >= 300:
            return True

    return False

