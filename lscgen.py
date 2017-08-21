#!/data/data/com.termux/files/usr/bin/python3.6

import math, sys, argparse

parser=argparse.ArgumentParser()
parser.add_argument("-q","--quiet", help="Don't output errors", action="store_true", default=False)
parser.add_argument("-v","--verbose", help="Be verbose", action="store_true", default=False)
parser.add_argument("theme", default='theme.cfg')
parser.description="""
{a}33;01mlscgen.py{a}00m\\n
This script generates a dircolors-like output to be processed by the shell from a human-readable config file.\n
""".format(a='\x1b\x1b[')
args=parser.parse_args()

#color attributes dictionary
styles={
'default': '00', 'normal': '00',
'bold': '01', 'bright': '01',
'faint': '02', # not widely supported
'italic': '03', # not widely supported
'underlined': '04', 'underline': '04',
'blink': '05', 'flashing': '05',
'fastblink': '06', # not widely supported
'reversed': '07', 'reverse': '07', 'image-negative': '07',
'concealed': '08', 'conceal': '08', 'hidden': '08', # not widely supported
'crossed-out': '09', # not widely supported
'font0': '10', # font stuff
'font1': '11', # .
'font2': '12', # .
'font3': '13', # .
'font4': '14', # .
'font5': '15', # .
'font6': '16', # .
'font7': '17', # .
'font8': '18', # .
'font9': '19', # font stuff
'fraktur': '20', # hardly ever supported
'not-bold': '21', 'bold-off': '21', 'underline-double': '21', # hardly supported
'normal-color': '22', 'normal-intensity': '22',
'not-italic': '23', 'not-fraktur': '23',
'not-underlined': '24', 'no-underline': '24',
'blink-off': '25', 'not-blinking': '25',
'image-positive': '27',
'reveal': '28', 'show': '28', 'conceal-off': '28',
'not-crossed-out': '29',
'black': '30',
'red': '31',
'green': '32',
'orange': '33',
'blue': '34',
'purple': '35',
'cyan': '36',
'grey': '37',
# 38: extended fg color:
# 38;5;n or
# 38;2;r;g;b
# (n,r,g,b are uint8 nums)
'normal-text-color': '39', 'normal-fg': '39',
'blackbg': '40',
'redbg': '41',
'greenbg': '42',
'orangebg': '43',
'bluebg': '44',
'purplebg': '45',
'cyanbg': '46',
'greybg': '47',
# 48: extended bg color (like 38)
'normal-background-color': '49', 'normal-bg': '49',
'framed': '51',
'encircled': '52',
'overlined': '53',
'not-framed': '54', 'not-encircled': '54',
'not-overlined': '55',

'dgrey': '90',
'lred': '91',
'lgreen': '92',
'yellow': '93',
'lblue': '94',
'lpurple': '95',
'turquoise': '96',
'white': '97',
'dgreybg': '100',
'lredbg': '101',
'lgreenbg': '102',
'yellowbg': '103',
'lbluebg': '104',
'lpurplebg': '105',
'turquoisebg': '106',
'whitebg': '107'
}

#Set a char to seperate comments from important stuff
soc='#'

directansi='$'

#Char between name and value
#default: name <- value
#inversed: value -> name
nassocOp='<-'
iassocOp='->'

lscolors=""

def similarstrings(faultykey:str, keylist:list):
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
		lendiff=1-(abs(la-lb)/la)
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

try:
	f=open(args.theme,'r')
except FileNotFoundError:
	exit(1)
allLines=f.readlines()
for line in allLines:
	line=line.strip()
	
	#don't parse lines when not necessary
	if (line.startswith(soc) == False and line.strip()!=''):
		if len(line.split(soc))>1 and args.verbose==True:
			print("skipping part {}".format(line.split(soc)[1]))
		line=line.split(soc)[0].strip() #we don't want comments
		stylestr="" #start every line from scratch
		skipline=False
		nsep=(line.find(nassocOp)!=-1)
		isep=(line.find(iassocOp)!=-1)
		if (nsep+isep==1):
			if (nsep==True):
				names=line.split(nassocOp)[0].strip().split(' ')
				values=line.split(nassocOp)[1].strip().split(' ')
			else:
				names=line.split(iassocOp)[1].strip().split(' ')
				values=line.split(iassocOp)[0].strip().split(' ')
			for attr in values:
				if (attr.startswith(directansi)==True):
					if args.verbose==True:
						sys.stderr.write("Warning: using direct sequence \""+attr[1:len(attr)]+"\"\n")
					stylestr+=attr[1:len(attr)]+';'
				else:
					try:
						stylestr+=styles[attr.strip().lower()]+';'
					except KeyError:
						if args.quiet==False:
							sys.stderr.write('# \x1b\x1b[31;01mError: \x1b\x1b[01;33m\"'+attr.strip().lower()+"\" is not a valid key!")
							si=similarstrings(attr.strip().lower(), list(styles.keys()))
							if si!=False:
								sys.stderr.write(" Did you mean \""+si+"\"?")
							sys.stderr.write("\x1b\x1b[00m\n")
						#skipline=True
			if (skipline==False):
				stylestr=stylestr[0:(len(stylestr)-1)]
				for name in names:
					if (name.startswith('*')==True):
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