import random
import statistics
from random import shuffle

from MonteCarlo import MonteCarlo
from pprint import pprint

PERCENT_CORRECT = .8
NUMBER_OF_DOCS = 20

def main():
    all_docs = get_docs(NUMBER_OF_DOCS)
    monte_carlo = MonteCarlo(all_docs, p=.9, N=100, epsilon=.1)
    comparison_counter = 0
    try:
        print(f'Comparisons: {comparison_counter}', end='\r')
        while not monte_carlo.all_same:
            pair = monte_carlo.next_pair()

            if PERCENT_CORRECT > random.random():
                if pair[0] > pair[1]:
                    monte_carlo.compare(pair, True)
                else:
                    monte_carlo.compare(pair, False)
            else:
                if pair[0] > pair[1]:
                    monte_carlo.compare(pair, False)
                else:
                    monte_carlo.compare(pair, True)
            comparison_counter += 1
            print(f'Comparisons: {comparison_counter}', end='\r')
            # pprint(pair)
            # print(monte_carlo.N_array)
    except KeyboardInterrupt:
        print(monte_carlo.get_sorted())
        exit()
    sorted_list = monte_carlo.get_sorted()

    distances = []
    for i in range(0, NUMBER_OF_DOCS):
        all_docs = monte_carlo.get_sorted()
        try:
            distances.append(abs((i) - all_docs[i]))
        except IndexError:
            print(f'i={i}')

    print(monte_carlo.get_sorted())
    print(f'Number of docs: {NUMBER_OF_DOCS}\n'
          f'Comparisons: {comparison_counter}\n'
          f'Average error: {statistics.mean(distances)}\n'
          f'SD of errors: {statistics.stdev(distances)}\n'
          f'Max error: {max(distances)}')


def _get_mean_error(all_docs):
    distances = []
    for i in range(0, NUMBER_OF_DOCS - 1):
        distances.append(abs(i - all_docs[i]))
    # print(f'max difference: {max(distances)}\n')
    # print(all_docs)
    return statistics.mean(distances)

def get_docs(number_of_docs):
    all_docs = list(range(number_of_docs))
    shuffle(all_docs)
    return all_docs


if __name__ == '__main__':
    main()
