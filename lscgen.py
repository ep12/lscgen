#!/data/data/com.termux/files/usr/bin/python3.6

#color attributes dictionary
styles={
'default': '00', 'normal': '00',
'bold': '01', 'bright': '00',
'underlined': '04',
'flashing': '05',
'reversed': '07', 'inverted': '07',
'concealed': '08',
'black': '30',
'red': '31',
'green': '32',
'orange': '33',
'blue': '34',
'purple': '35',
'cyan': '36',
'grey': '37',
'blackbg': '40',
'redbg': '41',
'greenbg': '42',
'orangebg': '43',
'bluebg': '44',
'purplebg': '45',
'cyanbg': '46',
'greybg': '47',
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

#Char between name and value
#default: name <- value
#inversed: value -> name
nassocOp='<-'
iassocOp='->'

lscolors=""

f=open('theme.cfg','r')
allLines=f.readlines()
for line in allLines:
	line=line.strip() #don't parse lines when not necessary
	if (line.startswith(soc) == False):
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
				try:
					stylestr+=styles[attr.strip().lower()]+';'
				except KeyError:
					print("Error: \""+attr.strip().lower()+"\" is not a valid key!")
					print("I will skip this line.")
					skipline=True
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
lscolors=lscolors[0:(len(lscolors)-1)]
print("LS_COLORS='" + lscolors + "'")
print("export LS_COLORS")
f.close()