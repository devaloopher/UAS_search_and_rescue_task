print("UAS Image Processing Task for Round 2 \n")

#PART 1 OF TASK

import cv2 as cv
import numpy as np

img = cv.imread('/Users/DevanshiJaiswal/Desktop/4.png')

#converting the image into HSV for better color (emergency) detection
hsvimg = cv.cvtColor(img, cv.COLOR_BGR2HSV)

#creating a mask for blue, to separate the ocean using the upper and lower boundary values for the color in hsv
lower_blue = np.array([90, 50, 50]) #hue in opencv is 0-180 and not 0-360
upper_blue = np.array([130, 255, 255])
blue_mask = cv.inRange(hsvimg, lower_blue, upper_blue)

#doing the same for green
lower_green = np.array([35, 50, 50])
upper_green = np.array([85, 255, 255])
green_mask = cv.inRange(hsvimg, lower_green, upper_green)

#creating a blank image of same dimensions as original to "paste" the masks on
maskedimg = np.zeros(img.shape, dtype='uint8')

#using the blue_mask to get the map of the blue areas and then assigning them the plain blue on the blank image
maskedimg[blue_mask>0]=[255,0,0]

#doing the same for the green areas
maskedimg[green_mask>0]=[0,255,255]

#in the final image, the land and water areas are clearly segmented with plain yellow for land and plain blue for water
cv.imshow('OUTPUT', maskedimg)
cv.waitKey(0)

#PART 2 OF TASK

import cv2 as cv
import numpy as np

img = cv.imread('/Users/DevanshiJaiswal/Desktop/4.png')

grayimg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
hsvimg = cv.cvtColor(img, cv.COLOR_BGR2HSV)
blurimg = cv.bilateralFilter(grayimg, 9, 75, 75)

#using Canny edge detection on a blurred and grayscale image
edgeimg = cv.Canny(blurimg, 50, 150) #contours are found from edges, 50 and 150 are lower and upper thresholds

# defining a function to the get the location of the casualties and the rescue pads
def get_location(contour):
    M = cv.moments(contour)             #moments are mathematical summary of a shape, describes things like area, center,spread
    if M["m00"] == 0:                   # avoids    ;     #m00 is area of contour, safety check to ensure if area is zero its not recognized.
        return (0, 0)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return (cx, cy)

def distance(c1, c2):
    return np.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)

def getCasualtydata(n):
    for padindex, details in pads.items():
        if details["capacity"] == n:
            i = 0
            for id in details["assigned"]:
                print(f"{casualties[id]["age"], casualties[id]["emergency"]}")
                i += 1
            print("Total casualties assigned: ", i)
    print('\n')

# we use findContours to detect the external edges of the shapes in the image
contours, hierarchies = cv.findContours(edgeimg, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  #RETR_EXTERNAL only outer contours not holes, CHAIN_APPROX_SIMPLE compresses pts

casualty_id = 1
casualties = {}
pad_id = 1
pads = {}

for contour in contours:
    area = cv.contourArea(contour)
    if area < 20:   #ignores small noise
        continue

    location = get_location(contour)
    perimeter = cv.arcLength(contour, True)                         #approx contour
    shape = cv.approxPolyDP(contour, 0.035 * perimeter, True)       #approxPolyDp lets us approximate a set of contours as a polygon, needs an epsilon (an error value, basically)
    edges = len(shape)
    mask = np.zeros(grayimg.shape, dtype='uint8')

    cv.drawContours(mask, [contour], -1, 255, -1)
    H, S, V, alpha = cv.mean(hsvimg, mask=mask)  #extracting the hsv values for segmentation based on emergency level

    if edges == 3:
        age = 2  # elderly
    elif edges == 4:
        age = 1  # adult
    elif edges == 10:
        age = 3  # children
    else:
        #segment and store the data for the rescue pads
        if 90 <= H <= 130:  # blue
            capacity = 4
        elif 140 <= H <= 170:  # pink
            capacity = 3
        elif S < 40 and V > 180:  # grey
            capacity = 2
        pads[pad_id] = {
            "capacity": capacity,
            "location": location
        }
        pad_id += 1
        continue

    # now we use the hsv values to assign emergency levels to the casualties, and designated capacities to the rescue pads
    if edges != 8:
        if 25 < H < 50 and S > 140:
            emergency = 2  # moderate
        elif H < 50 and S < 85:
            emergency = 3  # severe (this was a bit frustrating, since the color was very washed out)
        elif 45 < H < 70 and S < 140:
            emergency = 1  # safe
        else:
            emergency = 0

        casualties[casualty_id] = {
            "age": age,
            "emergency": emergency,
            "location": location,
            "priority score": age * emergency,
            "distances": {},
            "scores": {},
            "best pad": {}
        }
    casualty_id += 1

# all the data scanning, segmentation and storage is done
for index in casualties:
    p1 = (casualties[index]["location"])
    for padindex in pads:
        p2 = (pads[padindex]["location"])
        dist = distance(p1, p2)  #location of both the casualty and pads to calculate the distance
        casualties[index]["distances"][padindex] = dist
        score = casualties[index]["priority score"] * 100 - dist
        casualties[index]["scores"][padindex] = score
        pads[padindex]["assigned"] = []

#we now have both the priority score and the distance from each rescue pad stored along with the id of the casualty
#final score formula= priority score*100 - distance

sorted_casualties = sorted(
    casualties.items(),
    key=lambda item: max(item[1]["scores"].values()),  #this sorts casualties in descending order of their scores
    reverse=True
)
for index, details in sorted_casualties:
    sorted_scores = sorted(details["scores"].items(), key=lambda x: x[1],
                           reverse=True)  #this ranks the casualties best pad option in order
    for padindex, score in sorted_scores:
        if len(pads[padindex]["assigned"]) < pads[padindex]["capacity"]:
            pads[padindex]["assigned"].append(index)
            details["best pad"] = padindex
            break

#the casualties have now been assigned pads on the basis of emergency and distance
#outputting the data in the required format
print("Casualty details for blue pad (capacity = 4)")
getCasualtydata(4)

print("Casualty details for pink pad (capacity=3)")
getCasualtydata(3)

print("Casualty data for grey pad (capacity =2)")
getCasualtydata(2)

#PART 3 OF TASK

#for this part, we use the same pipeline as the previous to scan, segment and store casualty and rescue data

import cv2 as cv
import numpy as np

img = cv.imread('/Users/DevanshiJaiswal/Desktop/4.png')

grayimg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
hsvimg = cv.cvtColor(img, cv.COLOR_BGR2HSV)
blurimg = cv.bilateralFilter(grayimg, 9, 75, 75)

#using Canny edge detection on a blurred and grayscale image
edgeimg = cv.Canny(blurimg, 50, 150) #contours are found from edges, 50 and 150 are lower and upper thresholds

# defining a function to the get the location of the casualties and the rescue pads
def get_location(contour):
    M = cv.moments(contour)             #moments are mathematical summary of a shape, describes things like area, center,spread
    if M["m00"] == 0:                   # avoids    ;     #m00 is area of contour, safety check to ensure if area is zero its not recognized.
        return (0, 0)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return (cx, cy)

def distance(c1, c2):
    return np.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)

def getFinalscore(n):
    for padindex, details in pads.items():
        if details["capacity"] == n:
            score = 0
            for id in details["assigned"]:
                score += casualties[id]["priority score"]
    return score

# we use findContours to detect the external edges of the shapes in the image
contours, hierarchies = cv.findContours(edgeimg, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  #RETR_EXTERNAL only outer contours not holes, CHAIN_APPROX_SIMPLE compresses pts

casualty_id = 1
casualties = {}
pad_id = 1
pads = {}

for contour in contours:
    area = cv.contourArea(contour)
    if area < 20:   #ignores small noise
        continue

    location = get_location(contour)
    perimeter = cv.arcLength(contour, True)                         #approx contour
    shape = cv.approxPolyDP(contour, 0.035 * perimeter, True)       #approxPolyDp lets us approximate a set of contours as a polygon, needs an epsilon (an error value, basically)
    edges = len(shape)
    mask = np.zeros(grayimg.shape, dtype='uint8')

    cv.drawContours(mask, [contour], -1, 255, -1)
    H, S, V, alpha = cv.mean(hsvimg, mask=mask)  #extracting the hsv values for segmentation based on emergency level

    if edges == 3:
        age = 2  # elderly
    elif edges == 4:
        age = 1  # adult
    elif edges == 10:
        age = 3  # children
    else:
        #segment and store the data for the rescue pads
        if 90 <= H <= 130:  # blue
            capacity = 4
        elif 140 <= H <= 170:  # pink
            capacity = 3
        elif S < 40 and V > 180:  # grey
            capacity = 2
        pads[pad_id] = {
            "capacity": capacity,
            "location": location
        }
        pad_id += 1
        continue

    # now we use the hsv values to assign emergency levels to the casualties, and designated capacities to the rescue pads
    if edges != 8:
        if 25 < H < 50 and S > 140:
            emergency = 2  # moderate
        elif H < 50 and S < 85:
            emergency = 3  # severe (this was a bit frustrating, since the color was very washed out)
        elif 45 < H < 70 and S < 140:
            emergency = 1  # safe
        else:
            emergency = 0

        casualties[casualty_id] = {
            "age": age,
            "emergency": emergency,
            "location": location,
            "priority score": age * emergency,
            "distances": {},
            "scores": {},
            "best pad": {}
        }
    casualty_id += 1

# all the data scanning, segmentation and storage is done
for index in casualties:
    p1 = (casualties[index]["location"])
    for padindex in pads:
        p2 = (pads[padindex]["location"])
        dist = distance(p1, p2)  #location of both the casualty and pads to calculate the distance
        casualties[index]["distances"][padindex] = dist
        score = casualties[index]["priority score"] * 100 - dist
        casualties[index]["scores"][padindex] = score
        pads[padindex]["assigned"] = []

#we now have both the priority score and the distance from each rescue pad stored along with the id of the casualty
#final score formula= priority score*100 - distance

sorted_casualties = sorted(
    casualties.items(),
    key=lambda item: max(item[1]["scores"].values()),  #this sorts casualties in descending order of their scores
    reverse=True
)
for index, details in sorted_casualties:
    sorted_scores = sorted(details["scores"].items(), key=lambda x: x[1],
                           reverse=True)  #this ranks the casualties best pad option in order
    for padindex, score in sorted_scores:
        if len(pads[padindex]["assigned"]) < pads[padindex]["capacity"]:
            pads[padindex]["assigned"].append(index)
            details["best pad"] = padindex
            break
            
finalScores = [getFinalscore(4), getFinalscore(3), getFinalscore(2)]
print("Final priority scores (blue, grey, pink): ", finalScores)
print("The rescue ratio is: ", (finalScores[0] + finalScores[1] + finalScores[2]) / len(casualties))
