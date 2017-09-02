#!/usr/bin/python3
##!/data/data/com.termux/files/usr/bin/python3.6
#^ termux only
#^ normal environment

version='0.1'
import math, sys, argparse
from collections import OrderedDict

if sys.version_info[0] < 3:
    raise "Must be using Python 3"
    exit(1)

#NEEDS TO BE REVIEWED AND IMPROOVED!
parser=argparse.ArgumentParser()

# -a ACTION:
#   normal (default)
#   reverse
#   test
#   translate
#   help (color / syntax help)

# -v: verbose (default: quiet)
# -i: Info
# -c: color help
# -i INPUT (theme)
# -o OUTPUT

outputctrl = parser.add_mutually_exclusive_group()
infoopt = parser.add_mutually_exclusive_group()
reverseopt = infoopt.add_argument_group()

infoopt.add_argument("-t", "--theme", nargs=1 , help="Specify a theme. Default is \"theme.cfg\".", action="store", default='theme.cfg')

outputctrl.add_argument("-q","--quiet", help="Don't output errors", action="store_true", default=False)
outputctrl.add_argument("-v","--verbose", help="Be verbose", action="store_true", default=False)

infoopt.add_argument("--version", help="Show version", action="store_true", default=False)
infoopt.add_argument("-c", "--colors", "--color-help", dest="colors", action="store_true", default=False, help="Show available colors and syntax") 
infoopt.add_argument("--test", help="Test your terminal. Usually not every control code is working properly", action="store_true", default=False) # not yet implemented
infoopt.add_argument("-r","--reverse", help="Reverse the output to get a theme file", action="store_true", default=False)
infoopt.add_argument("-a", "--ansi", help="Translate a string to a sequence", action="store", default=False, nargs=1)

reverseopt.add_argument("-o", "--output", action="store", nargs=1, help="Output the theme file")
reverseopt.add_argument("-i", "--input", action="store", nargs=1, help="File to reverse, if none given, I read from stdin until Ctrl-D")

parser.description="""
{a}33;01mlscgen.py{a}00m
This script generates a dircolors-like output to be processed by the shell from a human-readable config file.
""".format(a='\x1b[')

args=parser.parse_args()

#color attributes dictionary
styles=OrderedDict([
('default', '00'), ('normal', '00'),
('bold', '01'), ('bright', '01'),
('faint', '02'), # not widely supported
('italic', '03'), # not widely supported
('underlined', '04'), ('underline', '04'),
('blink', '05'), ('flashing', '05'),
('fastblink', '06'), # not widely supported
('reversed', '07'), ('reverse', '07'), ('image-negative', '07'),
('concealed', '08'), ('conceal', '08'), ('hidden', '08'), # not widely supported
('crossed-out', '09'), # not widely supported
('font0', '10'), # font stuff
('font1', '11'), # .
('font2', '12'), # .
('font3', '13'), # .
('font4', '14'), # .
('font5', '15'), # .
('font6', '16'), # .
('font7', '17'), # .
('font8', '18'), # .
('font9', '19'), # font stuff
('fraktur', '20'), # hardly ever supported
('not-bold', '21'), ('bold-off', '21'), ('underline-double', '21'), # hardly supported
('normal-color', '22'), ('normal-intensity', '22'),
('not-italic', '23'), ('not-fraktur', '23'),
('not-underlined', '24'), ('no-underline', '24'),
('blink-off', '25'), ('not-blinking', '25'),
('image-positive', '27'),
('reveal', '28'), ('show', '28'), ('conceal-off', '28'),
('not-crossed-out', '29'),
('black', '30'),
('red', '31'),
('green', '32'),
('orange', '33'),
('blue', '34'),
('purple', '35'),
('cyan', '36'),
('grey', '37'),
# 38: extended fg color:
# 38;5;n or
# 38;2;r;g;b
# (n,r,g,b are uint8 nums)
('normal-text-color', '39'), ('normal-fg', '39'),
('blackbg', '40'),
('redbg', '41'),
('greenbg', '42'),
('orangebg', '43'),
('bluebg', '44'),
('purplebg', '45'),
('cyanbg', '46'),
('greybg', '47'),
# 48: extended bg color (like 38)
('normal-background-color', '49'), ('normal-bg', '49'),
('framed', '51'),
('encircled', '52'),
('overlined', '53'),
('not-framed', '54'), ('not-encircled', '54'),
('not-overlined', '55'),
('dgrey', '90'),
('lred', '91'),
('lgreen', '92'),
('yellow', '93'),
('lblue', '94'),
('lpurple', '95'),
('turquoise', '96'),
('white', '97'),
('dgreybg', '100'),
('lredbg', '101'),
('lgreenbg', '102'),
('yellowbg', '103'),
('lbluebg', '104'),
('lpurplebg', '105'),
('turquoisebg', '106'),
('whitebg', '107')
])

#Set a char to seperate comments from important stuff
soc='#'

directansi='$'
setuserstyle='+'

#Char between name and value
#default: name <- value
#inversed: value -> name
nassocOp='<-'
iassocOp='->'

lscolors=""

#why is this not working?
def similarstrings (faultykey:str, keylist:list):
	# further improovements possible (e.g. using find())
	la=len(faultykey)
	score=[]
	a=0.9
	g=0.1
	pivot=0.5
	k=-(math.log((2*a*g-a)/(g-a))/(g*pivot))
	for key in keylist:
		#print(key)
		cscore=0
		lb=len(key)
		try:
			lendiff=1-(abs(la-lb)/la)
		except ZeroDivisionError:
			return False
		if la>lb:
			ml=lb
		else:
			ml=la
		for i in range(0,ml):
			if key[i]==faultykey[i]:
				cscore+=1
		cscore/=(ml+1)
		# csi - charactaer score importance
		csi=(a*g) / (a + (g-a)*math.exp(-1*k*g*cscore))
		sc=csi*cscore+(1-csi)*lendiff
		#print(key.ljust(25,'.')+':\t'+str(sc).strip()+'\t('+str(cscore).strip()+'*'+str(csi).strip()+' + ' +str(lendiff).strip()+'*'+str(1-csi).strip())
		score.append(sc)
	maxscore=max(score)
	if maxscore>0.75:
		return keylist[score.index(maxscore)]
		#return score.index(maxscore)
	else:
		print("nothing found. best match:"+keylist[score.index(maxscore)]+" with "+str(maxscore)+" points")
		return False

def attrToSeq (attributes:list):
	stylestr=""
	for attr in attributes:
		if (attr.startswith(directansi)==True):
			if args.verbose==True:
				sys.stderr.write("Warning: using direct sequence \""+attr[1:len(attr)]+"\"\n")
			stylestr+=attr[1:len(attr)]+';'
		else:
			try:
				stylestr+=styles[attr.strip().lower()]+';'
			except KeyError:
				if args.quiet==False:
					sys.stderr.write("# {csi}31;01mError: {csi}01;33m\"{attr}\" is not a valid key!".format(csi='\x1b[', attr=attr.strip().lower()))
					si=similarstrings(attr.strip().lower(), list(styles.keys()))
					if si!=False:
						sys.stderr.write(" Did you mean \""+si+"\"?")
					sys.stderr.write("\x1b[00m\n")
					#sys.stderr.write("line: {} in config file {}".format(linenum, args.theme))
				#skipline=True
	return stylestr

def themeToVar ():
	if type(args.theme)==list:
		try:
			f=open(args.theme[0],'r')
		except FileNotFoundError:
			sys.stderr.write("# {csi}31;01mError: {csi}33;01mFile not found!{csi}00m\n".format('\x1b['))
			exit(1)
		if args.verbose==True:
			print("Opening theme file\"{}\"".format(args.theme[0]))
	else:
		try:
			f=open(args.theme,'r')
		except FileNotFoundError:
			sys.stderr.write("# {sci}31;01mError: {csi}33;01mFile not found!{csi}00m\n".format('\x1b['))
			exit(1)
		if args.verbose==True:
			print("Opening theme file\"{}\"".format(args.theme))
	lscolors=""
	allLines=f.readlines()
	for linenum in range(0,len(allLines)):
		line=allLines[linenum].strip()
		#don't parse lines when not necessary
		if (line.startswith(soc) == False and line.strip()!=''):
			if len(line.split(soc))>1 and args.verbose==True:
				print("skipping part {}".format(line.split(soc)[1]))
			line=line.split(soc)[0].strip() #we don't want comments
			stylestr=""
			nsep=(line.find(nassocOp)!=-1)
			isep=(line.find(iassocOp)!=-1)
			if (nsep+isep==1):
				if (nsep==True):
					names=line.split(nassocOp)[0].strip().split(' ')
					values=line.split(nassocOp)[1].strip().split(' ')
				else:
					names=line.split(iassocOp)[1].strip().split(' ')
					values=line.split(iassocOp)[0].strip().split(' ')
				stylestr=attrToSeq(values)
				stylestr=stylestr[0:(len(stylestr)-1)]
				for name in names:
					if name.startswith(setuserstyle)==True:
						if args.verbose==True:
							print("Adding custom style: \"{}\" with \"{}\"".format(name[1:len(name)], stylestr))
							#print(styles)
							try:
								print(styles[name[1:len(name)]])
							except:
								sys.stderr.write("# {csi}31;01mError:{csi}33;01m Could not append key to dictionary!{csi}00m\n".format(csi='\x1b['))
						styles.update(styles.fromkeys([name[1:len(name)]], stylestr))
					elif (name.startswith('*')==True):
						lscolors+=name.strip()+'='+stylestr+':'
					elif (name.startswith('\\')==True):
						lscolors+=name[1:len(name)].strip()+'='+stylestr+':'
					elif (name.startswith('.')==False):
						lscolors+=name.strip()+'='+stylestr+':'
					else:
						lscolors+='*'+name.strip()+'='+stylestr+':'
		elif args.verbose==True:
			print("skipping line {}".format(line))
	lscolors=lscolors[0:(len(lscolors)-1)]
	print("LS_COLORS=\x27" + lscolors + "\x27;")
	print("export LS_COLORS")
	f.close()
	return "LS_COLORS='{lsc}';\;export LS_COLORS".format(lsc=lscolors)

def varToTheme ():
	if args.input==None:
		inp=sys.stdin.readlines()
	else:
		if type(args.input)==list:
			try:
				f=open(args.input[0],'r')
			except FileNotFoundError:
				sys.stderr.write("# {csi}31;01mError: {csi}33;01mFile not found!{csi}00m\n".format('\x1b['))
				exit(1)
			if args.verbose==True:
				print("Opening var file\"{}\"".format(args.input[0]))
		else:
			try:
				f=open(args.input,'r')
			except FileNotFoundError:
				sys.stderr.write("# {sci}31;01mError: {csi}33;01mFile not found!{csi}00m\n".format('\x1b['))
				exit(1)
			if args.verbose==True:
				print("Opening var file\"{}\"".format(args.input))
		inp=f.readlines()
		f.close()
	if len(inp)==2:
		#hopefully dircolors output
		var=inp[0][0:len(inp[0])-1]
	elif len(inp)==1:
		#maybe just the first line or even without LS_COLORS='
		var=inp[0][0:len(inp[0])-1]
	else:
		print("I have no idea to parse your input...")
		exit(1)
	if var.startswith("LS_COLORS='"):
		var=var[11:]
	if var.endswith(":';"):
		var=var[0:len(var)-3]
	lines=var.split(':')
	names=[]
	values=[]
	for l in lines:
		names.append(l.split('=')[0])
		values.append(l.split('=')[1])
	rvalues=[]
	rnames=[]
	ind=0
	for i in range(0, len(values)):
		v=values[i]
		try:
			ind=rvalues.index(v)
			rnames[ind]+=" "+names[i]
		except ValueError:
			#not in rvalues array
			rvalues.append(v)
			rnames.append(names[i])
	if args.verbose==True:
		print(rnames)
		print()
		print(rvalues)
	attrs=[]
	for attrl in rvalues:
		attr=attrl.split(';')
		attrstr=""
		for a in attr:
			try:
				attrstr+=list(styles.keys())[list(styles.values()).index(a)]+" "
			except ValueError:
				try:
					attrstr+=list(styles.keys())[list(styles.values()).index('0'+a)]+" "
				except ValueError:
					#not in list!
					if args.quiet==False:
						sys.stderr.write("# {sci}31;01mError: {csi}33;01mAttribute not in list!{csi}00m\n".format('\x1b['))
		attrstr=attrstr[0:len(attrstr)-1]
		attrs.append(attrstr)
	restored=[]
	for i in range(0, len(attrs)):
		if rnames[i].count(" ")>2:
			restored.append("{val} {i} {names}".format(names=rnames[i], val=attrs[i], i=iassocOp, n=nassocOp))
		else:
			restored.insert(0,"{names} {n} {val}".format(names=rnames[i], val=attrs[i], i=iassocOp, n=nassocOp))
	if args.output==None:
		for l in restored:
			print(l)
	else:
		if type(args.output)==list:
			try:
				f=open(args.output[0],'w')
			except FileNotFoundError:
				sys.stderr.write("# {csi}31;01mError: {csi}33;01mFile not found!{csi}00m\n".format('\x1b['))
				exit(1)
			if args.verbose==True:
				print("Opening var file\"{}\"".format(args.output[0]))
		else:
			try:
				f=open(args.output,'w')
			except FileNotFoundError:
				sys.stderr.write("# {sci}31;01mError: {csi}33;01mFile not found!{csi}00m\n".format('\x1b['))
				exit(1)
			if args.verbose==True:
				print("Opening var file\"{}\"".format(args.output))
		try:
			f.writelines(line+'\n' for line in restored)
			f.close()
		except:
			f.close()
			if args.quiet==False:
				sys.stderr.write("# {sci}31;01mError: {csi}33;01mFile not writable!{csi}00m\n".format('\x1b['))
				exit(1)
	return 
	
if  args.reverse==True:
	varToTheme()
	exit(0)

if args.test==True:
	attrsdone=[]
	for i in range(0,len(list(styles.keys()))):
		v=list(styles.values())[i]
		try:
			ind=attrsdone.index(v)
		except ValueError:
			n=list(styles.keys())[i]
			print("{n}: {csi}{v}mThis is a test.{csi}00m".format(n=n.ljust(25, "."), v=v, csi='\x1b['))
			attrsdone.append(v)
	exit(0)
	
if args.version==True:
	print("You are running version {} of lscgen.py".format(version))
	exit(0)

if args.colors==True:
	print("""
{csi}107;30;05mBASIC SYNTAX{csi}00m:
name name name {normaldirection} value value value # comment
value value value {inversedirection} name name name # comment

{csi}107;30;05mADVANCED SYNTAX{csi}00m:
+userstyle {normaldirection} $directansi
	+userstyle: add the color attributributes to the dictionary for reusing styles (groups)
	$directansi: for direct use like $38;2;255;255;255 or $48;5;28
	 {csi}33;01mWARNING:{csi}00m The script does not perform checks: if it doesn't work, check your directs!

{csi}107;30;05mCOLORS{csi}00m:
black	dgrey	red	green	orange	blue	purple	cyan	
white	grey	lred	lgreen	yellow	lblue	lpurple	turquoise
{csi}107;30;05mBACKGROUND COLORS{csi}00m:
append "bg" to every color above to make it color the background.

{csi}107;30;05mTEXT ATTRIBUTES:{csi}00m
NOTE: This script is a converter. If the terminal doesn't support special styles, don't blame the script!
font0	font1	font2	font3	font4	font5	font6	font7	font8	font9
default			bold/bright		faint		italic
underline(d)		blink/flashing		fastblink	reverse(d)/image-negative
conceal/hidden		crossed-out		fraktur		image-positive
framed			encircled		overlined	not-framed/not-encircled
not-overlined		
not-bold/bold-off/underline-double		normal-color/normal-intensity
not-underlined/no-underline			blink-off/not-blinking
reveal/show/conceal-off				not-crossed-out	
""".format(normaldirection=nassocOp, inversedirection=iassocOp, csi='\x1b['))
	exit(0)
	
defaultconvert=themeToVar()
exit(0)
