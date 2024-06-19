# Initialize variables to store total sum and number of rows
total_sum = 0
num_rows = 0
num_true_true = 0
num_true_true_stags = 0

num_true_false = 0
num_true_false_stags = 0

num_false_true = 0
num_false_true_stags = 0

num_false_false = 0
num_false_false_stags = 0

# Open the file for reading
with open('format', 'r') as file:
    # Iterate over each line in the file
    for line in file:
        # Strip any leading/trailing whitespace and split the line into a list of integers
        integers = [int(num) for num in line.strip().split(',')]
        others_visible = integers[1]
        chat_visible = integers[2]
        num_rows += 1
        
        # true true
        if others_visible and chat_visible:
            num_true_true += 1
            num_true_true_stags += sum(integers[3:])

        # true false
        if others_visible and not chat_visible:
            num_true_false += 1
            num_true_false_stags += sum(integers[3:])

        # false true
        if not others_visible and chat_visible:
            num_false_true += 1
            num_false_true_stags += sum(integers[3:])

        # false false
        if not others_visible and not chat_visible:
            num_false_false += 1
            num_false_false_stags += sum(integers[3:])


#How many in each condition
print("True True: " + str(num_true_true))
print("True False: " + str(num_true_false))
print("False True: " + str(num_false_true))
print("False False: " + str(num_false_false))

# Calculate the median for each condition
print("Median True True: " + str(num_true_true_stags / num_true_true))
print("Median True False: " + str(num_true_false_stags / num_true_false))
print("Median False True: " + str(num_false_true_stags / num_false_true))
print("Median False False: " + str(num_false_false_stags / num_false_false))