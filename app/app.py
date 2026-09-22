VERSION = "1.0.0"


def payment():
    return "Payment successful"


def product():
    return "Product available"


if __name__ == "__main__":
    print(f"Retail App - Version {VERSION}")
    print(payment())
    print(product())