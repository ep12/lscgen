#!/usr/bin/python3
##!/data/data/com.termux/files/usr/bin/python3.6
#^ termux only

version='0.1'
import math, sys, argparse
from collections import OrderedDict

if sys.version_info[0] < 3:
    raise "Must be using Python 3"
    exit(1)

parser=argparse.ArgumentParser()
parser.prog = "lscgen.py"
parser.description = "Convert a theme for colored ls output to ANSI colors and vice versa."

parser.add_argument("action",
					nargs=1,
					default="normal",
					type=str,
					choices=["normal", "reverse", "test", "translate", "help"],
					metavar="ACTION",
					action="store",
					help="Convert a theme to a executable output or reverse input to a config file"
					)
parser.add_argument("-i", "--input",
					nargs=1,
					default="",
					dest="input",
					type=str,
					required=False,
					metavar="FILE",
					action="store",
					help="Input file"
					)
parser.add_argument("-o", "--output",
					nargs=1,
					default="",
					dest="output",
					type=str,
					required=False,
					metavar="FILE",
					action="store",
					help="Output file"
					)
parser.add_argument("-v", "--verbose",
					default=False,
					dest="verbose",
					required=False,
					action="store_true",
					help="Output errors and warnings"
					)
parser.add_argument("-t", "--translate",
					default="default",
					dest="text",
					type=str,
					required=False,
					action="store",
					help="list of attributes to translate"
					)

args=parser.parse_args()

if len(args.action)>0 and type(args.action)==list:
	action=args.action[0]
else:
	action="normal"
	
if len(args.input)>0:
	inFile=args.input[0]
else:
	inFile=None
	
if len(args.output)>0:
	outFile=args.output[0]
else:
	outFile=None

verbose=args.verbose

text=args.text

soc='#' #          start of comment
directansi='$' #   use direct ANSIS in theme files
setuserstyle='+' # store a user-defined style

#Char between name and value
nassocOp='<-' #default: name <- value
iassocOp='->' #inversed: value -> name

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

def throwError (text:str="Error", ex:bool=True):
	if args.verbose==True:
		msg="# \x1b[31;01mERROR  \x1b[00;01m [{pn}] \x1b[00m{t}\x1b[00m\n".format(pn=parser.prog, t=text)
		sys.stderr.write(msg)
	if ex:
		exit(1)

def throwWarning (text:str="Warning"):
	if args.verbose==True:
		msg="# \x1b[33;01mWARNING\x1b[00;01m [{pn}] \x1b[00m{t}\x1b[00m\n".format(pn=parser.prog, t=text)
		sys.stderr.write(msg)

def info (text:str="Info"):
	if args.verbose==True:
		msg="# \x1b[34;01mINFO   \x1b[00;01m [{pn}] \x1b[00m{t}\x1b[00m\n".format(pn=parser.prog, t=text)
		sys.stderr.write(msg)

def readIn():
	if inFile!=None:
		try:
			f=open(inFile)
		except:
			throwError("Could not open file \"{}\" (r)".format(inFile))
		r=f.readlines()
		f.close()
		return r
	else:
		return sys.stdin.readlines()

def writeOut(value):
	if value.endswith('\n')==False: value+='\n'
	if outFile!=None:
		try:
			f=open(outFile,'w')
		except:
			throwError("Could not open file \"{}\" (w)".format(outFile))
		f.writelines(value)
		f.close()
	else:
		sys.stdout.write(value)

def similarstrings (faultykey:str, keylist:list):
	# further improovements possible (e.g. using find())
	la=len(faultykey)
	score=[]
	a,g=0.9,0.1
	pivot=0.5
	k=-(math.log((2*a*g-a)/(g-a))/(g*pivot))
	for key in keylist:
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
			if key[i]==faultykey[i]: cscore+=1
		cscore/=(ml+1)
		# csi - charactaer score importance
		csi=(a*g) / (a + (g-a)*math.exp(-1*k*g*cscore))
		sc=csi*cscore+(1-csi)*lendiff
		score.append(sc)
	maxscore=max(score)
	if maxscore>0.7:
		return keylist[score.index(maxscore)]
	else:
		throwError("No similar key found. Best match: "+keylist[score.index(maxscore)]+" with "+str(maxscore)+" points", False)
		return False

def attrsToSeq (attributes:list):
	stylestr=""
	for attr in attributes:
		if attr.strip()=='': break
		if (attr.startswith(directansi)==True):
			info("Using direct sequence \"{}\"".format(attr[1:len(attr)]))
			stylestr+=attr[1:len(attr)]+';'
		else:
			try:
				stylestr+=styles[attr.strip().lower()]+';'
			except KeyError:
				throwError("{csi}01;33m\"{attr}\"{csi}01;31m is not a valid key!".format(csi='\x1b[', attr=attr.strip().lower()), False)
				si=similarstrings(attr.strip().lower(), list(styles.keys()))
				if si!=False:
					throwError("Did you mean \"{}\"?".format(si), False)
					#throwWarning("line: {} in config file {}".format(linenum, args.theme))
	return stylestr[0:len(stylestr)-1]

def themeToVar ():
	allLines=readIn()
	lscolors=""
	for linenum in range(0,len(allLines)):
		line=allLines[linenum].strip()
		if (line.startswith(soc) == False and line.strip()!=''): #don't parse lines when not necessary
			#if len(line.split(soc))>1: info("skipping part {}".format(line.split(soc)[1]))
			line=line.split(soc)[0].strip() # we don't want comments
			stylestr=""; nsep=(line.find(nassocOp)!=-1); isep=(line.find(iassocOp)!=-1)
			if (nsep+isep==1):
				if (nsep==True):
					names=line.split(nassocOp)[0].strip().split(' '); values=line.split(nassocOp)[1].strip().split(' ')
				else:
					names=line.split(iassocOp)[1].strip().split(' '); values=line.split(iassocOp)[0].strip().split(' ')
				stylestr=attrsToSeq(values) ############################
				for name in names:
					if name.startswith(setuserstyle)==True:
						info("Adding custom style: \"{}\" {} \"{}\"".format(name[1:], nassocOp, stylestr))
						try:
							styles.update(styles.fromkeys([name[1:]], stylestr))
							#print(styles[name[1:]])
						except:
							throwError("Could not append key to dictionary!".format(csi='\x1b['))
					elif (name.startswith('*')==True): lscolors+=name.strip()+'='+stylestr+':'
					elif (name.startswith('\\')==True): lscolors+=name[1:].strip()+'='+stylestr+':'
					elif (name.startswith('.')==False): lscolors+=name.strip()+'='+stylestr+':'
					else: lscolors+='*'+name.strip()+'='+stylestr+':'
	#lscolors=lscolors[0:(len(lscolors)-1)]
	#print("LS_COLORS=\x27" + lscolors + "\x27;")
	#print("export LS_COLORS")
	return "LS_COLORS='{lsc}';\nexport LS_COLORS".format(lsc=lscolors)

def varToTheme ():
	inp=readIn()
	if len(inp)==2:
		#hopefully dircolors output
		var=inp[0][0:len(inp[0])-1]
	elif len(inp)==1:
		#maybe just the first line or even without LS_COLORS='
		var=inp[0][0:len(inp[0])-1]
	else:
		throwError("I have no idea to parse your input...")
	if var.startswith("LS_COLORS='"): var=var[11:]
	if var.endswith(":';"): var=var[0:len(var)-3]
	lines=var.split(':')
	names=[]; values=[]
	for l in lines:
		names.append(l.split('=')[0])
		values.append(l.split('=')[1])
	rvalues=[]; rnames=[]
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
					throwError("Attribute not in list!\n")
		attrstr=attrstr[0:len(attrstr)-1]
		attrs.append(attrstr)
	restored=[]
	for i in range(0, len(attrs)):
		if rnames[i].count(" ")>2:
			restored.append("{val} {i} {names}".format(names=rnames[i], val=attrs[i], i=iassocOp, n=nassocOp))
		else:
			restored.insert(0,"{names} {n} {val}".format(names=rnames[i], val=attrs[i], i=iassocOp, n=nassocOp))
	return "\n".join(restored)
	

def test():
	r=""
	attrsdone=[]
	for i in range(0,len(list(styles.keys()))):
		v=list(styles.values())[i]
		try:
			ind=attrsdone.index(v)
		except ValueError:
			n=list(styles.keys())[i]
			r+="{n}: {csi}{v}mThis is a test.{csi}00m\n".format(n=n.ljust(25, "."), v=v, csi='\x1b[')
			attrsdone.append(v)
	return r
	
def help():
	return """
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
""".format(normaldirection=nassocOp, inversedirection=iassocOp, csi='\x1b[')

if action=='normal': writeOut(themeToVar())
if action=='reverse': writeOut(varToTheme())
if action=='test': writeOut(test())
if action=='translate': writeOut(attrsToSeq(text.split(' ')))
if action=='help': writeOut(help())

exit(0)
