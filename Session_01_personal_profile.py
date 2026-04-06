print("Welcome to the Personal Profile Generator!")
print("Answer the 5 question to create your profile")
print()

user_name = input("What is your name?")
user_city = input("Which city you are in?")
user_goal = input("What is your goal?")

user_age_str = input("What is your age?")
user_age = int(user_age_str)

user_hobby = input("What is your hobby?")

user_height = float(input("What is your height?"))

profile_card = f"""

==================================================
              YOUR PROFILE CARD
==================================================
    Name  :              {user_name}
    City  :              {user_city}
    Age   :               {user_age}
    Height:               {user_height}
    Hobby :              {user_hobby}
    Goal  :              {user_goal}
==================================================
"""

print(profile_card)
print(f"Thank you {user_name}. Your profile has been created!")