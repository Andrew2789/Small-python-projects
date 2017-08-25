"""
   Convex Hull Assignment: COSC262 (2017)
   Student Name: Andrew Davidson
   Usercode: ada130
"""

def theta(p1, p2, ambiguousIs0):
	"""Returns an approximation of the angle between the line 
		  through p1 and p2, and a horizontal line through p1.
		  ambiguousIs0 specifies whether the ambiguous case 
		  should evaluate to 0 or to 360.
	"""
	dx = p2[0] - p1[0]
	dy = p2[1] - p1[1]

	if abs(dx) < 1e-6 and abs(dy) < 1e-6:
		t = 0
	else:
		t = dy/(abs(dx) + abs(dy))

	if dx < 0:
		t = 2 - t
	elif dy < 0:
		t = 4 + t
	elif dy == 0:
		if ambiguousIs0 == True:
			t = 0
		else:
			t = 4

	return t*90

def lineFn(ptA, ptB, ptC):
	return (
	(ptB[0]-ptA[0])*(ptC[1]-ptA[1]) -
	(ptB[1]-ptA[1])*(ptC[0]-ptA[0]) )

def rightmostLowestIndex(listPts):
	"""Returns the index of the lowest point from
		  the input point list, ties are broken by
		  choosing the rightmost tied point.
	"""
	index = 0 
	for i in range(len(listPts)):
		if listPts[i][1] < listPts[index][1] or (listPts[i][1] == listPts[index][1] and listPts[i][0] > listPts[index][0]):
			index = i
	return index

def distanceBetween(p1, p2):
	"""Returns the distance between points p1 and p2.
	"""
	return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5

def readDataPts(filename, N):
	"""Reads the first N lines of data from the input file
		  and returns a list of N tuples
		  [(x0,y0), (x1, y1), ...]
	"""
	with open(filename, "r") as f:
		listPts = [tuple([float(x) for x in f.readline().split()]) for i in range(N)]

	return listPts

def giftwrap(listPts):
	"""Returns the convex hull vertices computed using the
		  giftwrap algorithm as a list of 'h' tuples
		  [(u0,v0), (u1,v1), ...]    
	"""
	#copy the input list to avoid modifying the main program's list
	localListPts = listPts[:]

	#set start to index of rightmost point of minimum y value
	startIndex = rightmostLowestIndex(localListPts)
	localListPts.append(localListPts[startIndex])

	hullSize = 0
	endPoint = len(localListPts)-1
	lastAngle = 0

	while endPoint != startIndex:
		#swap the next hull point into position
		localListPts[hullSize], localListPts[endPoint] = localListPts[endPoint], localListPts[hullSize]
		#if the start point was swapped to another position, update startIndex
		if hullSize == startIndex:
			startIndex = endPoint

		minAngle = 361
		for pointIndex in range(hullSize+1, len(localListPts)):
			angle = theta(localListPts[hullSize], localListPts[pointIndex], False)
			if angle > lastAngle and localListPts[pointIndex] != localListPts[hullSize]:
				if angle < minAngle:
					minAngle = angle
					endPoint = pointIndex
				#handle collinear hull points
				elif angle == minAngle and distanceBetween(localListPts[hullSize], localListPts[pointIndex]) > \
										   distanceBetween(localListPts[hullSize], localListPts[endPoint]):
					minAngle = angle
					endPoint = pointIndex


		hullSize += 1
		lastAngle = minAngle

	return localListPts[:hullSize]

def grahamscan(listPts):
	"""Returns the convex hull vertices computed using the
		 Graham-scan algorithm as a list of 'h' tuples
		 [(u0,v0), (u1,v1), ...]  
	"""
	#copy the input list to avoid modifying the main program's list
	localListPts = listPts[:]

	#order the points by angle from rightmost lowest (maple leaf)
	p0 = localListPts[rightmostLowestIndex(localListPts)]
	localListPts.sort(key=lambda pt: theta(p0, pt, True))

	#move the first 3 items to a stack
	stack = localListPts[:3]
	
	for i in range(3, len(localListPts)):
		#pop from the stack until the top two items and the next point make a counter-clockwise turn
		while not lineFn(stack[-2], stack[-1], localListPts[i]) > 1e-6:
			stack.pop()
		stack.append(localListPts[i])

	return stack

def quickhull(listPts):
	"""Returns the convex hull vertices computed using 
		  a third algorithm - quickhull
	"""
	#find the points of a line from the leftmost to the rightmost point
	leftmost, rightmost = min(listPts, key=lambda pt: pt[0]), max(listPts, key=lambda pt: pt[0])

	#seperate the points cw and ccw of the line
	cwPts, ccwPts = set(), set()
	for pt in listPts:
		direction = lineFn(leftmost, rightmost, pt)
		if direction < 0:
			cwPts.add(pt)
		elif direction > 0:
			ccwPts.add(pt)

	#find the two halves of the hull
	return findHull(cwPts, leftmost, rightmost) + findHull(ccwPts, rightmost, leftmost)

def findHull(setPts, linePt1, linePt2):
	"""Recursive function to find the convex hull 
		  of a section of the points
	"""
	#base case when there are no points in the set to be checked
	if len(setPts) == 0:
		return [linePt1]

	#find the next point on the convex hull - the point with max distance from linePt1 and linePt2
	newPt = max(setPts, key=lambda pt: linePtDistance(linePt1, linePt2, pt))

	#seperate points outside the newly formed triangle (linePt1. linePt2, newPt) into those cw and ccw
	cwPts, ccwPts = set(), set()
	for pt in setPts:
		if lineFn(linePt1, newPt, pt) < 0:
			cwPts.add(pt)
		elif lineFn(linePt2, newPt, pt) > 0:
			ccwPts.add(pt)

	#find the next points on the hull and return them
	return findHull(cwPts, linePt1, newPt) + findHull(ccwPts, newPt, linePt2)

def linePtDistance(linePt1, linePt2, pt):
	"""Find the orthogonal distance from the line 
		  (linePt1, linePt2) and pt
	"""
	#find a, b, and c for line equation ax + by + c = 0
	a = linePt1[1] - linePt2[1]
	b = linePt2[0] - linePt1[0]
	c = linePt1[0]*linePt2[1] - linePt2[0]*linePt1[1]

	#return distance from the line to pt
	return abs(a*pt[0] + b*pt[1] + c)/(a**2 + b**2)**0.5

def main():
	listPts = readDataPts('Set_A.dat', 1000)

	giftWrapped = giftwrap(listPts)
	grahamScanned = grahamscan(listPts)
	quickHulled = quickhull(listPts)

	print(giftWrapped)
	print(grahamScanned)
	print(quickHulled)
 
if __name__  ==  "__main__":
	main()
  