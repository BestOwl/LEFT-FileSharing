numbers_string = input('Please input a string: ')

length = 0
pos = 0
pos_num = -1
num_str = ''
containDec = False

number_list = []
location_list = []

for c in numbers_string:
    if '0' <= c <= '9' or c == '.':
        if length == 0:
            pos_num = pos

        if c == '.':
            containDec = True

        num_str += c
        length += 1
    else:
        if length > 0:
            # print(num_str)
            if containDec:
                number_list.append(float(num_str))
            else:
                number_list.append(int(num_str))

            location_list.append([pos_num, length])

            num_str = ''
            length = 0
            containDec = False

    pos += 1


# print(number_list)
# print(location_list)

sorted_location_list = [l for n, l in sorted(zip(number_list, location_list))]
sorted_number_list = sorted(number_list)

print(f'number_list={sorted_number_list}')
print(f'location_list={sorted_location_list}')