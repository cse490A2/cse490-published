def check_age(age):
    if age < 0:
        raise ValueError("age cannot be negative")
    return age >= 18
