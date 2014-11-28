#! /usr/bin/python
import heapq

def min_bins(bin_size, sizes, counts):
    available = zip(sizes, counts)
    available.sort(reverse=True)
    seen = set([])
    upcoming = [(0, available, [])]
    while 0 < len(upcoming):
        (n, available, bins) = heapq.heappop(upcoming)
        for (bin, left) in bin_packing_and_left(bin_size, available):
            new_bins = bins + [bin]
            if 0 == len(left):
                return new_bins
            elif left not in seen:
                heapq.heappush(upcoming, (n+1, left, new_bins))
                seen.add(left)

def bin_packing_and_left(bin_size, available, top=True):
    if 0 == len(available):
        yield ((), ())
    else:
        (size, count) = available[0]
        available = available[1:]
        for (bin, left, used) in bin_packing_and_left_size(bin_size, available):
            can_use = (bin_size - used) / size
            if count <= can_use:
                yield(((size, count),) + bin, left)
            elif 0 < can_use:
                yield(((size, can_use),) + bin,
                      ((size, count - can_use),) + left)
            else:
                yield(bin, ((size, count),) + left)

def bin_packing_and_left_size(bin_size, available):
    if 0 == len(available):
        yield ((), (), 0)
    else:
        (size, count) = available[0]
        available = available[1:]
        for (bin, left, used) in bin_packing_and_left_size(bin_size, available):
            for i in range(1 + min(count, (bin_size - used) / size)):
                if count == i:
                    yield(((size, count),) + bin, left, used + size * count)
                elif 0 < i:
                    yield(((size, i),) + bin,
                          ((size, count - i),) + left,
                          used + size * i)
                else:
                    yield(bin, ((size, count),) + left, used)

answer = min_bins(23, (2, 3, 5), (20, 30, 40))
print (len(answer))
print (answer)
