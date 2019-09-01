#!/usr/bin/env python3

import sys
import math

def printUsage():
	print("SYNOPSIS\n\t./groundhog period\n\nDESCRIPTION\n\tperiod\t\tthe number of days defining a period")
	exit(0)

def errors():
	if len(sys.argv) != 2 :
		exit(84)
	if (sys.argv[1] == "-h") :
		printUsage()
	try:
		sys.argv[1] = int(sys.argv[1])
	except ValueError:
		exit(84)

def sumOfLastOnes(array, period):
	sumof = 0;
	diff = 0;
	i = 0;
	while (i < period) :
		diff = array[index - i] - array[index - i - 1]
		if diff < 0 :
			diff = 0
		sumof = sumof + diff
		i = i + 1;
	return (sumof)

def avgOfLastOnes(array, period):
	sumof = 0;
	i = 0;
	while (i < period) :
		sumof = sumof + array[i - period];
		i = i + 1;
	return(sumof / period)

def variance(array, period) :
	avg = avgOfLastOnes(array, period)
	return (avgOfLastOnes([math.pow((x - avg), 2) for x in array], period))

def deviation(array, period):
	return(math.pow(variance(array, period), 0.5))

def calcultateG(g):
	if index >= period and period > 1 :
		g = sumOfLastOnes(values, period)/ period
		if g < 0 :
			g = 0.00
		g = '{0:.2f}'.format(g)
		return(g)
	else :
		return "nan"

def calcultateR(r):
	if index >= period :
		r = (values[index] / values[index - period]) * 100 - 100
		r = '{0:.0f}'.format(r)
		return(r)
	else :
		return("nan")

def calcultateS(s):
	if index >= period - 1 :
		s = deviation(values, period)
		s = '{0:.2f}'.format(s)
	else :
		s = "nan"
	return(s)

def sumofPeriod(array, period) :
	sumof = 0;
	i = 0;
	while (i < period) :
		sumof = sumof + array[i - period];
		i = i + 1;
	return (sumof)

def checkValues(g, r, s, value):
	mobileAverage = (1 / period) * sumofPeriod(values, period)
	highBand = mobileAverage + 2 * float(s)
	lowBand = mobileAverage - 2 * float(s)
	toAdd = []
	diff = 0

	toAdd.append(value)
	try :
		diff = (value - lowBand) / (highBand - lowBand)
	except ZeroDivisionError:
		exit(84)
	if (diff > 0.5) :
		toAdd.append(1 - diff)
	else :
		toAdd.append(diff)
	weirdestValues.append(toAdd)

def didSwitchOccured():
	if r != "nan" :
		if (previousr < 0 and r > 0) :
			switch = True
		elif (previousr > 0 and r < 0) :
			switch = True
		else :
			switch = False
	else :
		switch = False
	return (switch)

try:

	errors()

	values = []

	value = 0
	period = sys.argv[1]
	g = 0
	r = 0
	previousr = r
	s = 0
	index = 0
	increasement = []
	diffSup = []
	diffInf = []
	switchCount = 0;
	weirdestValues = []
	fiveWeirdestValues = []

	while value != "STOP":

		try:
			value = input()
		except EOFError :
			exit(84)
		except KeyError :
			exit(84)

		try:
			if (value == "STOP") :
				pass
			else:
				value = float(value)
		except ValueError:
			exit(84)

		values.append(value)
		if (value == "STOP") :
			if len(values) < period :
				exit (84)
			else :
				break
		g = calcultateG(g)
		if (r != "nan") :
			previousr = int(r)
		r = calcultateR(r)
		if (r != "nan") :
			r = int(r)
		s = calcultateS(s)
		if (didSwitchOccured()) :
			print("g=", g, "\tr=", r, "%\ts=", s, "\t a switch occurs", sep='')
			switchCount = switchCount + 1
		else :
			print("g=", g, "\tr=", r, "%\ts=", s, sep='')
		index = index + 1
		if index >= period :
			checkValues(g, r, s, value)

	weirdestValues.sort(key=lambda x: x[1], reverse = False)

	print("Global tendency switched", switchCount, "times")
	if (len(weirdestValues) >= 5) :
		for x in range(0,5):
			fiveWeirdestValues.append(weirdestValues[x][0])
		print("5 weirdest values are", fiveWeirdestValues)
	else :
		exit (84)

except KeyboardInterrupt:
	exit(84)