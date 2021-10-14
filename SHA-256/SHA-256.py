def b2Tob16(value):
  #takes list of 32 bits
  #convert to string
  value = ''.join([str(x) for x in value])
  #creat 4 bit chunks, and add bin-indicator
  binaries = []
  for d in range(0, len(value), 4):
    binaries.append('0b' + value[d:d+4])
  #transform to hexadecimal and remove hex-indicator
  hexes = ''
  for b in binaries:
    hexes += hex(int(b ,2))[2:]
  return hexes
def fill(bits, length):
    for j in range(length-len(bits)):
        bits = ["0"]+bits
    return bits

def char2bit(string):
    """returns list of lists of 8-bit code for input string"""
    bits = []
    for char in string:
        bits = bits + fill(list((bin(ord(char))[2:])),8)
    return bits
def pad(bits):
    """pad with zeros to (multiple of 512)-64"""
    multiplier=(len(bits)+64)//512+1
    pad_length = multiplier*512 -64
    bits = bits + list((pad_length-len(bits))*"0")
    return bits
def bit2hex(bit):
    """outputs hex representation of given bit sequence"""
    return hex(int("".join(bit)))
def prime_numbers(n):
    primes=[]
    number=2
    while len(primes)<n:
        divisor_found=False
        for divisor in range(2, number):
            divisor_found = number%divisor==0
            if divisor_found == True:
                break
        if divisor_found==False:
            primes.append(number)
        number+=1
    return primes
def initialize_constants(primes, root_dim, length, base="hex"):
    constants=[]
    for prime in primes:
        root = prime**(1/root_dim)
        fraction = root - int(root)
        if base == "hex":
            constants.append(hex(int(fraction*2**length)))
        else:
            constants.append(list(bin(int(fraction*2**length))[2:]))

    if base != "hex":
        for i in range(len(constants)):
            for j in range(32-len(constants[i])):
                constants[i]=["0"]+constants[i]

    return constants
def chunker(bits, n):
    chunks=[]
    for i in range(n,len(bits)+1,n):
        chunks.append(bits[i-n:i])
    return chunks
def xor(bit1, bit2):
    bit1,bit2 = align_length(bit1,bit2)
    bits = []
    for i in range(len(bit1)):
        if bit1[i]!=bit2[i]:
            bits.append("1")
        else:
            bits.append("0")
    return bits
def _and(bit1, bit2):
    bit1,bit2 = align_length(bit1,bit2)
    bits = []
    for i in range(len(bit1)):
        if bit1[i]== bit2[i] == "1":
            bits.append("1")
        else:
            bits.append("0")
    return bits
def _not(bit):
    bits = []
    for i in range(len(bit)):
        if bit[i]== "1":
            bits.append("0")
        else:
            bits.append("1")
    return bits
def rotate_right(bits, n):
    """rotate right by n values"""
    for step in range(n):
        bits = [bits[-1]]+bits[:-1]
    return bits
def shift_right(bits, n):
    """shift right by n values (fill with zeros)"""
    for step in range(n):
        bits = ["0"]+bits[:-1]
    return bits
def majority(bit1,bit2,bit3):
    sum = int(bit1)+int(bit2)+int(bit3)
    if sum >= 2:
        return "1"
    else:
        return "0"
def add(value_list):
    """bitwise mod32 addition"""
    value = 0
    for element in value_list:
        element = "".join(element)
        value += int(element, 2)
    mod32 = 2 ** 32
    result = list(str(format(value % mod32, "032b")))
    return result
def align_length(bit1,bit2):
    max_len = max(len(bit1),len(bit2))
    for j in range(max_len-len(bit1)):
        bit1 = ["0"]+bit1
    for j in range(max_len-len(bit2)):
        bit2 = ["0"]+bit2
    return bit1, bit2
def preprocess_message(string):
    #1. Preprocess
    #1.1 convert to binary
    bits = char2bit(string)
    message_length = fill(list(bin(len(bits)))[2:],8) #needed later
    #1.2 append a single one
    bits = bits+["1"]
    #1.3 pad with zeros to (multiple of 512) - 64
    bits = pad(bits)
    #1.4 add 64 bits with length of initial message
    message_length = list((64-len(message_length))*"0") + message_length
    bits = bits + message_length
    return bits
def sha256(string):
    bits = preprocess_message(string)
    #initialize constants
    h_constants = initialize_constants(prime_numbers(8), root_dim=2, length=32, base="bin")
    k_constants = initialize_constants(prime_numbers(64), root_dim=3, length=32, base="bin")
    chunks= chunker(bits, 512)
    for message in chunks:
        #5.Create message schedule
        #5.1 split in chunks of 32 bits
        words = chunker(message, 32)
        #5.2 add 48 words initialized to zero
        for i in range(48):
            words.append(list("0"*32))
        #5.3 modify zero indices
        for i in range(16,64):
            s0=xor(rotate_right(words[i-15],7), xor(rotate_right(words[i-15],18), shift_right(words[i-15],3)))
            s1=xor(rotate_right(words[i-2],17), xor(rotate_right(words[i-2],19), shift_right(words[i-2],10)))
            words[i] = add([words[i-16],s0,words[i-7],s1])

        #6.1 initialize a b c d e f g
        a = h_constants[0]
        b = h_constants[1]
        c = h_constants[2]
        d = h_constants[3]
        e = h_constants[4]
        f = h_constants[5]
        g = h_constants[6]
        h = h_constants[7]
        #6.2 compression loop
        for i in range(0,64):
            s1 = xor(rotate_right(e,6), xor(rotate_right(e,11),rotate_right(e,25)))
            ch = xor(_and(e,f),_and(_not(e),g))
            temp1 = add([h,s1,ch,k_constants[i],words[i]])
            s0 = xor(rotate_right(a,2), xor(rotate_right(a,13), rotate_right(a,22)))
            maj = xor(_and(a,b),xor(_and(a,c),_and(b,c)))
            temp2 = add([s0, maj])
            h = g
            g = f
            f=e
            e=add([d,temp1])
            d=c
            c=b
            b=a
            a= add([temp1,temp2])
        h_constants[0] = add([h_constants[0],a])
        h_constants[1] = add([h_constants[1],b])
        h_constants[2] = add([h_constants[2],c])
        h_constants[3] = add([h_constants[3],d])
        h_constants[4] = add([h_constants[4],e])
        h_constants[5] = add([h_constants[5],f])
        h_constants[6] = add([h_constants[6],g])
        h_constants[7] = add([h_constants[7],h])

    hash_value = ''
    for constant in h_constants:
        hash_value += b2Tob16(constant)
    return hash_value

def test_sha256():
    test_values = {"hello world":"b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
                   "abc":"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
                   "1234567":"8bb0cf6eb9b17d0f7d22b456f121257dc1254e1f01665370476383ea776df414",
                   "abcdefghijklmnopqrstuvwxyz":"71c480df93d6ae2f1efad1447c66c9525e316218cf51fc8d9ed832f2daf18b73",
                   "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz":
                   "941ac378682e3dc66275dd49d5fb09978754ecf4231d18d30326fa51962648ec"}
    for word in test_values.keys():
        print("Test word: ", word, " Bit length: ", len(char2bit(word)), "Test passed: ", sha256(word)==test_values[word])

test_sha256()

string = "hello world"
hash_value = sha256(string)
print("Hash value for ", string, ": ", hash_value)



