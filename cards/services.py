import secrets
from datetime import UTC, datetime


def calculate_luhn_digit(number: str) -> str:
    total = 0
    for index, value in enumerate(reversed(number)):
        digit = int(value)
        if index % 2 == 0:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return str((10 - total % 10) % 10)


def generate_card_data() -> dict[str, str]:
    network = secrets.choice(["V", "M"])
    prefix = "4" if network == "V" else "5"
    partial_number = prefix + "".join(str(secrets.randbelow(10)) for _ in range(14))
    number = partial_number + calculate_luhn_digit(partial_number)
    month = str(secrets.randbelow(12) + 1).zfill(2)
    year = str(datetime.now(UTC).year + 10)[2:]
    return {
        "name": "DIO Bank Platinum",
        "last_four": number[-4:],
        "token": secrets.token_urlsafe(32),
        "network": network,
        "expiration_date": f"{month}/{year}",
    }
