import sys
import time


SECRET_PIN = "1337"

# Artificial delay for every correctly matched digit.
# This intentionally creates a timing side channel.
DELAY_PER_DIGIT = 0.08


def validate_pin(pin):
    if len(pin) != 4 or not pin.isdigit():
        return False

    for guessed_digit, correct_digit in zip(
        pin,
        SECRET_PIN
    ):
        if guessed_digit != correct_digit:
            return False

        time.sleep(DELAY_PER_DIGIT)

    return True


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python demo_validator.py <PIN>")
        sys.exit(2)

    pin = sys.argv[1]

    if validate_pin(pin):
        print("Correct")
        sys.exit(0)

    print("Incorrect")
    sys.exit(1)