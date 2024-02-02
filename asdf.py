def is_staircase(nums):
    col_length = 0
    staircase = []

    while len(nums) > 0:
        col_length = col_length + 1
        column = []

        for i in range(0, col_length):
            column.append(nums.pop(0))

            if (len(nums) == 0):
                if i < col_length - 1:
                    return False
                return staircase
        staircase.append(column)

f = open('input.txt')
dictionary = {}
num_lines = 0
for line in f.read().split('\n'):
    qwe = line.split(' ')
    # print(qwe)
    dictionary[qwe[0]] = qwe[1]
    num_lines = num_lines + 1

print(dictionary)

asdf = is_staircase(list(range(1, num_lines+1)))
print(asdf)

message = []
for line in asdf:
    message.append(dictionary[str(line[-1])])

print(" ".join(message))