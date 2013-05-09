#!/usr/bin/env python
from PIL import Image
import os, shutil

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
		preproces_set(valid_set, path, i)
		

def preproces_set(store_set, path, output):
	for file_name in os.listdir(path):
		obrazek = Image.open(path + '/' + file_name)
		obrazek.convert("RGB")
		pix = obrazek.load()
		
		store_set.append((preprocess(obrazek, pix),[output]))

def preprocess(obrazek, pix):	
	hranice = 760
	(x,y) = obrazek.size
	i = 1
	j = 1
	barva = 766
	while barva > hranice:
		if i == x-1:
			i = 1
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
		if i == 0:
			i = x-2
			j = j-1
			if j == 0:
				return
		else:
			i = i-1
		(r,g,b) = pix[i,j]
		barva = r + g + b
	dolni_bod = j
	i = 1
	j = 1
	barva = 766
	while barva > hranice:
		if j == y-1:
			j = 1
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
		if j == 0:
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
	vyska = 70
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
