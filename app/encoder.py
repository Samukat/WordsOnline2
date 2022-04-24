def encode(ToCode):
    rm = ToCode%26
    tt = ToCode//26
    def toCode(num, base):
        if num//26 > 0:
            return toCode(num//26, 65) + toCode(num%26, 65)
        else:
            return chr(base + num)
    return toCode(tt,65) + toCode(rm,97)

def decode(ToDecode):
    code = [ord(item) for item in ToDecode][::-1]

    num = 0
    for i in range(len(code)):
        if code[i] >= 97:
            num += code[i] - 97
        elif code[i] >= 65:
            num += (code[i] - 65) * (26**i)
    return num

def optional(**kwargs):
    g = kwargs.get('g', None)
    if g:
        print(g)
    else:
        print("a")

if __name__ == "__main__":
    b = 133
    print(encode(b))
    print(decode(encode(b)))
    optional()
