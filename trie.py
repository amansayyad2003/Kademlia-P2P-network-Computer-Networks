import random

'''hex_values = [
    "bec2f5b914de9d0d43e32f1bee18d502791be0e4",
    "d264d67ead367e2418f8904da6b4a26f020ae6a9",
    "90b0095bda5e8bb132924c0b557046fb8459e2c8",
    "8694667eadda24cf239530aecc8497150cd83f56",
    "04f1a5845882c9f375e6da3cb39004092e15f6b3",
    "2e7d2fb88c4b848a299c9d410392cacedd524672",
    "e5e8e5966a4c1d0341809bf931095151d7e02a10",
    "6c673336348294c4ef92bc04d043dcbf65d203ff",
    "d7b865fcd779a58a9ebf453cde5d52c0fdf20e38",
    "85bd785675f4080474c98a70c352b627bd254281",
    "e39e6f508d7241f9f471291225c67433031da723",
    "7e9dbc901dfdc50fb20cbb8415900cab50b2c732",
    "2e2d09da29d71bc064a830501f4dee2ad03f7bf7",
    "3e87471237ba111c9df853cfef8e546050673385",
    "62b975ada3a9c706a5df2141e06ce9537a7f0977",
    "bce632bc5482fbab4b6d6d5ad6c71a930024c581",
    "0ec2b859549bd07e336538f31ca323e47ac56f36",
    "0a8c8e11b4cd7e342fc200b70ff9290e42ae1e45",
    "5c9c71ed8293b27a38424598abc3de6b54a2f017",
    "3b8699f4872336afbd469cde3f76a7da6adf9df9",
    "1783dc95e142a61ad86f39de2e6fd38a7891642d",
    "9f6b9f28360abc5d1788ddec8fb3c30c7ed278d7",
    "3c38725b5846b6441b87ee6645953afd5691efdc",
    "9531b3a125fc768500873b009da3f332a2f9213f",
    "abe7273179d222b747ec5237b43dbcf41c03fa8f",
    "fc518b21f8748dd6e5fd50dbce7f12f0f53fee9f",
    "0a8f6df34f6d95215eaee33c09a8d7e1b039afdf",
    "b81c3ec8b27a147c89e7834f39f4468379277144",
    "96eafee80104fe3fcab1b8691b3d7ddfc0e0ff01",
    "8a78ad39304a86d31e9f7db1b9f91b1aa9cd6fef",
    "12df8baca9dd5c9cef8f529329af927c355d6535",
    "3be844b20d26bd07a4f52d6cf2c2c82b8553590a",
    "d53a5f19511b950a9b8022e6d5415669f5bba967",
    "595a33153d40f075c83fe080a8ff1766f5e1bd42",
    "22eea1574fd98cb0c2864180d9e08240e537f5c6",
    "5d1567a0a50abb06ef9df7e1de3b7161dc0af329",
    "7d696b72792450983503d8688a88ced7b2fbb741",
    "e2c25dfc8aa7f6c4777ae6e3133a265341a636c4",
    "ceaf4a60c99b3485ec8e18e7cdf5c6186a71b1b9",
    "3c46b41511121400421c13a022d85e75b5c49a57",
    "6074248a4b97f4e31e0da83ec7568d36c410b1b2",
    "3f8f251a10f4b96efedc533e1a1db66e35215380",
    "6731d224162091e6afc8693a5ae37ff284341990",
    "0e8bb3859ff1ee1a874a1beaaa4ed2ef252f0841",
    "1195c360977b0e9ad0990cf73703d0ffc4ee4602",
    "39b9517eb8fe33a592ee40a5aab85e7ce1325a2e",
    "54189508b93ede3bdb9cdf5364854ac8bf8c1ad0",
    "f0f267546a266453ca936d0d50e1118b2c182680",
    "56668c669713d924ea36c2ef893f8b9d0143ccd3"
]


info_dict = {}
ip_address = "127.0.0.1"
port = 9000
formatted_values = [[ip_address, port, hex_value] for hex_value in hex_values] '''


class TrieNode:
    def __init__(self):
        self.children = [None]*2
        self.isEndOfWord = False
    
class Trie:
    def __init__(self):
        self.root = self.get_node()

    def get_node(self):
        return TrieNode()

    def get_index(self, index):
        if index == '0':
            return 0
        else:
            return 1

    def insert(self, peer_id):
        root_node = self.root
        length = len(peer_id)
        for i in range(length):
            index = peer_id[i]
            if not root_node.children[self.get_index(index)]:
                root_node.children[self.get_index(index)] = self.get_node()
            root_node = root_node.children[self.get_index(index)]
        root_node.isEndOfWord = True

    def search(self, peer_id):
        root_node = self.root
        length = len(peer_id)
        for i in range(length):
            index = peer_id[i]
            if not root_node.children[self.get_index(index)]:
                return False
            root_node = root_node.children[self.get_index(index)]
        return root_node.isEndOfWord


    def compliment_index(self, index):
        if index:
            return 0
        return 1

    def get_node_id(self, index, root2):
        if not root2:
            print("!")
            return "NULL"
        root1 = root2
        index = self.compliment_index(index)
        id_rem = str(index) 
        count = 0
        #root1 = root1.children[index]
        if not root1:
            print("@")
            return "NULL"
        while not root1.isEndOfWord:
            while True:
                ind = random.randint(0, 1)
                if root1.children[ind] and not root1.isEndOfWord:
                    id_rem += str(ind)
                    break
                if count >= 100:      # TODO: Think once again about it
                    print("$")
                    id_rem = "NULL" 
                    return id_rem
                count = count + 1
            root1 = root1.children[ind]
            count = 0
        return id_rem

    def get_bucket_node(self, peer_id):
        mylist = []
        root_node = self.root
        # print(peer_id)
        length = len(peer_id)
        id_no = ""
        id_no1 = ""
        id_no2 = ""
        # print(length)
        for i in range(length):
            # print(i)
            index = peer_id[i]
            id_no2 = self.get_node_id(self.get_index(index), root_node) 
            print("id_no: " + id_no2)
            if id_no2 == "NULL":
                mylist.insert(len(mylist), None)
                continue
                # return mylist
            id_no1 += id_no2
            mylist.insert(len(mylist), id_no1)
            id_no += index
            id_no1 = id_no
            # print(id_no1)
            if not root_node or root_node.isEndOfWord:
                mylist.insert(len(mylist), None)
                continue
                # return mylist
            root_node = root_node.children[self.get_index(index)]

        return mylist


'''info_peer = {"00001": ["192.168.0.1", 9000], "00010": ["192.168.0.2", 9001]} '''

if __name__ == '__main__':
    t = Trie()
    t.insert("000")
    t.insert("001")
    t.insert("010")
    # t.insert("011")
    t.insert("100")
    t.insert("101")
    t.insert("110")
    t.insert("111")
    string = t.get_bucket_node("011")
    # x = info_peer[st]
    # x.append(st)
    # print(string)
    ''' if t.search("0110"):
        print("YEs")
    else:
        print("No") '''
