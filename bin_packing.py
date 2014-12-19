# from https://bitbucket.org/kent37/python-tutor-samples/
# src/f657aeba5328/bin_packing.py

""" Partition a list into sublists whose sums don't exceed a maximum
    using a First Fit Decreasing algorithm. See
    http://www.ams.org/new-in-math/cover/bins1.html
    for a simple description of the method.
"""


class Bin(object):
    """ Container for items that keeps a running sum """

    def __init__(self):
        self.items = []
        self.sum = 0.0

    def append(self, item):
        self.items.append(item)
        self.sum += item

    def __str__(self):
        """ Printable representation """
        return 'Bin(sum=%s, items=%s)' % (self.sum, str(self.items))


def pack(values, maxvalue):
    values = sorted(values, reverse=True)
    bins = []

    for item in values:
        # Try to fit item into a bin
        for p_bin in bins:
            if p_bin.sum + item <= maxvalue:
                # print 'Adding', item, 'to', bin
                p_bin.append(item)
                break
        else:
            # item didn't fit into any bin, start a new bin
            # print 'Making new bin for', item
            p_bin = Bin()
            p_bin.append(item)
            bins.append(p_bin)

    return bins


if __name__ == '__main__':

    def pack_and_show(a_list, maxvalue):
        """ Pack a list into bins and show the result """
        print('List with sum', sum(a_list), 'requires at least',
              (sum(a_list) + maxvalue - 1) / maxvalue, 'bins')

        bins = pack(a_list, maxvalue)
        print('Solution using', len(bins), 'bins:')
        for p_bin in bins:
            print(p_bin)

        print()

    aList = 9 * [1200, 1200, 1200, 900, 900, 900, 900, 600, 1200, 1200, 1200, 600]
    pack_and_show(aList, 6000)

    # aList = 13*[6600,3300]
    # packAndShow(aList, 6800)

    # aList = [5.1, 4.2, 4, 3, 2, 2]
    # packAndShow(aList, 10)
