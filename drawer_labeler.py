#!/usr/bin/env python

import os
import svgwrite
import sys
import subprocess

class Drawer:
    def __init__(self, organizer, key, front_lines, bottom_lines=[]):
	# Check argment types:
	assert isinstance(organizer, Organizer)
	assert isinstance(key, str)
	assert isinstance(front_lines, list)
	assert isinstance(bottom_lines, list)

	# Load up *self*:
	self._organizer = organizer
	self._key = key
	self._front_lines = front_lines
	self._bottom_lines = bottom_lines

class Organizer:
    def __init__(self, name, length, width, height,
      font_height, front_rows, labels_per_page):
	""" *Organizer*: Initialize. """

	# Check argument types:
	assert isinstance(name, str)
	assert isinstance(length, float)
	assert isinstance(width, float)
	assert isinstance(height, float)
	assert isinstance(font_height, float)
	assert isinstance(front_rows, int)
	assert isinstance(labels_per_page, int)

	# Load up *self*:
	self._name = name
	self._length = length
	self._width = width
	self._height = height
	self._font_height = font_height
	self._front_rows = front_rows
	self._table = {}
	self._labels_per_page = labels_per_page
	self._pending = []
	self._drawing = None
	self._inter_line = (height + font_height) / (front_rows + 1)

    def drawer(self, key, front_labels, bottom_labels=[]):
	""" *Organizer*: Create a new drawer. """
	# Check argument types:
	assert isinstance(key, str)
	assert isinstance(front_labels, list)
	assert isinstance(bottom_labels, list)

	# Create *drawer* and stuff it into *self*:
	drawer = Drawer(self, key, front_labels, bottom_labels)
	self._table[key] = drawer

    def draw(self, key):
	""" *Organizer: Schedule *key* to be drawn. """
	# Check argument types:
	assert isinstance(key, str)

	result = False
	if key in self._table:
	    self._pending.append(key)
	    result = True
	return result

    def done(self):
	""" *Organizer*. Cause all drawing to occur. """

	# Group keys into *labels_per_page* chunks:
	pending = self._pending
	labels_per_page = self._labels_per_page
	key_chunks = []
	size = len(pending)
	for index in range(0, size, labels_per_page):
	    start = index
	    end = index + labels_per_page
	    if end > size:
		end = size
	    #print("start={0} end={1}".format(start, end))
	    key_chunk = pending[start:end]
	    key_chunks.append(key_chunk)
	    #print("key_chunks[{0}:{1}]:{2}".format(start, end, key_chunk))
	#print("key_chunks={0}".format(key_chunks))

	file_names = []
	for file_index in range(len(key_chunks)):
	    key_chunk = key_chunks[file_index]
	    x_size = 8 * 25.4
	    y_size = 10 * 25.4
	    svg_file_name = "{0}{1}.svg".format(self._name, file_index)
	    pdf_file_name = "{0}{1}.pdf".format(self._name, file_index)

	    # Create the SVG *drawing*:
	    drawing = svgwrite.Drawing(svg_file_name,
	      size = ("{0}mm".format(x_size), "{0}mm".format(y_size)),
	      viewBox = "0 0 {0} {1}".format(x_size, y_size), profile="tiny")
	    self._drawing = drawing

	    for drawer_index in range(len(key_chunk)):
		# Draw the outline:
		key = key_chunk[drawer_index]
		drawer = self._table[key]
		assert isinstance(drawer, Drawer)
		
		# Draw the *drawer* at (*x_origin*, *y_origin*):
		x_origin = 3.0
		y_origin = 3.0 + drawer_index * self._width
		self.drawer_draw(drawer, x_origin, y_origin)
		#print("Drawer[{0}]:key={1}".format(drawer_index, drawer._key))

	    # Cause the drawing to be written out:
	    drawing.save()
	    self._drawing = None

	    # Convert to pdf:
	    command = "inkscape -f {0} -A {1}".format(
	      svg_file_name, pdf_file_name)
	    #print("command='{0}'".format(command))
	    try:
		subprocess.check_call(command, shell=True)
	    except subprocess.CalledProcessError as cpe:
		print("Command '{0}' failed".format(command))
            os.remove(svg_file_name)

	    file_names.append(pdf_file_name)

	return file_names

    def line(self, x1, y1, x2, y2):
	""" *Organizer*: Draw a line from (*x1*, *y1) to (*x2*, *y2). """
	# Check argument types:
	assert isinstance(x1, float)
	assert isinstance(y1, float)
	assert isinstance(x2, float)
	assert isinstance(y2, float)

	# Draw the line:
	drawing = self._drawing
	drawing.add(drawing.line((x1, y1), (x2, y2),
	  stroke="black", stroke_width = ".1mm"))

    def text(self, label, x, y):
	""" *Organizer*: Draw *label* at (*x*, *y*): """

	drawing = self._drawing
	drawing.add(drawing.text(label, insert = (x, y),
	  font_family="sans-serif", font_size="1.2mm", fill="black",
	  text_anchor="middle", transform="rotate(-90 {0} {1})".format(x, y)))

    def drawer_draw(self, drawer, x_origin, y_origin):
	""" Drawer: Draw a drawer into *drawing* """
	# Check argument types:
	assert isinstance(drawer, Drawer)
	assert isinstance(x_origin, float)
	assert isinstance(y_origin, float)

	drawing = self._drawing

	x1 = x_origin
	x2 = x1 + self._height
	x3 = x2 + self._length
	y1 = y_origin
	y2 = y1 + self._width/2
	y3 = y2 + self._width/2

        # Draw horizontal lines:
	self.line(x1, y1, x3, y1)
	self.line(x1, y3, x3, y3)

	# Draw vertical lines:
	self.line(x1, y1, x1, y3)
	self.line(x2, y1, x2, y3)
	self.line(x3, y1, x3, y3)

	# Draw the labels:
	font_height = self._font_height
	inter_line = self._inter_line
	line_height = font_height + inter_line

	front_lines = drawer._front_lines
	for line_index in range(len(front_lines)):
	    front_line = front_lines[line_index]
	    self.text(front_line,
	      x1 + (line_index *inter_line) + font_height, y2)

class Organizers:
    def __init__(self):
	""" *Organizers*: Initialize. """
	self._organizers = []

    def organizer_add(self, organizer):
	""" *Organizers*: Add *organizer* to *self* """
	# Check argument types:
	assert isinstance(organizer, Organizer);

	# Add *origanizer* to *self*:
	self._organizers.append(organizer)

    def draw(self, key):
	""" *Organziers*: Cause the drawer named *key* to be drawn. """
	# Check argument types:
	assert isinstance(key, str)

	# Search through *self* looking for a drawer that matches *key:
	result = False
	for organizer in self._organizers:
	    if organizer.draw(key):
		result = True
		break
	return result

    def done(self):
	""" *Organizers*: Force all of the drawings to be generated: """

	file_names = []
	for organizer in self._organizers:
	    file_names += organizer.done()
	return file_names

def main():
    # Create all the drawer labels:
    organizers = Organizers()
    organizers.organizer_add(electronics_organizer())
    organizers.organizer_add(hardware_organizer())

    arguments = sys.argv[1:]
    ok = True
    for drawer_name in arguments:
	if not organizers.draw(drawer_name):
	    print("No drawer named '{0}'".format(drawer_name))
	    ok = False

    if ok:
	file_names = organizers.done()
	if len(file_names) > 1:
	    command = "pdfunite"
	    for file_name in file_names:
		print("Generated file: '{0}'".format(file_name))
		command += " {0}".format(file_name)
	    command += " labels.pdf"
	    #print("command={0}".format(command))
	    try:
		subprocess.check_call(command, shell=True)
	    except subprocess.CalledProcessError as cpe:
		print("Command '{0}' failed".format(command))

	    for file_name in file_names:
		os.remove(file_name)
	else:
	    os.rename(file_names[0], "labels.pdf")

def electronics_organizer():
    o = Organizer(name="Electronics",
      length=116.0, width=49.0, height=12.0,
      font_height=4.0, front_rows=2, labels_per_page=5)

    # Capacitors:
    o.drawer("cceramic10pf50v", ["10 pF 50V", "Ceramic Capacitor"], ["J:15334"])
    o.drawer("cceramic100nf50v", [".1 uF 50V", "Ceramic Capacitor"],
      ["J:25524", "J:25523"])
    o.drawer("cceramic1uf50v", ["1 uf 50V", "Ceramic Capacitor"], ["J:81510"])
    o.drawer("cradial1uf100v", ["1 uF 100V", "Electrolytic Cap."], ["J:158490"])
    o.drawer("cradial10uf16v", ["10 uF 16V", "Electrolytic Cap."], ["J:330691"])
    o.drawer("cradial47uf100v", ["47 uF 100V", "Electrolytic Cap."],
      ["J:607161"])
    o.drawer("cradial220uf16v", ["220 uF 16V", "Electrolytic Cap."],
      ["J:198871"])
    o.drawer("cradial470uf16v", ["Radial 470 uF 16V", "Electrolytic Cap."],
      ["J:158203"])
    o.drawer("cradial470uf25v", ["Radial 470 uF 25V", "Electrolytic Cap."])
    o.drawer("cradial470uf35v", ["Radial 470 uF 35V", "Electrolytic Cap."],
      ["J:93818"])
    o.drawer("cradial470uf50v", ["Radial 470 uF 50V", "Electrolytic Cap."],
      ["J:93825"])
    o.drawer("cradial470uf63v", ["Radial 470 uF 63V", "Electrolytic Cap."],
      ["J:154465"])
    o.drawer("cradial1000uf16v", ["Radial 1000 uF 16V", "Electrolytic Cap."],
      ["J:30016"])
    o.drawer("cradial2200uf6.3v", ["Radial 2200uF 6.3V", "Electrolytic Cap."],
      ["J:608841"])
    o.drawer("cradial2200uf25v", ["Radial 2200uF 25V", "Electrolytic Cap."],
      ["J:30535"])
    o.drawer("ctantalum100nf25v", [".1 uF 25V", "Tantalum Cap."],
      ["J:154861"])
    o.drawer("ctantalum100nf35v", [".1 uF 35V", "Tantalum Cap."],
      ["J:33487", "J:33486"])
    o.drawer("ctantalum330nf35v", [".33 uF 35V", "Tantalum Cap."],
      ["J:33524", "J:545908", "J:33525"])
    o.drawer("ctantalum470nf35v", [".47 uF 35V", "Tantalum Cap."],
      ["J:33532", "J:33531"])
    o.drawer("ctantalum1uf25v", ["1 uF 25V", "Tantalum Cap."],
      ["J:545588", "J:154860"])
    o.drawer("ctantalum1uf35v", ["1 uF 35V", "Tantalum Cap."],
      ["J:33663", "J:545561", "J:545596"])
    o.drawer("ctantalum2.2uf16v", ["2.2 uF 16V", "Tanalum Cap."], ["J:94002"])
    o.drawer("ctantalum2.2uf35v", ["2.2 uF 35V", "Tanalum Cap."], ["J:33734"])
    o.drawer("ctantalum22uf6.3v", ["22 uF 6.3V", "Tantalum Cap."],
      ["J:33752", "J:545836"])
    o.drawer("ctantalum22uf16v", ["22 uF 16V", "Tantalum Cap."],
      ["J:94095", "J:545852"])
    o.drawer("ctantalum22uf25v", ["22 uF 25V", "Tantalum Cap."])
    o.drawer("cmylar1uf100v", ["1 uF 100V", "Mylar Capacitor"], ["J:27001"])

    # Connectors:
    o.drawer("n1x2header", ["1x2 .1 inch", "Headers"],
      ["M:571-6412152", "J:345965", "J:326019"])
    o.drawer("n1x3header", ["1x3 .1 inch", "Headers"],
      ["M:571-641215-3", "J:345973", "J:326027"])
    o.drawer("n1x4header", ["1x4 .1 inch", "Headers"],
      ["M:571-641215-4", "J:345981", "J:326035"])
    o.drawer("n1x5header", ["1x5 .1 inch", "Headers"])
    o.drawer("n1x6header", ["1x6 .1 inch", "Headers"], ["M:571-641215-6"])
    o.drawer("n1x8header", ["1x8 .1 inch", "Headers"])
    o.drawer("n1xNheader", ["1xN .1 inch", "Headers"])
    o.drawer("n1x36header", ["1x36 .1 inch", "Headers"])
    o.drawer("n1x40header", ["1x40 .1 inch", "Headers"])
    o.drawer("n1x40angle", ["1x40 Rt. Angle", "Headers"])
    o.drawer("n2x5header", ["2x5 .1 inch", "Headers"])
    o.drawer("n2x8header", ["2x8 .1 inch", "Headers"])
    o.drawer("n2x10header", ["2x10 .1 inch", "Headers"])
    o.drawer("n2x13header", ["2x13 .1 inch", "Headers"])
    o.drawer("n2x17header", ["2x17 .1 inch", "Headers"])
    o.drawer("n2x20header", ["2x20 .1 inch", "Headers"])
    o.drawer("n2x25header", ["2x25 .1 inch", "Headers"])
    o.drawer("n2x36header", ["2x36 .1 inch", "Headers"])
    o.drawer("n2x40header", ["2x40 .1 inch", "Headers"])
    o.drawer("n2x25cable", ["2x25 .1 inch", "IDC Male Header:"], ["J:29217"])
    o.drawer("n1.25x.25fuseholder", ["1.25 x .25", "Fuse Holder"])
    o.drawer("n6_6femalephonejack", ["6-6 Female", "RJ-11 Phone Jack"])
    o.drawer("n6_4femalephonejack", ["6-4 Female", "RJ-11 Phone Jack"],
      ["M:571-520257-2"])
    o.drawer("n9voltbatteryclip", ["9 Volt", "Battery Clip"])
    o.drawer("ndb9", ["DB9", "Connector"])
    o.drawer("ndb15", ["DB15", "Connector"])
    o.drawer("ndb25", ["DB25", "Connector"])
    o.drawer("ndb37", ["DB37", "Connector"])
    o.drawer("ndeems", ["Deems", "Connector"])
    o.drawer("ndin50", ["DIN50", "Connector"])
    o.drawer("nbananna", ["Banana Plug", "Connectors"])
    o.drawer("ndbxcrimppin", ["DBx", "Crimp Pins"])
    o.drawer("nmolex", ["Molex Pins &", "Connectors"])
    o.drawer("npowerjack", ["2.1mm & 3.1mm", "PCB Power Jacks"])
    o.drawer("nshortingblock", [".1 Inch", "Shorting Block"])
    o.drawer("nphonejack", [".25 Inch HeadPhone", "Jack and Plug"])
    o.drawer("nhousingmalepin", ["Connector Housing", "Male Crimp Pin"])
    o.drawer("nhousingfemalepin", ["Connector Housing", "Female Crimp Pin"])
    o.drawer("nminidin6", ["6-pin Mini-DIN", "Connector"])
    o.drawer("nminidin8", ["8-pin Mini-DIN", "Connector"])
    o.drawer("ndin5", ["5-pin DIN", "Connector"])
    o.drawer("nrj11", ["RJ11", "Connector"])
    o.drawer("nspadelug", ["Spade", "Lug"])
    o.drawer("npowercordmaleplug", ["Male Power", "Cord Plug"])
    o.drawer("nterminalblockvertical", [".2 Inch Vert.", "Terminal Block"])

    # Sockets:
    o.drawer("dip8", ["8-pin", "DIP Socket"])
    o.drawer("dip14", ["14-pin", "DIP Socket"])
    o.drawer("dip16", ["16-pin", "DIP Socket"])
    o.drawer("dip18", ["18-pin", "DIP Socket"])
    o.drawer("dip20", ["20-pin", "DIP Socket"])
    o.drawer("dip22", ["22-pin", "DIP Socket"])
    o.drawer("dip24", ["24-pin", "DIP Socket"])
    o.drawer("dip28", ["28-pin", "DIP Socket"])
    o.drawer("dip32", ["32-pin", "DIP Socket"])
    o.drawer("dip40", ["40-pin", "DIP Socket"])
    o.drawer("zif", ["Zero Insertion", "Force Sockets"])
    o.drawer("zif48", ["48-pin", "ZIF Socket"])
    o.drawer("plcc84", ["84-pin", "PLCC Socket"], ["J:71976"])

    # Chips:
    o.drawer("echip74htc03", ["74HCT03 Quad", "2-Input OC NAND"])
    o.drawer("echip74htc08", ["74HCT08", "Quad 2-Input AND"])
    o.drawer("echip74hct32", ["74HCT32", "Quad 2-Input OR"])

    o.drawer("echip74ls00", ["74LS00", "Quad 2-Input NAND"])
    o.drawer("echip74ls02", ["74LS02", "Quad 2-Input NOR"])
    o.drawer("echip74ls04", ["74LS04", "Hex Inverter"])
    o.drawer("echip74ls05", ["74LS05", "Hex OC Inverter"])
    o.drawer("echip74ls06", ["74LS06", "Hex OC Inverter"])
    o.drawer("echip74ls07", ["74LS07", "Hex OC Buffer"])
    o.drawer("echip74ls08", ["74LS08", "Quad 2-Input AND"])
    o.drawer("echip74ls10", ["74LS10", "Triple 3-In NAND"])
    o.drawer("echip74ls14", ["74LS14", "Hex Schmitt Inv."])
    o.drawer("echip74ls21", ["74LS21", "Dual 4-Input AND"])
    o.drawer("echip74ls30", ["74LS30", "8-Input NAND"])
    o.drawer("echip74ls32", ["74LS32", "Quad 2-Input OR"])
    o.drawer("echip74ls74", ["74LS74", "Dual D Flip-Flop"])
    o.drawer("echip74hct123", ["74HCT123", "Dual One-shot"])
    o.drawer("echip74ls125", ["74LS125 (neg. en.)", "Quad Bus Buffer"])
    o.drawer("echip74ls126", ["74LS126 (pos. en.)", "Quad Bus Buffer"])
    o.drawer("echip74ls138", ["74LS138", "1-of-8 Decoder"])
    o.drawer("echip74hct138", ["74HCT138", "1-of-8 Decoder"])
    o.drawer("echip74ls139", ["74LS139", "Dual 1-of-4 Decode"])
    o.drawer("echip74ls148", ["74LS148 8-to-3", "Priority Encoder"])
    o.drawer("echip74ls151", ["74LS151 8-input", "Multiplexer"])
    o.drawer("echip74ls153", ["74LS153 Dual 4-in", "Multiplexer"])
    o.drawer("echip74ls155", ["74LS155", "Dual 1-of-4 Demux"])
    o.drawer("echip74ls157", ["74LS157", "Quad 2-Input Mux"])
    o.drawer("echip74ls164", ["74LS164", "8-bit S-to-P Reg."])
    o.drawer("echip74ls165", ["74LS165", "8-bit P-to-S Cvt."])
    o.drawer("echip74hc165", ["74HC165", "8-bit P-to-S Cvt."])
    o.drawer("echip74ls175", ["74LS175", "Quad D Flip Flop"])
    o.drawer("echip74ls244", ["74LS244", "Octal Line Driver"])
    o.drawer("echip74ls273", ["74LS273", "Octal D Flip Flop"])
    o.drawer("echip74ls365", ["74LS365", "Hex 3-State Buffer"])
    o.drawer("echip74ls374", ["74LS374", "Octal D Flip-Flop"])
    o.drawer("echip75175", ["75175", "Quad RS-422 Rec."])
    o.drawer("echip75176", ["75176", "RS-422 Tranceiver"])
    o.drawer("echip26ls31", ["26LS31", "Quad RS-422 Rec."])
    o.drawer("echip26ls32", ["26LS32", "Quad RS-422 Driver"])
    o.drawer("echipcd40109", ["CD40109BE", "Quad Volt Shifter"])
    o.drawer("echiplm339", ["LM339 Quad", "O/C Comparator"], ["J:143888"])
    o.drawer("echiptlc3704", ["TLC3704CN", "Quad Comparator"], ["J:280137"])
    o.drawer("echipmcp2551", ["MCP2551-I/P", "CAN Transceiver"],
      ["M:579-MCP2551-I/P"])
    o.drawer("echipds8921an", ["DS8921AN", "RS422 Drv/Rec"], ["J:299671"])
    o.drawer("echipps2501_4", ["PS2501-4", "Quad Optoisolator"], ["J:160338"])
    o.drawer("echipl6210", ["L6210 Schottky", "Diode Bridge"],
      ["DK:497-3646-ND"])
    o.drawer("echiptlc5628", ["TLC5628CN", "Octal SPI D/A"], ["J:289879"])
    o.drawer("echiptlc5620", ["TLC5620CN", "Quad SPI D/A"], ["J:289836"])
    o.drawer("echipmax548a", ["MAX548ACPA", "Dual SPI D/A"],
      ["DK:MAX548ACPA-ND"])
    o.drawer("echiplm567", ["LM567CN", "Tone Decoder"], ["J:24395"])
    o.drawer("echipat24c32", ["AT24C32A", "4Kx8 Ser. EEPROM"], ["J:369449"])
    o.drawer("echip628128", ["628128LP-85", "128Kx8 RAM"], ["J:103982"])
    o.drawer("echipls7366", ["LS7366 Quad.", "Encoder"], ["Gemini Elect."])

    o.drawer("ecrystalosc", ["Crystal", "Oscillator"])
    o.drawer("ecrystalosc20mhz", ["20MHz Crystal", "Oscillator"])
    o.drawer("echipmax232", ["Max232", "RS-232 Converter"])
    o.drawer("ediode1n4001", ["1N4001 1A 50PRV", "Rectifying Diode"])
    o.drawer("ediode1n4002", ["1N4002 1A 100PRV", "Rectifying Diode"])
    o.drawer("ediode1n4004", ["1N4004 1A 200PRV", "Rectifying Diode"])
    o.drawer("ediode1n4148", ["1N4148", "Switching Diode"])
    o.drawer("ediode1n4733", ["1N4733 5.1V 1W", "Zener Diode"])
    o.drawer("ediode1n5400", ["1N5400 3A 50PRV", "Rectifying Diode"])
    o.drawer("ediode1n5819", ["1N5819 1A", "Schottky Diode"])
    o.drawer("ediode1n5822", ["1N5822 3A", "Schottky Diode"])
    o.drawer("eheatsinkto220", ["TO-220", "Heat Sink"])
    o.drawer("eheatsinkmw15", ["Multi-Watt 15", "Heat Sink"])
    o.drawer("efuseclips", ["5x20mm", "PCB Fuse Clips"])
    o.drawer("efuse5by20mm250ma", ["5x20mm 250mA", "Fuse"])
    o.drawer("efuse5by20mm500ma", ["5x20mm 500mA", "Fuse"])
    o.drawer("efuse5by20mm1a", ["5x20mm 1Amp", "Fuse"])
    o.drawer("efuse5by20mm2a", ["5x20mm 2Amp", "Fuse"])
    o.drawer("efuse5by20mm5a", ["5x20mm 5Amp", "Fuse"])
    o.drawer("epicotp", ["Microchip OTP", "PIC Processors"])
    o.drawer("eresettablefuserue090", ["Resettable Fuse", "RUE090 .9A"])
    o.drawer("eresettablefuserue110", ["Resettable Fuse", "RUE110 1.1A"])
    o.drawer("eresonator20mhz", ["20 MHz", "Resonator"], ["M:ZTT2000MX"])
    o.drawer("eresonator16mhz", ["16 MHz", "Resonator"], ["M:ZTT1600MX"])
    o.drawer("eresonator10mhz", ["10 MHz", "Resonator"], ["M:ZTT1000MT"])
    o.drawer("eresonator6mhz", ["6 MHz", "Resonator"], ["M:ZTT600MT"])

    o.drawer("epicuv", ["PIC UV Window", "Microprocessor"])
    o.drawer("epic12c509a", ["PIC12C509A", "Microprocessor"])
    o.drawer("epic12c672", ["PIC12C672", "Microprocessor"])
    o.drawer("epic16c505", ["PIC16C505", "Microprocessor"])
    o.drawer("epic12f675", ["PIC12F675", "Microprocessor"])
    o.drawer("epic16f628", ["PIC16F628", "Microprocessor"])
    o.drawer("epic16f630", ["PIC16F630", "Microprocessor"])
    o.drawer("epic16f648", ["PIC16F648", "Microprocessor"])
    o.drawer("epic16f676", ["PIC16F676", "Microprocessor"])
    o.drawer("epic16f688", ["PIC16F688", "Microprocessor"])
    o.drawer("epic16f767", ["PIC16F767", "Microprocessor"])
    o.drawer("epic16f777", ["PIC16F777", "Microprocessor"])
    o.drawer("epic16f876", ["PIC16F876", "Microprocessor"])
    o.drawer("epic16f877", ["PIC16F877/876A", "Microprocessor"])
    o.drawer("epic16f84", ["PIC16F84", "Microprocessor"])
    o.drawer("epic16f88", ["PIC16F88", "Microprocessor"])
    o.drawer("eatmega168", ["ATMega168", "Microprocessor"],
      ["D:ATMEGA168-20PU"])
    o.drawer("eatmega324p", ["ATMega324P", "Microprocessor"],
      ["D:ATMEGA324P-20PU", "M:ATMEGA324P-20PU"])

    o.drawer("efetfqp47p06", ["FQP47P06", "P-Channel FET"])
    o.drawer("eslotgp1s094hcz", ["GP1S094HCZ0F 3mm", "Slot Interrupter"])

    o.drawer("epotentiometerpcb10k", ["10KOhm", "PCB Potentiometer"])
    o.drawer("evoltageregulatorlm317", ["LM317 Variable", "1.5A Volt. Reg."])
    o.drawer("evoltageregulatorlm317lz",
      ["LM317LZ Variable", "100mA Volt. Reg."])
    o.drawer("esocketdip40", ["40-pin DIP", "Solder Tail Socket"])
    o.drawer("esocketdip14single", ["14-pin DIP", "Single Pins"])
    o.drawer("eswitchdip", ["DIP Switch", ""])
    o.drawer("eswitchdpdt", ["DPDT Switch", "Solder Tail"])
    o.drawer("eswitchspdt", ["SPDT Switch", ""])
    o.drawer("eswitchpcbbutton", ["Push Button", "Solder Tail"])
    o.drawer("eswitchhexrotary", ["Hex Rotary Switch", "6-pin DIP"])
    o.drawer("eswitchmicro", ["SPDT Micro", "Switch"])
    o.drawer("eswitchpower", ["SPST Power", "Switch"])
    o.drawer("etransistortip31a", ["TIP31A NPN 3A", "Power Transistor"])
    o.drawer("etransistortip32a", ["TIP32A PNP 3A", "Power Transistor"])
    o.drawer("etransistortip41a", ["TIP41A NPN 3A", "Power Transistor"])
    o.drawer("etransistortip42a", ["TIP42A PNP 3A", "Power Transistor"])
    o.drawer("etransistortip122", ["TIP122 NPN 3A", "Darlington Trans."])
    o.drawer("etransistorpnp2222", ["PN2222 NPN", "Silicon Transistor"])
    o.drawer("etransistorpnp2907", ["PN2907 PNP", "Silicon Transistor"])
    o.drawer("etransistorpnp3904", ["2N3904 NPN", "Silicon Transistor"])
    o.drawer("etransistorpnp3906", ["2N3906 PNP", "Silicon Transistor"])

    # Linear Stuff:
    o.drawer("l7805t", ["7805T +5V 1.5A", "Volt. Reg TO-220"])
    o.drawer("l78l05t", ["78L05 +5V 100mA", "Volt. Reg TO-220"])
    o.drawer("l7806c", ["7806C +6V 1.5A", "Voltage Regulator"])
    o.drawer("l7815t", ["7815T +15V 1A", "Volt. Reg. TO-220"])
    o.drawer("l7824t", ["7824T +24V 1A", "Volt. Reg. TO-220"])
    o.drawer("ll4931abz25", ["L4931ABZ25 2.5V", "LDO VR TO92"])
    o.drawer("lle33cz-tr", ["LE33CZ-TR 3.3V", "LDO VR TO92"])
    o.drawer("llm1458n", ["LM1458N (RC4558)", "Dual Op Amp"])
    o.drawer("llm317t", ["LM317T 1.5A", "1.2-37V Volt. Reg."])
    o.drawer("llm317lz", ["LM317T 100mA", "1.2-37V Volt. Reg."])
    o.drawer("llm324n", ["LM324N (ULN4336)", "Low Pwr Quad OpAmp"])
    o.drawer("llm336z", ["LM336Z-2.5", "2.5 Volt. Ref."])
    o.drawer("llm348n", ["LM348N (UPC4741C)", "Quad 741 Op Amp"])
    o.drawer("llf353n", ["LF343N (TL082CP)", "Dual BiFET Op Amp"])
    o.drawer("llm358n", ["LM358N", "Low Pwr Dual OpAmp"])
    o.drawer("llm385b725", ["LM385B7-2.5 2.5V", "LDO VR TO92"])
    o.drawer("llm1086ct33", ["LM1086CT-3.3 3.3V", "LDO VR TO220"])
    o.drawer("ltl082cp", ["TL082CP", "JFET Dual Op Amp"])

    o.drawer("lm2950cz30", ["LM2950LCZ-3.0", "3.0V Reg. TO-92"], ["J:266845"])
    o.drawer("lp2950cz33", ["LP2950LCZ-3.3", "3.3V Reg. TO-92"], ["Anchor"])
    o.drawer("lm2931z50", ["LM2931Z-5.0", "5.0V Reg. TO-92"], ["J:121048"])

    o.drawer("llm1117t3_3", ["LM1117T-3.3", "3.3V LDO Reg."])
    o.drawer("llm2940ct", ["LM2940CT 5V", "Low Drop Out Reg."])
    o.drawer("ll293d", ["L293D Push-Pull", "4 Ch. Driver"])
    o.drawer("ll298", ["L298 4Amp", "Dual Full Bridge"])

    # Miscellaneous:
    o.drawer("mdinsmorecompass", ["DIN1490/DIN1655", "Dinsmore Compass"])
    o.drawer("m40tr16f", ["40kHz Ultrasonic", "Transmit/Receive"])
    o.drawer("msmallmotor", ["Small DC", "Motor"])
    o.drawer("mrubberfeet", ["Small", "Rubber Feet"])
    o.drawer("msrf05", ["Devantech SRF04", "Sonar Unit"])
    o.drawer("mledmount", ["LED Mount"], ["J:14277", "J:417851"])
    o.drawer("mpcbspeaker", ["PCB Speaker", ""])
    o.drawer("mhstube", ["Heat Shrink", "Tubing"])
    o.drawer("mpressure", ["Pressure", "Sensor"])
    o.drawer("mavrdragon", ["AVR-Dragon", "Rewire Boards"])

    # Optoelectronics:
    o.drawer("ois471fe", ["IS471FE", "Opto Detector"], ["D:425-2069-5-ND"])
    o.drawer("out0393", ["UT0393-46-0125R", "IR Detector"], ["J:372964"])
    o.drawer("op5587", ["Hamamatsu P5587", "Photo Reflector"])
    o.drawer("oird300", ["IRD300 Infrared", "940nM Detect Diode"])
    o.drawer("oqrb1114", ["QRB1114 IR (tri)", "Photo Sensor"])
    o.drawer("oqrd1114", ["QRD1114 IR (sq)", "Photo Sensor"])
    o.drawer("oledred", ["Red LED"])
    o.drawer("oledyellow", ["Yellow LED"])
    o.drawer("oledgreen", ["Green LED"])
    o.drawer("oled7segment", ["7-Segment LED"])
    o.drawer("oledtricolor", ["Tri-color LED"])
    o.drawer("otsop1840", ["TSOP1840", "40kHz IR Det."])
    o.drawer("ogp1u26x", ["GP1U26X", "40kHz IR Det."])
    o.drawer("ogp2d12", ["GP2D12 IR Optical", "Distance Unit"])
    o.drawer("ogp2d120", ["GP2D120 IR Optical", "Distance Unit"])
    o.drawer("olpt2023", ["LPT2023", "IR Det. Diode"])
    o.drawer("olpt3313", ["LPT3313", "IR Det. Diode"])
    o.drawer("olvir3333", ["LVIR3333", "IR Emit Diode"])
    o.drawer("oledbar10", ["10 Segment", "Bar LED"])
    o.drawer("oirreceiver56k8", ["58.6KHz IR", "Receiver"])
    o.drawer("olcmso01602dtrm", ["LCM-SO01602DTR/M", "16x2 LCD Display"])

    # Resistors:
    o.drawer("r220_.125w", ["220 Ohm 1/8W Res.", "Red Red Brown"])
    o.drawer("r330_.125w", ["330 Ohm 1/4W Res.", "Orange Orange Brn"])
    o.drawer("r470_.125w", ["470 Ohm 1/8W Res.", "Yellow Violet Brn"])

    o.drawer("r1", ["1.0 Ohm Resistor", "Brown Black Gold"])
    o.drawer("r10", ["10 Ohm Resistor", "Brown Black Black"])
    o.drawer("r12", ["12 Ohm Resistor", "Brown Red Black"])
    o.drawer("r15", ["15 Ohm Resistor", "Brown Green Black"])
    o.drawer("r18", ["18 Ohm Resistor", "Brown Gray Black"])
    o.drawer("r22", ["22 Ohm Resistor", "Red Red Black"])
    o.drawer("r27", ["27 Ohm Resistor", "Red Violet Black"])
    o.drawer("r30", ["30 Ohm Resistor", "Orange Black Black"])
    o.drawer("r33", ["33 Ohm Resistor", "Orange Orange Blk"])
    o.drawer("r39", ["39 Ohm Resistor", "Orange White Black"])
    o.drawer("r47", ["47 Ohm Resistor", "Yellow Violet Blk"])
    o.drawer("r56", ["56 Ohm Resistor", "Green Blue Black"])
    o.drawer("r68", ["68 Ohm Resistor", "Blue Gray Black"])
    o.drawer("r75", ["75 Ohm Resistor", "Violet Green Black"])
    o.drawer("r82", ["82 Ohm Resistor", "Gray Red Black"])
    o.drawer("r100", ["100 Ohm Resistor", "Brown Black Brown"])
    o.drawer("r120", ["120 Ohm Resistor", "Brown Red Brown"])
    o.drawer("r150", ["150 Ohm Resistor", "Brown Green Brown"])
    o.drawer("r180", ["180 Ohm Resistor", "Brown Gray Brown"])
    o.drawer("r220", ["220 Ohm Resistor", "Red Red Brown"])
    o.drawer("r270", ["270 Ohm Resistor", "Red Violet Brown"])
    o.drawer("r300", ["300 Ohm Resistor", "Orange Black Brown"])
    o.drawer("r390", ["390 Ohm Resistor", "Orange White Brown"])
    o.drawer("r470", ["470 Ohm Resistor", "Yellow Violet Brn"])
    o.drawer("r560", ["560 Ohm Resistor", "Green Blue Brown"])
    o.drawer("r680", ["680 Ohm Resistor", "Blue Gray Brown"])
    o.drawer("r750", ["750 Ohm Resistor", "Violet Green Brown"])
    o.drawer("r820", ["820 Ohm Resistor", "Gray Red Brown"])
    o.drawer("r1k0", ["1.0k Ohm Resistor", "Brown Black Red"])
    o.drawer("r1k2", ["1.2k Ohm Resistor", "Brown Red Red"])
    o.drawer("r1k5", ["1.5k Ohm Resistor", "Brown Green Red"])
    o.drawer("r1k8", ["1.8k Ohm Resistor", "Brown Gray Red"])
    o.drawer("r2k2", ["2.2k Ohm Resistor", "Red Red Red"])
    o.drawer("r2k7", ["2.7k Ohm Resistor", "Red Violet Red"])
    o.drawer("r3k0", ["3.0k Ohm Resistor", "Orange Black Red"])
    o.drawer("r3k3", ["3.3k Ohm Resistor", "Orange Orange Red"])
    o.drawer("r3k9", ["3.9k Ohm Resistor", "Orange White Red"])
    o.drawer("r4k7", ["4.7k Ohm Resistor", "Yellow Violet Red"])
    o.drawer("r5k6", ["5.6k Ohm Resistor", "Green Blue Red"])
    o.drawer("r6k8", ["6.8k Ohm Resistor", "Blue Gray Red"])
    o.drawer("r7k5", ["7.5k Ohm Resistor", "Violet Green Red"])
    o.drawer("r8k2", ["8.2k Ohm Resistor", "Gray Red Red"])
    o.drawer("r10k", ["10k Ohm Resistor", "Brown Black Orange"])
    o.drawer("r12k", ["12k Ohm Resistor", "Brown Red Orange"])
    o.drawer("r15k", ["15k Ohm Resistor", "Brown Green Orange"])
    o.drawer("r18k", ["18k Ohm Resistor", "Brown Gray Orange"])
    o.drawer("r22k", ["22k Ohm Resistor", "Red Red Orange"])
    o.drawer("r27k", ["27k Ohm Resistor", "Red Violet Orange"])
    o.drawer("r30k", ["30k Ohm Resistor", "Ornge Black Ornge"])
    o.drawer("r33k", ["33k Ohm Resistor", "Ornge Ornge Ornge"])
    o.drawer("r39k", ["39k Ohm Resistor", "Ornge White Ornge"])
    o.drawer("r47k", ["47k Ohm Resistor", "Yel. Violet Ornge"])
    o.drawer("r56k", ["56k Ohm Resistor", "Green Blue Orange"])
    o.drawer("r68k", ["68k Ohm Resistor", "Blue Gray Orange"])
    o.drawer("r75k", ["75k Ohm Resistor", "Violet Green Ornge"])
    o.drawer("r82k", ["82k Ohm Resistor", "Gray Red Orange"])
    o.drawer("r100k", ["100k Ohm Resistor", "Brown Black Yellow"])
    o.drawer("r120k", ["120k Ohm Resistor", "Brown Red Yellow"])
    o.drawer("r150k", ["150k Ohm Resistor", "Brown Green Yellow"])
    o.drawer("r180k", ["180k Ohm Resistor", "Brown Gray Yellow"])
    o.drawer("r220k", ["220k Ohm Resistor", "Red Red Yellow"])
    o.drawer("r270k", ["270k Ohm Resistor", "Red Violet Yellow"])
    o.drawer("r300k", ["300k Ohm Resistor", "Orange Black Yel."])
    o.drawer("r330k", ["330k Ohm Resistor", "Orange Orange Yel."])
    o.drawer("r390k", ["390k Ohm Resistor", "Orange White Yel."])
    o.drawer("r470k", ["470k Ohm Resistor", "Yellow Violet Yel."])
    o.drawer("r560k", ["560k Ohm Resistor", "Green Blue Yellow"])
    o.drawer("r680k", ["680k Ohm Resistor", "Blue Gray Yellow"])
    o.drawer("r750k", ["750k Ohm Resistor", "Violet Green Yel."])
    o.drawer("r820k", ["820k Ohm Resistor", "Gray Red Yellow"])
    o.drawer("r1m+", ["1M 1/4 Res.", "Multiple Values"])
    o.drawer("r1_.5w", ["1.0 Ohm 1/2W Res.", "Brown Black Gold"])
    o.drawer("r.51_2w", [".51 Ohm 2W Res.", " Greem Brn Silver"])

    o.drawer("xr20k", ["20k Ohm Resistor", "Red Black Orange"])
    o.drawer("xr2k0", ["2.0K Ohm Resistor", "Red Black Red"])
    o.drawer("xr200", ["200 1/4W Resistor", "Red Black Brown"])
    o.drawer("xr1k1", ["1.1K 1/4W Resistor", "Brown Brown Red"])
    o.drawer("xr1percent", ["Misc. 1% Res."])
    o.drawer("xrtrimpots", ["Misc. Trim Pot."])

    o.drawer("r220dip", ["220 Ohm", "16-pin DIP"])
    o.drawer("r330sip", ["330 Ohm", "10-pin SIP"])
    o.drawer("r10ksip", ["10k Ohm", "10-pin SIP"])
    o.drawer("r10kdip", ["10k Ohm", "16-pin DIP"])
    o.drawer("r200trim", ["200 Ohm", "Trim Pot."])
    o.drawer("r500trim", ["500 Ohm", "Trim Pot."])
    o.drawer("r1ktrim", ["1k Ohm", "Trim Pot."])
    o.drawer("r10ktrim", ["10k Ohm", "Trim Pot."])
    o.drawer("r20ktrim", ["20k Ohm", "Trim Pot."])
    o.drawer("r25ktrim", ["25k Ohm", "Trim Pot."])
    o.drawer("r100ktrim", ["100k Ohm", "Trim Pot."])
    o.drawer("rpotknob", ["Potentiometer", "Knob"])
    o.drawer("rmisc", ["Resistors", "Misc. Values"])

    # Fuse:
    o.drawer("polyswitch_.90", [".90A Resetable", "Fuse"])

    # Robobricks:
    o.drawer("rbanalogin8", ["AnalogIn8"])
    o.drawer("rbcompass8", ["Compass8"])
    o.drawer("rbdigital8", ["Digital8"])
    o.drawer("rbdualmotor1amp", ["DualMotor1Amp"])
    o.drawer("rbiredge4", ["IREdge4"])
    o.drawer("rbirremote1", ["IRRemote1"])
    o.drawer("rblaserholder1", ["LaserHolder1"])
    o.drawer("rblcd32", ["LCD32"])
    o.drawer("rbled10", ["LED10"])
    o.drawer("rbline3", ["Line3"])
    o.drawer("rbmicrobrain8", ["MicroBrain8"])
    o.drawer("rbmultiplex8", ["Multiplex8"])
    o.drawer("rbpicbrain11", ["PICBrain11"])
    o.drawer("rbrcinput8", ["RCInput8"])
    o.drawer("rbreckon2", ["Reckon2"])
    o.drawer("rbscanpage", ["ScanPage"])
    o.drawer("rbscanpanel", ["ScanPanel"])
    o.drawer("rbsense3", ["Sense3"])
    o.drawer("rbservo4", ["Servo4"])
    o.drawer("rbservomount", ["ServoMount"])
    o.drawer("rbserial1", ["Serial1"])
    o.drawer("rbswitch8", ["Switch8"])
    o.drawer("rbtwingearsensorleft", ["Twin Gear", "Sensor Left"])
    o.drawer("rbtwingearsensorright", ["Twin Gear", "Sensor Right"])
    return o


def hardware_organizer():
    # FIXME: The orgainzer values are wrong:
    o = Organizer(name="Electronics",
      length=116.0, width=49.0, height=12.0,
      font_height=4.0, front_rows=2, labels_per_page=5)

    # #0 Hardware:
    o.drawer("hw0fm0", ["#0-80 1/8 Inch", "FH Machine Screw"])
    o.drawer("hw0fm1", ["#0-80 3/16 Inch", "FH Machine Screw"])
    o.drawer("hw0fm2", ["#0-80 1/4 Inch", "FH Machine Screw"])
    o.drawer("hw0fm3", ["#0-80 5/16 Inch", "FH Machine Screw"])
    o.drawer("hw0fm4", ["#0-80 3/8 Inch", "FH Machine Screw"])
    o.drawer("hw0fm5", ["#0-80 1/2 Inch", "FH Machine Screw"])
    o.drawer("hw0fm6", ["#0-80 5/8 Inch", "FH Machine Screw"])
    o.drawer("hw0fm7", ["#0-80 3/4 Inch", "FH Machine Screw"])
    o.drawer("hw0fm8", ["#0-80 7/8 Inch", "FH Machine Screw"])
    o.drawer("hw0fm9", ["#0-80 1 Inch", "FH Machine Screw"])

    o.drawer("hw0pm0", ["#0-80 1/8 Inch", "PH Machine Screw"])
    o.drawer("hw0pm1", ["#0-80 3/16 Inch", "PH Machine Screw"])
    o.drawer("hw0pm2", ["#0-80 1/4 Inch", "PH Machine Screw"])
    o.drawer("hw0pm3", ["#0-80 5/16 Inch", "PH Machine Screw"])
    o.drawer("hw0pm4", ["#0-80 3/8 Inch", "PH Machine Screw"])
    o.drawer("hw0pm5", ["#0-80 1/2 Inch", "PH Machine Screw"])
    o.drawer("hw0pm6", ["#0-80 5/8 Inch", "PH Machine Screw"])
    o.drawer("hw0pm7", ["#0-80 3/4 Inch", "PH Machine Screw"])
    o.drawer("hw0pm8", ["#0-80 7/8 Inch", "PH Machine Screw"])
    o.drawer("hw0pm9", ["#0-80 1 Inch", "PH Machine Screw"])

    o.drawer("hw0wsh", ["#0 Washer", ""])
    o.drawer("hw0lw", ["#0 Lock Washer", ""])
    o.drawer("hw0hn", ["#0-80", "Hex Nut"])

    # #2 Hardware
    o.drawer("hw2pm0", ["#2-56 1/8 Inch", "PH Machine Screw"])
    o.drawer("hw2pm1", ["#2-56 3/16 Inch", "PH Machine Screw"])
    o.drawer("hw2pm2", ["#2-56 1/4 Inch", "PH Machine Screw"])
    o.drawer("hw2pm3", ["#2-56 3/8 Inch", "PH Machine Screw"])
    o.drawer("hw2pm4", ["#2-56 1/2 Inch", "PH Machine Screw"])
    o.drawer("hw2pm5", ["#2-56 5/8 Inch", "PH Machine Screw"])
    o.drawer("hw2pm6", ["#2-56 3/4 Inch", "PH Machine Screw"])

    o.drawer("hw2fm0", ["#2-56 1/8 Inch", "FH Machine Screw"])
    o.drawer("hw2fm1", ["#2-56 3/16 Inch", "FH Machine Screw"])
    o.drawer("hw2fm2", ["#2-56 1/4 Inch", "FH Machine Screw"])
    o.drawer("hw2fm3", ["#2-56 3/8 Inch", "FH Machine Screw"])
    o.drawer("hw2fm4", ["#2-56 1/2 Inch", "FH Machine Screw"])
    o.drawer("hw2fm5", ["#2-56 5/8 Inch", "FH Machine Screw"])
    o.drawer("hw2fm6", ["#2-56 3/4 Inch", "FH Machine Screw"])

    o.drawer("hw2flw", ["#2 Flat/Lock", "Washer"])
    o.drawer("hw2fw", ["#2", "Flat Washer"])
    o.drawer("hw2sw", ["#2", "Split Lock Washer"])
    o.drawer("hw2lw", ["#2", "Ext. Lock Washer"])
    o.drawer("hw2hn", ["#2-56", "Hex Nut"])

    #4 Hardware:

    o.drawer("hw4pm0", ["#4-40 1/8 Inch", "PH Machine Screw"])
    o.drawer("hw4pm1", ["#4-40 3/16 Inch", "PH Machine Screw"])
    o.drawer("hw4pm2", ["#4-40 1/4 Inch", "PH Machine Screw"])
    o.drawer("hw4pm3", ["#4-40 5/16 Inch", "PH Machine Screw"])
    o.drawer("hw4pm4", ["#4-40 3/8 Inch", "PH Machine Screw"])
    o.drawer("hw4pm5", ["#4-40 1/2 Inch", "PH Machine Screw"])
    o.drawer("hw4pm6", ["#4-40 5/8 Inch", "PH Machine Screw"])
    o.drawer("hw4pm7", ["#4-40 3/4 Inch", "PH Machine Screw"])
    o.drawer("hw4pm8", ["#4-40 1 Inch", "PH Machine Screw"])
    o.drawer("hw4pm9", ["#4-40 1-1/4 Inch", "PH Machine Screw"])
    o.drawer("hw4pm10", ["#4-40 1-1/2 Inch", "PH Machine Screw"])
    o.drawer("hw4pm11", ["#4-40 2 Inch", "PH Machine Screw"])

    o.drawer("hw4fm0", ["#4-40 1/8 Inch", "FH Machine Screw"])
    o.drawer("hw4fm1", ["#4-40 3/16 Inch", "FH Machine Screw"])
    o.drawer("hw4fm2", ["#4-40 1/4 Inch", "FH Machine Screw"])
    o.drawer("hw4fm3", ["#4-40 5/16 Inch", "FH Machine Screw"])
    o.drawer("hw4fm4", ["#4-40 3/8 Inch", "FH Machine Screw"])
    o.drawer("hw4fm5", ["#4-40 1/2 Inch", "FH Machine Screw"])
    o.drawer("hw4fm6", ["#4-40 5/8 Inch", "FH Machine Screw"])
    o.drawer("hw4fm7", ["#4-40 3/4 Inch", "FH Machine Screw"])
    o.drawer("hw4fm8", ["#4-40 1 Inch", "FH Machine Screw"])
    o.drawer("hw4fm9", ["#4-40 1 1/4 Inch", "FH Machine Screw"])

    o.drawer("hw4fw1", ["#4 3/8 Inch", "FH Wood Screw"])

    o.drawer("hw4flw", ["#4 Flat/Lock", "Washers"])
    o.drawer("hw4fw", ["#4", "Flat Washer"])
    o.drawer("hw4sw", ["#4", "Split Lock Washer"])
    o.drawer("hw4lw", ["#4", "Ext. Lock Washer"])
    o.drawer("hw4hn", ["#4-40", "Hex Nut"])

    # #6 Hardware:

    o.drawer("hw6rm1", ["#6-32 1/4 Inch", "RH Machine Screw"])
    o.drawer("hw6rm2", ["#6-32 3/8 Inch", "RH Machine Screw"])
    o.drawer("hw6rm3", ["#6-32 1/2 Inch", "RH Machine Screw"])
    o.drawer("hw6rm4", ["#6-32 5/8 Inch", "RH Machine Screw"])
    o.drawer("hw6rm5", ["#6-32 3/4 Inch", "RH Machine Screw"])
    o.drawer("hw6rm6", ["#6-32 1 Inch", "RH Machine Screw"])
    o.drawer("hw6rm7", ["#6-32 1-1/4 Inch", "RH Machine Screw"])
    o.drawer("hw6rm8", ["#6-32 1-1/2 Inch", "RH Machine Screw"])
    o.drawer("hw6rm9", ["#6-32 1-3/4 Inch", "RH Machine Screw"])
    o.drawer("hw6rm10", ["#6-32 2 Inch", "RH Machine Screw"])

    o.drawer("hw6fm1", ["#6-32 1/4 Inch", "FH Machine Screw"])
    o.drawer("hw6fm2", ["#6-32 3/8 Inch", "FH Machine Screw"])
    o.drawer("hw6fm3", ["#6-32 1/2 Inch", "FH Machine Screw"])
    o.drawer("hw6fm4", ["#6-32 5/8 Inch", "FH Machine Screw"])
    o.drawer("hw6fm5", ["#6-32 3/4 Inch", "FH Machine Screw"])
    o.drawer("hw6fm6", ["#6-32 1 Inch", "FH Machine Screw"])
    o.drawer("hw6fm7", ["#6-32 1-1/4 Inch", "FH Machine Screw"])
    o.drawer("hw6fm8", ["#6-32 1-1/2 Inch", "FH Machine Screw"])
    o.drawer("hw6fm9", ["#6-32 1-3/4 Inch", "FH Machine Screw"])
    o.drawer("hw6fm10", ["#6-32 2 Inch", "FH Machine Screw"])

    o.drawer("hw6rw1", ["#6 1/4 Inch", "RH Wood Screw"])
    o.drawer("hw6rw2", ["#6 3/8 Inch", "RH Wood Screw"])
    o.drawer("hw6rw3", ["#6 1/2 Inch", "RH Wood Screw"])
    o.drawer("hw6rw4", ["#6 5/8 Inch", "RH Wood Screw"])
    o.drawer("hw6rw5", ["#6 3/4 Inch", "RH Wood Screw"])
    o.drawer("hw6rw6", ["#6 1 Inch", "RH Wood Screw"])
    o.drawer("hw6rw7", ["#6 1-1/4 Inch", "RH Wood Screw"])
    o.drawer("hw6rw8", ["#6 1-1/2 Inch", "RH Wood Screw"])
    o.drawer("hw6rw9", ["#6 1-3/4 Inch", "RH Wood Screw"])
    o.drawer("hw6rw10", ["#6 2 Inch", "RH Wood Screw"])

    o.drawer("hw6fw1", ["#6 1/4 Inch", "FH Wood Screw"])
    o.drawer("hw6fw2", ["#6 3/8 Inch", "FH Wood Screw"])
    o.drawer("hw6fw2b", ["#6 3/8 Inch", "Brass FH Wood Screw"])
    o.drawer("hw6fw3", ["#6 1/2 Inch", "FH Wood Screw"])
    o.drawer("hw6fw4", ["#6 5/8 Inch", "FH Wood Screw"])
    o.drawer("hw6fw5", ["#6 3/4 Inch", "FH Wood Screw"])
    o.drawer("hw6fw6", ["#6 1 Inch", "FH Wood Screw"])
    o.drawer("hw6fw7", ["#6 1-1/4 Inch", "FH Wood Screw"])
    o.drawer("hw6fw8", ["#6 1-1/2 Inch", "FH Wood Screw"])
    o.drawer("hw6fw9", ["#6 1-3/4 Inch", "FH Wood Screw"])
    o.drawer("hw6fw10", ["#6 2 Inch", "FH Wood Screw"])

    o.drawer("hw6hw1", ["#6 1/4 Inch", "Hex Wood Screw"])
    o.drawer("hw6hw2", ["#6 3/8 Inch", "Hex Wood Screw"])
    o.drawer("hw6hw3", ["#6 1/2 Inch", "Hex Wood Screw"])
    o.drawer("hw6hw4", ["#6 5/8 Inch", "Hex Wood Screw"])
    o.drawer("hw6hw5", ["#6 3/4 Inch", "Hex Wood Screw"])
    o.drawer("hw6hw6", ["#6 1 Inch", "Hex Wood Screw"])
    o.drawer("hw6hw7", ["#6 1-1/4 Inch", "Hex Wood Screw"])
    o.drawer("hw6hw8", ["#6 1-1/2 Inch", "Hex Wood Screw"])
    o.drawer("hw6hw9", ["#6 1-3/4 Inch", "Hex Wood Screw"])
    o.drawer("hw6hw10", ["#6 2 Inch", "Hex Wood Screw"])

    o.drawer("hw6fw", ["#6", "Flat Washer"])
    o.drawer("hw6fwb", ["#6", "Brass Flat Washer"])
    o.drawer("hw6sw", ["#6", "Split Lock Washer"])
    o.drawer("hw6lw", ["#6", "Ext. Lock Washer"])
    o.drawer("hw6hn", ["#6-32", "Hex Nut"])

    o.drawer("hw7fw1", ["#7 5/8 Inch", "FH Wood Screw"])

    # #8 Hardware:

    o.drawer("hw8rm1", ["#8-32 1/4 Inch", "RH Machine Screw"])
    o.drawer("hw8rm2", ["#8-32 3/8 Inch", "RH Machine Screw"])
    o.drawer("hw8rm3", ["#8-32 1/2 Inch", "RH Machine Screw"])
    o.drawer("hw8rm4", ["#8-32 5/8 Inch", "RH Machine Screw"])
    o.drawer("hw8rm5", ["#8-32 3/4 Inch", "RH Machine Screw"])
    o.drawer("hw8rm6", ["#8-32 1 Inch", "RH Machine Screw"])
    o.drawer("hw8rm7", ["#8-32 1-1/4 Inch", "RH Machine Screw"])
    o.drawer("hw8rm8", ["#8-32 1-1/2 Inch", "RH Machine Screw"])
    o.drawer("hw8rm9", ["#8-32 1-3/4 Inch", "RH Machine Screw"])
    o.drawer("hw8rm10", ["#8-32 2 Inch", "RH Machine Screw"])

    o.drawer("hw8fm1", ["#8-32 1/4 Inch", "FH Machine Screw"])
    o.drawer("hw8fm2", ["#8-32 3/8 Inch", "FH Machine Screw"])
    o.drawer("hw8fm3", ["#8-32 1/2 Inch", "FH Machine Screw"])
    o.drawer("hw8fm4", ["#8-32 5/8 Inch", "FH Machine Screw"])
    o.drawer("hw8fm5", ["#8-32 3/4 Inch", "FH Machine Screw"])
    o.drawer("hw8fm6", ["#8-32 1 Inch", "FH Machine Screw"])
    o.drawer("hw8fm7", ["#8-32 1-1/4 Inch", "FH Machine Screw"])
    o.drawer("hw8fm8", ["#8-32 1-1/2 Inch", "FH Machine Screw"])
    o.drawer("hw8fm9", ["#8-32 1-3/4 Inch", "FH Machine Screw"])
    o.drawer("hw8fm10", ["#8-32 2 Inch", "FH Machine Screw"])

    o.drawer("hw8rw1", ["#8 1/4 Inch", "RH Wood Screw"])
    o.drawer("hw8rw2", ["#8 3/8 Inch", "RH Wood Screw"])
    o.drawer("hw8rw3", ["#8 1/2 Inch", "RH Wood Screw"])
    o.drawer("hw8rw4", ["#8 5/8 Inch", "RH Wood Screw"])
    o.drawer("hw8rw5", ["#8 3/4 Inch", "RH Wood Screw"])
    o.drawer("hw8rw6", ["#8 1 Inch", "RH Wood Screw"])
    o.drawer("hw8rw7", ["#8 1-1/4 Inch", "RH Wood Screw"])
    o.drawer("hw8rw8", ["#8 1-1/2 Inch", "RH Wood Screw"])
    o.drawer("hw8rw9", ["#8 1-3/4 Inch", "RH Wood Screw"])
    o.drawer("hw8rw10", ["#8 2 Inch", "RH Wood Screw"])

    o.drawer("hw8fw1", ["#8 1/4 Inch", "FH Wood Screw"])
    o.drawer("hw8fw2", ["#8 3/8 Inch", "FH Wood Screw"])
    o.drawer("hw8fw3", ["#8 1/2 Inch", "FH Wood Screw"])
    o.drawer("hw8fw4", ["#8 5/8 Inch", "FH Wood Screw"])
    o.drawer("hw8fw5", ["#8 3/4 Inch", "FH Wood Screw"])
    o.drawer("hw8fw6", ["#8 1 Inch", "FH Wood Screw"])
    o.drawer("hw8fw7", ["#8 1-1/4 Inch", "FH Wood Screw"])
    o.drawer("hw8fw8", ["#8 1-1/2 Inch", "FH Wood Screw"])
    o.drawer("hw8fw9", ["#8 1-3/4 Inch", "FH Wood Screw"])
    o.drawer("hw8fw10", ["#8 2 Inch", "FH Wood Screw"])

    o.drawer("hw8hw1", ["#8 1/4 Inch", "Hex Wood Screw"])
    o.drawer("hw8hw2", ["#8 3/8 Inch", "Hex Wood Screw"])
    o.drawer("hw8hw3", ["#8 1/2 Inch", "Hex Wood Screw"])
    o.drawer("hw8hw4", ["#8 5/8 Inch", "Hex Wood Screw"])
    o.drawer("hw8hw5", ["#8 3/4 Inch", "Hex Wood Screw"])
    o.drawer("hw8hw6", ["#8 1 Inch", "Hex Wood Screw"])
    o.drawer("hw8hw7", ["#8 1-1/4 Inch", "Hex Wood Screw"])
    o.drawer("hw8hw8", ["#8 1-1/2 Inch", "Hex Wood Screw"])
    o.drawer("hw8hw9", ["#8 1-3/4 Inch", "Hex Wood Screw"])
    o.drawer("hw8hw10", ["#8 2 Inch", "Hex Wood Screw"])

    o.drawer("hw8fw", ["#8", "Flat Washer"])
    o.drawer("hw8sw", ["#8", "Split Lock Washer"])
    o.drawer("hw8lw", ["#8", "Ext. Lock Washer"])
    o.drawer("hw8hn", ["#8-32", "Hex Nut"])

    # #10 Hardware:

    o.drawer("hw10rm1", ["#10-24 1/4 Inch", "RH Machine Screw"])
    o.drawer("hw10rm2", ["#10-24 3/8 Inch", "RH Machine Screw"])
    o.drawer("hw10rm3", ["#10-24 1/2 Inch", "RH Machine Screw"])
    o.drawer("hw10rm4", ["#10-24 5/8 Inch", "RH Machine Screw"])
    o.drawer("hw10rm5", ["#10-24 3/4 Inch", "RH Machine Screw"])
    o.drawer("hw10rm6", ["#10-24 1 Inch", "RH Machine Screw"])
    o.drawer("hw10rm7", ["#10-24 1-1/4 Inch", "RH Machine Screw"])
    o.drawer("hw10rm8", ["#10-24 1-1/2 Inch", "RH Machine Screw"])
    o.drawer("hw10rm9", ["#10-24 1-3/4 Inch", "RH Machine Screw"])
    o.drawer("hw10rm10", ["#10-24 2 Inch", "RH Machine Screw"])
    o.drawer("hw10rm11", ["#10-24 2-1/2 Inch", "RH Machine Screw"])

    o.drawer("hw10fm1", ["#10-24 1/4 Inch", "FH Machine Screw"])
    o.drawer("hw10fm2", ["#10-24 3/8 Inch", "FH Machine Screw"])
    o.drawer("hw10fm3", ["#10-24 1/2 Inch", "FH Machine Screw"])
    o.drawer("hw10fm4", ["#10-24 5/8 Inch", "FH Machine Screw"])
    o.drawer("hw10fm5", ["#10-24 3/4 Inch", "FH Machine Screw"])
    o.drawer("hw10fm6", ["#10-24 1 Inch", "FH Machine Screw"])
    o.drawer("hw10fm7", ["#10-24 1-1/4 Inch", "FH Machine Screw"])
    o.drawer("hw10fm8", ["#10-24 1-1/2 Inch", "FH Machine Screw"])
    o.drawer("hw10fm9", ["#10-24 1-3/4 Inch", "FH Machine Screw"])
    o.drawer("hw10fm10", ["#10-24 2 Inch", "FH Machine Screw"])
    o.drawer("hw10fm11", ["#10-24 2-1/2 Inch", "FH Machine Screw"])

    o.drawer("hw10rw1", ["#10 1/4 Inch", "RH Wood Screw"])
    o.drawer("hw10rw2", ["#10 3/8 Inch", "RH Wood Screw"])
    o.drawer("hw10rw3", ["#10 1/2 Inch", "RH Wood Screw"])
    o.drawer("hw10rw4", ["#10 5/8 Inch", "RH Wood Screw"])
    o.drawer("hw10rw5", ["#10 3/4 Inch", "RH Wood Screw"])
    o.drawer("hw10rw6", ["#10 1 Inch", "RH Wood Screw"])
    o.drawer("hw10rw7", ["#10 1-1/4 Inch", "RH Wood Screw"])
    o.drawer("hw10rw8", ["#10 1-1/2 Inch", "RH Wood Screw"])
    o.drawer("hw10rw9", ["#10 1-3/4 Inch", "RH Wood Screw"])
    o.drawer("hw10rw10", ["#10 2 Inch", "RH Wood Screw"])
    o.drawer("hw10rw11", ["#10 2-1/2 Inch", "RH Wood Screw"])

    o.drawer("hw10fw1", ["#10 1/4 Inch", "FH Wood Screw"])
    o.drawer("hw10fw2", ["#10 3/8 Inch", "FH Wood Screw"])
    o.drawer("hw10fw3", ["#10 1/2 Inch", "FH Wood Screw"])
    o.drawer("hw10fw4", ["#10 5/8 Inch", "FH Wood Screw"])
    o.drawer("hw10fw5", ["#10 3/4 Inch", "FH Wood Screw"])
    o.drawer("hw10fw6", ["#10 1 Inch", "FH Wood Screw"])
    o.drawer("hw10fw7", ["#10 1-1/4 Inch", "FH Wood Screw"])
    o.drawer("hw10fw8", ["#10 1-1/2 Inch", "FH Wood Screw"])
    o.drawer("hw10fw9", ["#10 1-3/4 Inch", "FH Wood Screw"])
    o.drawer("hw10fw10", ["#10 2 Inch", "FH Wood Screw"])
    o.drawer("hw10fw11", ["#10 2-1/2 Inch", "FH Wood Screw"])

    o.drawer("hw10fw", ["#10", "Flat Washer"])
    o.drawer("hw10sw", ["#10", "Split Lock Washer"])
    o.drawer("hw10lw", ["#10", "Ext. Lock Washer"])
    o.drawer("hw10hn", ["#10-24", "Hex Nut"])

    # Metric hardware:

    o.drawer("hwm3", ["M3-.5", "Hardware"])

    return o

main()

