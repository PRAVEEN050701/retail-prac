VERSION = "1.1.0-release"


def payment():
    return "Payment successful"


def product():
    return "Product available"

def search():
    return "Search available"

def cart():
    return "Cart available"


if __name__ == "__main__":
    print(f"Retail App - Version {VERSION}")
    print(payment())
    print(product())