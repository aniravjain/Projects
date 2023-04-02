"""
A HashTable represented as a list of lists with open hashing.
Each bucket is a list of (key,value) tuples
"""

class HashTable:
    def __init__(self, nbuckets):
        """Init with a list of nbuckets lists"""
        self.buckets = [[] for i in range (0,nbuckets)]


    def __len__(self):
        """
        number of keys in the hashable
        """
        total = 0
        for k in self.buckets:
            for j in k:
                total+=1
        return total



    def __setitem__(self, key, value):
        """
        Perform the equivalent of table[key] = value
        Find the appropriate bucket indicated by key and then append (key,value)
        to that bucket if the (key,value) pair doesn't exist yet in that bucket.
        If the bucket for key already has a (key,value) pair with that key,
        then replace the tuple with the new (key,value).
        Make sure that you are only adding (key,value) associations to the buckets.
        The type(value) can be anything. Could be a set, list, number, string, anything!
        """
        h = hash(key) % len(self.buckets)
        if self.bucket_indexof(key)==None:
            self.buckets[h].append((key,value))
        else:
            keyOfBucket = self.bucket_indexof(key)
            if isinstance(self.buckets[h][keyOfBucket][1],set) == True:
                self.buckets[h][keyOfBucket][1].update(value)
            else:
                self.buckets[h][keyOfBucket] = (key,value)
            
            
 


    def __getitem__(self, key):
        """
        Return the equivalent of table[key].
        Find the appropriate bucket indicated by the key and look for the
        association with the key. Return the value (not the key and not
        the association!). Return None if key not found.
        """
        h = hash(key) % len(self.buckets)
        keyOfBucket=self.bucket_indexof(key)
        if keyOfBucket is not None:

            return self.buckets[h][keyOfBucket][1]

        else:
            return None



    def __contains__(self, key):
        """
        check if a certain key is in the hashtable

        """
        for i in self.buckets:
            for j in i:
                if j[0] == key:
                    return True
        return False
        


    def __iter__(self):
        """
        iterate over all keys in the hashtable

        """
        l = self.keys()
        return iter(l)


    def keys(self):
        """
        return all keys in the hashtable
        

        """
        l = []
        for i in self.buckets:
            for j in i:
                l.append(j[0])
        return l



    def items(self):
        """
        returns all values in the hashable

        """
        l = []
        for i in self.buckets:
            for j in i:
                l.append(j)
        return l



    def __repr__(self):
        """
        Return a string representing the various buckets of this table.
        The output looks like:
            0000->
            0001->
            0002->
            0003->parrt:99
            0004->
        where parrt:99 indicates an association of (parrt,99) in bucket 3.
        """
        full=''
        for p in range(len(self.buckets)):
            s=''
            b=f'{p:04}->'
            if len(self.buckets[p])>0:
                for q in self.buckets[p]:
                    if(len(s)==0):
                        s=b+f'{q[0]}:{q[1]}'
                    else:
                        s=s+f', {q[0]}:{q[1]}'
                s=s+'\n'
            else:
                s=b+'\n'
            full=full+s
        return full 



    def __str__(self):
        """
        Return what str(table) would return for a regular Python dict
        such as {parrt:99}. The order should be in bucket order and then
        insertion order within each bucket. The insertion order is
        guaranteed when you append to the buckets in htable_put().
        """
        str1=''
        list2=[]

        for i in range(len(self.buckets)):
            for j, d in enumerate(self.buckets[i]):
                list2.append(f"{d[0]}:{d[1]}")

        return '{'+", ".join(list2)+'}'



    def bucket_indexof(self, key):
        """
        You don't have to implement this, but I found it to be a handy function.

        Return the index of the element within a specific bucket; the bucket is:
        table[hashcode(key) % len(table)]. You have to linearly
        search the bucket to find the tuple containing key.
        """
        h = hash(key) % len(self.buckets)
        for i in range(len(self.buckets[h])):
            if self.buckets[h][i][0]==key:
                return i
        return None
