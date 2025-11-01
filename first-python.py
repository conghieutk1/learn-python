print("Em")
print("Em")
age = 21
print("I am " + str(age+1) + " years old")
print("I am", age, "years old")
print(f"I am {age} years old")

x, y, z = 1, 2, 3
print(x, y, z)
a = b = c = 0
print(a, b, c)

# name = input("Enter your name: ")
# phone_number = input("Enter your phone #: ")

# length = len(name)
# index = name.find(" ")
# name = name.capitalize()
# name = name.upper()
# name = name.lower()
# result = name.isdigit()
# result = name.isalpha()
# result = phone_number.count(" ")
# phone_number = phone_number.replace("-", "")

def sum(a = 0, b = 0):
    return a + b

print(f"sum = {sum(1, 2)}")

# Trên thực tế, không phải lúc nào chúng ta cũng biết được chính xác số lượng biến truyền vào trong hàm. 
# Chính vì thế trong Python có cũng cấp cho chúng ta khai báo một param đại diện cho các biến truyền
# vào hàm bằng cách thêm dấu * vào trước param đó.
def get_sum(*num):
    tmp = 0
    # duyet cac tham so
    for i in num:
        tmp += i
    return tmp

result = get_sum(1, 2, 3, 4, 5, 6)

print(result)