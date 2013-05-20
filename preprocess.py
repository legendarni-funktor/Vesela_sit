#!/usr/bin/env python
from PIL import Image
from matplotlib.pylab import *
import os, shutil
import math
from pylab import *
import matplotlib.pyplot as plt

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
	
	
def create_valid_train_preproc_sets(positive, negative, size):
	for i, path in enumerate(['training_set_img_neg', 'valid_set_img_neg']):
		preproces_set(negative, path, 0, 7, 25, size)
	for i, path in enumerate(['valid_set_img_pos', 'training_set_img_pos']):
		preproces_set(positive, path, 1, 7, 25, size) 
		
#@profile
def preproces_set(store_set, path, output, columns, rows, size):
	for file_name in os.listdir(path):
		obrazek = Image.open(path + '/' + file_name)
		obrazek.convert("RGB")
		pix = obrazek.load()
		
		#matouci, ale bude se hodit
		(x,y) = obrazek.size
		citlivost = 0.5
		
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
		obrazek.rotate(angle)					#minusem si nejsem jist
		
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
		dolni_bod = p1y

		#posledni vertikalni
		p1x = x-2
		p1y = 2
		(r,g,b) = pix[p1x,p1y]
		while(r<(g+b)*citlivost+10):
			p1x -= 1
			(r,g,b) = pix[p1x,p1y]
		pravy_bod = p1x
		
		okraj = 30
		okraj = (obrazek.size[0] * okraj)/7000
		
 		sirka_puvodni = pravy_bod - levy_bod
 		vyska_puvodni = dolni_bod - horni_bod
 		sirka_dilku = sirka_puvodni/columns
 		vyska_dilku = vyska_puvodni/rows
 		for i in xrange(columns):
 			for j in xrange(rows):
 				left = sirka_puvodni*i/columns + levy_bod + okraj
 				#up = vyska_dilku*j + horni_bod + okraj
 				up = vyska_puvodni*j/rows + horni_bod + okraj
 				#x = sirka_dilku*(i+1) + levy_bod - okraj
 				x = sirka_puvodni*(i+1)/columns + levy_bod - okraj
 				#y = vyska_dilku*(j+1) + horni_bod - okraj
 				y = vyska_puvodni*(j+1)/rows + horni_bod - okraj
 				orez = cut(obrazek, pix, (left, up), (x, y), size)
 				if orez:
 					store_set.append((orez, (output,)))
	

		
# 		for k in range(x):
# 			pix[k, horni_bod] = (0,255,0)				
		obrazek.show()
#@profile
def cut(obrazek, pix, (left,up), (x,y), size):	
	hranice = 760
	left = left + (x - left)/10
	x = x - (x - left)/10
	citlivost_r = 290
	citlivost_b = 180
	citlivost = 0.05
	horni_bod = up
	dolni_bod = y
	levy_bod = left
	pravy_bod = x
	
	mezisoucet = 0
	first_while = True
	stored_blue = {}
	stored_red = {}
	while float(mezisoucet)/((pravy_bod-levy_bod)*(dolni_bod-horni_bod)) < citlivost:
		mezisoucet = 0	
		for i in xrange(levy_bod, pravy_bod):
			for j in xrange(horni_bod,dolni_bod):
 				(r,g,b) = pix[i,j]
 				
 				if first_while: # v prvnim cyklu se bluness a red... ulozi do slovniku a dale uz se budou z nej jen volat - je to rychlejsi
 					stored_blue[(i, j,)] = blueness(pix, i, j)
 					stored_red[(i, j,)] = redness(pix, i, j)
 					r += stored_red[(i, j,)]
 				 	b += stored_blue[(i, j,)]
 				else:
					r += stored_red[(i, j,)]
 				 	b += stored_blue[(i, j,)]			
				if (b>citlivost_b and r<citlivost_r):
					mezisoucet += 1
					
		citlivost_r += 10
		citlivost_b -= 10
		first_while = False
	citlivost_r -= 10
	citlivost_b += 10
	
	#hledani horniho bodu 
	i = levy_bod
	j = horni_bod
	(r,g,b) = pix[i,j]
	r += redness(pix, i, j)
	b += blueness(pix, i, j)
	while (b<citlivost_b or r>citlivost_r):
		if i == pravy_bod - 1:
			i = levy_bod
			j = j+1
			if j == dolni_bod:
 				print "prazdny obrazek"
				return False
		else:
			i = i+1
		(r,g,b) = pix[i,j]
		r += redness(pix, i, j)
		b += blueness(pix, i, j)
	horni_bod = j
	
	#hledani dolniho bodu
	i = pravy_bod - 2
	j = dolni_bod - 2
	(r,g,b) = pix[i,j]
	r += redness(pix, i, j)
	b += blueness(pix, i, j)
	while b<citlivost_b or r>citlivost_r:
		if i == levy_bod:
			i = pravy_bod - 2
			j = j - 1
			if j == horni_bod:
 				print "prazdny obrazek"
				return False
		else:
			i = i-1
		(r,g,b) = pix[i,j]
		r += redness(pix, i, j)
		b += blueness(pix, i, j)
	dolni_bod = j
	
	#hledani leveho bodu
	i = levy_bod
	j = horni_bod
	(r,g,b) = pix[i,j]
	r += redness(pix, i, j)
	b += blueness(pix, i, j)
	while b<citlivost_b or r>citlivost_r:
		if j == dolni_bod - 1:
			j = horni_bod
			i = i+1
			if i == pravy_bod:
 				print "prazdny obrazek"
				return False
		else:
			j = j+1
		(r,g,b) = pix[i,j]
		r += redness(pix, i, j)
		b += blueness(pix, i, j)
	levy_bod = i
	
	#hledani praveho bodu
	i = pravy_bod - 2
	j = dolni_bod - 2
	(r,g,b) = pix[i,j]
	r += redness(pix, i, j)
	b += blueness(pix, i, j)
	while b<citlivost_b or r>citlivost_r:
		if j == horni_bod:
			j = dolni_bod - 2
			i = i - 1
			if i == levy_bod:
 				print "prazdny obrazek"
				return False
		else:
			j = j-1
		(r,g,b) = pix[i,j]
		r += redness(pix, i, j)
		b += blueness(pix, i, j)
	pravy_bod = i
		
	matice = []
	sirka_puvodni = pravy_bod - levy_bod
	vyska_puvodni = dolni_bod - horni_bod	
	sirka = size[0]
	vyska = size[1]
	sirka_dilku = sirka_puvodni/sirka + 1
	vyska_dilku = vyska_puvodni/vyska + 1
	for i in range(sirka):
		matice.append([])
		for j in range(vyska):
			barva = 0
			for k in range(sirka_dilku):
				for l in range(vyska_dilku):
					(r,g,b) = pix[(sirka_puvodni*i)/sirka+k+levy_bod,(vyska_puvodni*j)/vyska+l+horni_bod]
					barva += r
			a = barva/(sirka_dilku * vyska_dilku)
			matice[i].append(a)
	
# 	#vykresleni bodu v ramci citlivosti zelelne
# 	for k in xrange(levy_bod,pravy_bod):
# 		for l in xrange(horni_bod, dolni_bod):
# 			(r,g,b) = pix[k,l]
# 			r += redness(pix, k, l)
# 			b += blueness(pix, k, l)
# 			if (b>citlivost_b and r<citlivost_r):
# 				pix[k,l] = (r,0,b)
	
 	#zeleny obdelnicek pro debug
  	for i in xrange(levy_bod, pravy_bod):
  		pix[i,horni_bod] = (0, 255, 0)
  		pix[i,dolni_bod] = (0, 255, 0)
  	for i in xrange(horni_bod, dolni_bod):
  		pix[pravy_bod,i] = (0, 255, 0)
  		pix[levy_bod,i] = (0, 255, 0)	
	
	#prepsani matice na cernobilou
	for i in xrange(len(matice)):
		for j, n in enumerate(matice[i]):
			if n > 220:
				matice[i][j] = 0
			else:
				matice[i][j] = 1
	
	
	output_vector = []
	
 	for i in xrange(len(matice)):
 		output_vector.extend(matice[i])
 	
 	#vykresleni matice
# 	arr = zeros((len(matice[0]), len(matice)))
# 	for i in xrange(len(matice[0])):
# 		for j in xrange(len(matice)):
# 			arr[i][j] = matice[j][i]
#	matshow(arr)
#	show()
 	
	return output_vector
#@profile
def redness(pix, i, j):
	return (pix[i,j][0] + pix[i+1,j][0] + pix[i+1,j+1][0] + pix[i,j+1][0] +\
			pix[i-1,j+1][0] + pix[i-1,j][0] + pix[i-1,j-1][0] + pix[i,j-1][0] + pix[i+1,j-1][0])/9
#@profile
def blueness(pix, i, j):
	return  (pix[i,j][2] + pix[i+1,j][2] + pix[i+1,j+1][2] + pix[i,j+1][2] +\
			 pix[i-1,j+1][2] + pix[i-1,j][2] + pix[i-1,j-1][2] + pix[i,j-1][2] + pix[i+1,j-1][2])/9
