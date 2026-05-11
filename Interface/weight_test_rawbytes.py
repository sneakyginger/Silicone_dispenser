def readNextByte(bit_formant, PD_SCK, DOUT):
    byteValue = 0

    # Read bits and build the byte from top, or bottom, depending
    # on whether we are in MSB or LSB bit mode.
    for x in range(8):
        if bit_formant == 'MSB':
            byteValue <<= 1
            byteValue |= readNextBit(PD_SCK, DOUT)
        else:
            byteValue >>= 1              
            byteValue |= readNextBit(PD_SCK, DOUT) * 0x80

    # Return the packed byte.
    return byteValue 

def readNextBit(PD_SCK, DOUT):
    # Clock HX711 Digital Serial Clock (PD_SCK).  DOUT will be
    # ready 1us after PD_SCK rising edge, so we sample after
    # lowering PD_SCL, when we know DOUT will be stable.
    GPIO.output(PD_SCK, True)
    GPIO.output(PD_SCK, False)
    time.sleep(0.000001)
    value = GPIO.input(DOUT)

    # Convert Boolean to int and return it.
    return int(value)

def __main__():
    import time
    PD_SCK, DOUT = 29, 31
    GPIO.setmode(GPIO.BOARD)
    while True:
        print(readNextByte('MSB', PD_SCK, DOUT))