########################################################################
'''
python word_counter.py directory/path/to/the/txt/file.txt

To run from python console:
Just simply follow the program's instructions.

The script produces a file of counted items with the file name you
request, in the same directory you're running it.
'''
########################################################################

from collections import Counter
import sys




def read_file(file_name):
    lst = []
    with open(file_name) as file:
        for itm in file.readlines():
            lst.append(str(itm).strip())
    return lst

def count_(lst):
    counted = Counter(lst)
    print('---counting----')
    with open('words_to_count_input.txt', 'w') as file:
        for key, value in counted.items():
            line = "'"+key+"'" + ':' + str(value)
            #print(line)
            file.writelines(line+'\n')
            print(line)
            #print('--writing to file---')
    print('--Process Completed--')

def main():
    lst = read_file('counted_words_output.txt')
    count_(lst)

if __name__ == '__main__':
    main()