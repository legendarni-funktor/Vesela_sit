#!/usr/bin/env python
from PIL import Image
import os, shutil
import math

def normalize_sets():
	for path in ['training_set_img_neg', 'training_set_img_pos', 'valid_set_img_neg', 'valid_set_img_pos']:
		normalize_set(path)

def normalize_set(path):
	try:
		shutil.rmtree('tmp') #del tmp
	except: pass
	
	os.mkdir('tmp');
	for i, nazev in enumerate(os.listdir(path)):
		shutil.move(path + '/' + nazev, 'tmp/Sketch_' + str(i + 1) + '.jpg')
	shutil.rmtree(path)
	shutil.copytree('tmp',path)
	shutil.rmtree('tmp') #del tmp
	
	
def create_valid_train_preproc_sets(valid_set, train_set):
	for i, path in enumerate(['training_set_img_neg', 'training_set_img_pos']):
		preproces_set(train_set, path, i)
	for i, path in enumerate(['valid_set_img_neg', 'valid_set_img_pos']):
		preproces_set(valid_set, path, i, 8, 28)
		

def preproces_set(store_set, path, output, columns, rows):
	for file_name in os.listdir(path):
		obrazek = Image.open(path + '/' + file_name)
		obrazek.convert("RGB")
		pix = obrazek.load()
		
		#matouci, ale bude se hodit
		(x,y) = obrazek.size
		citlivost = 0.8
		
		#jdu po okraji obrazku a zastavim u prvni cervene
		
		#prvni horizontalni cara:
		p1x = 2
		p1y = 2
		(r,g,b) = pix[p1x,p1y]
		while(r<(g+b)*citlivost+10):
			p1y += 1
			(r,g,b) = pix[p1x,p1y]
			
		p2x = x-2
		p2y = 2
		(r,g,b) = pix[p2x,p2y]
		while(r<(g+b)*citlivost+10):
			p2y += 1
			(r,g,b) = pix[p2x,p2y]
		#spocitam uhel o ktery je papir otocen (pravdepodobne docela maly)
		angle = math.floor(math.atan(((p1y-p2y)*1.0)/((p1x-p2x)*1.0))*180/math.pi)
		obrazek.rotate(-angle)					#minusem si nejsem jist
		
		#znovu prvni horizontalni cara, ale tentokrat jen na jedne strane:
		p1x = 2
		p1y = 2
		(r,g,b) = pix[p1x,p1y]
		while(r<(g+b)*citlivost+10):
			p1y += 1
			(r,g,b) = pix[p1x,p1y]
		horni_bod = p1y

		#prvni vertikalni
		p1x = 2
		p1y = 2
		(r,g,b) = pix[p1x,p1y]
		while(r<(g+b)*citlivost+10):
			p1x += 1
			(r,g,b) = pix[p1x,p1y]
		levy_bod = p1x

		#posledni horizontalni
		p1x = 2
		p1y = y-2
		(r,g,b) = pix[p1x,p1y]
		while(r<(g+b)*citlivost+10):
			p1y -= 1
			(r,g,b) = pix[p1x,p1y]
		dolni_bod = l1y

		#posledni vertikalni
		p1x = x-2
		p1y = 2
		(r,g,b) = pix[p1x,p1y]
		while(r<(g+b)*citlivost+10):
			p1x -= 1
			(r,g,b) = pix[p1x,p1y]
		pravy_bod = p1x
		
		okraj = 5
		sirka_puvodni = pravy_bod - levy_bod
		vyska_puvodni = dolni_bod - horni_bod
		sirka_dilku = sirka_puvodni/columns - 1
		vyska_dilku = vyska_puvodni/rows - 1
		for i in range(columns):
			for j in range(rows):
#				for k in range(sirka_dilku):
# 					for l in range(vyska_dilku):
# 						(r,g,b) = pix[(sirka_puvodni*i)/sirka+k+levy_bod,(vyska_puvodni*j)/vyska+l+horni_bod]
# 						barva += r+g+b
# 				a = barva/(3 * sirka_dilku * vyska_dilku)
				store_set.append(cut(obrazek, pix, (sirka_dilku*i + pravy_bod + okraj, delka_dilku*j + horni_bod + okraj), (sirka_dilku*(i+1) + pravy_bod - okraj, delka_dilku*(j+1) + horni_bod - okraj), [output]))

def cut(obrazek, pix, (left,up), (x,y)):	
	hranice = 760
	
	#hledani horniho bodu 
	i = left
	j = up
	barva = 766
	while barva > hranice:
		if i == x-1:
			i = left
			j = j+1
			if j == y:
				return
		else:
			i = i+1
		(r,g,b) = pix[i,j]
		barva = r + g + b
	horni_bod = j
	i = x-2
	j = y-2
	barva = 766
	while barva > hranice:
		if i == left:
			i = x-2
			j = j-1
			if j == 0:
				return
		else:
			i = i-1
		(r,g,b) = pix[i,j]
		barva = r + g + b
	dolni_bod = j
	i = left
	j = up
	barva = 766
	while barva > hranice:
		if j == y-1:
			j = up
			i = i+1
			if i == x:
				return
		else:
			j = j+1
		(r,g,b) = pix[i,j]
		barva = r + g + b
	levy_bod = i
	i = x-2
	j = y-2
	barva = 766
	while barva > hranice:
		if j == up:
			j = y-2
			i = i-1
			if i == 0:
				return
		else:
			j = j-1
		(r,g,b) = pix[i,j]
		barva = r + g + b
	pravy_bod = i

	matice = []
	sirka_puvodni = pravy_bod - levy_bod
	vyska_puvodni = dolni_bod - horni_bod	
	sirka = 70
	vyska = 40
	sirka_dilku = sirka_puvodni/sirka + 1
	vyska_dilku = vyska_puvodni/vyska + 1
	for i in range(sirka):
		matice.append([])
		for j in range(vyska):
			barva = 0
			for k in range(sirka_dilku):
				for l in range(vyska_dilku):
					(r,g,b) = pix[(sirka_puvodni*i)/sirka+k+levy_bod,(vyska_puvodni*j)/vyska+l+horni_bod]
					barva += r+g+b
			a = barva/(3 * sirka_dilku * vyska_dilku)
			matice[i].append(a)
	
	for i in xrange(len(matice)):
		for j, n in enumerate(matice[i]):
			if n == 255:
				matice[i][j] = 0
			else:
				matice[i][j] = 1
	
	
	output_vector = []
	
	for i in xrange(len(matice)):
		output_vector.extend(matice[i])
	
	
	return output_vector
#	for i in range(x-levy_bod):
#		for j in range(y-horni_bod):
#			pix[i,j] = pix[i+levy_bod,j+horni_bod]
#	for i in range(sirka):
#		for j in range(vyska):
#			pix[i,j] = (matice[i][j],matice[i][j],matice[i][j])
#	obrazek.show()
