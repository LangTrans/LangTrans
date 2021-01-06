from yaml import load,SafeLoader
from re import compile as comp,MULTILINE,sub
def extract(spattern):
	fdict=dict()
	pt=dict()
	cat=[]
	for name,value in spattern.items():
		if name[0]=="_":
			value['tokens']=spattern[name[2:]]['tokens']
		pt.update({name:comp(value['regex'],MULTILINE)})
		eachline=dict()
		replas=dict()
		for w in value['tokens']:
			if w in value:
				if 'eachline' in value[w]:
					eachline.update({w:value[w]['eachline']})
				if 'replace' in value[w]:
					replas.update({w:[(comp(q[0]),q[1]) if 1<len(q) else (comp(q[0]),"") for q in value[w]['replace']]})
		fdict.update({name:[eachline,replas]})
		cat.append(value['tokens'])
	return fdict,pt,cat
def matching(patterns,cats,content):
	matches = dict()
	fullmatch = dict()
	for (name,pattern),cat in zip(patterns.items(),cats):
		fullmatch[name]=[i.group() for i in pattern.finditer(content)]
		if len(cat)==1:
			matches[name]=[{c:mat} for mat,c in zip(pattern.findall(content),cat)]
			continue
		matches[name]=[{c:i for i,c in zip(mat,cat)} for mat in pattern.findall(content)]
	return matches,fullmatch
def main(content,exlocation,plocation):
	spattern = load(open(exlocation).read(),Loader=SafeLoader)#Source
	tpattern = load(open(plocation).read(),Loader=SafeLoader)#Target
	loop=False
	lmit=7
	if 'settings' in spattern:
		settings=spattern['settings']
		if 'loop' in settings:
			loop=settings['loop']
		if 'looplimit' in settings:
			lmit=settings['looplimit']
		if 'variables' in settings:
			var = settings['variables']
			for k,v in spattern.items():
				if k!="settings":
					r =  v['regex']
					for n,rg in var.items():
						if "<"+n+">" in r:
							r=r.replace("<"+n+">",rg)
					spattern[k]['regex']=r
		del spattern['settings']
	fdict,pt,cats=extract(spattern);del spattern
	count=0
	while 1:
		matches,fullmatch = matching(pt,cats,content)
		if not any(len(i)!=0 for i in fullmatch.values()):
			break
		for i in matches:
			forline,replacer=fdict[i]
			if i[0]!="_":
				rp=tpattern[i]
			else:
				rp=tpattern[i[2:]]
			for j,f in zip(matches[i],fullmatch[i]):
				rpn=rp
				for k,v in j.items():
					if k in forline:
						line=forline[k]
						v="\n".join([line.replace("<line>",l) for l in v.split("\n") if l.strip()!=""])
					if k in replacer:
						for rval in replacer[k]:
							v=sub(*rval,v)
					rpn=rpn.replace(f"<{k}>",v)
				content=content.replace(f,rpn)
		count+=1
		if not loop or count==lmit:
			break
	return content