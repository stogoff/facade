### from https://bitbucket.org/kent37/python-tutor-samples/
####src/f657aeba5328/BinPacking.py

''' Partition a list into sublists whose sums don't exceed a maximum
    using a First Fit Decreasing algorithm. See
    http://www.ams.org/new-in-math/cover/bins1.html
    for a simple description of the method.
'''


class Bin(object):
    ''' Container for items that keeps a running sum '''
    def __init__(self):
        self.items = []
        self.sum = 0

    def append(self, item):
        self.items.append(item)
        self.sum += item

    def __str__(self):
        ''' Printable representation '''
        return 'Bin(sum=%d, items=%s)' % (self.sum, str(self.items))


def pack(values, maxValue):
    values = sorted(values, reverse=True)
    bins = []

    for item in values:
        # Try to fit item into a bin
        for bin in bins:
            if bin.sum + item <= maxValue:
                #print 'Adding', item, 'to', bin
                bin.append(item)
                break
        else:
            # item didn't fit into any bin, start a new bin
            #print 'Making new bin for', item
            bin = Bin()
            bin.append(item)
            bins.append(bin)

    return bins


if __name__ == '__main__':


    def packAndShow(aList, maxValue):
        ''' Pack a list into bins and show the result '''
        print ('List with sum', sum(aList), 'requires at least', (sum(aList)+maxValue-1)/maxValue, 'bins')

        bins = pack(aList, maxValue)

        print ('Solution using', len(bins), 'bins:')
        for bin in bins:
            print (bin)

        print ()


    aList = [1200,1200,1200,900,900,900,900,600,1200,1200,1200,600]
    packAndShow(aList, 6000)

    aList = 13*[6600,3300]
    packAndShow(aList, 6800)

    aList = [5, 4, 4, 3, 2, 2]
    packAndShow(aList, 10)
