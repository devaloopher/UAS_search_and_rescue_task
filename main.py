print("UAS Image Processing Task for Round 2 \n")

#processing criteria

#adding dictionaries
age_score = {"children_stars" : 3, "elderly_triangle" : 2, "adults_square" : 1}
severity_score = {"severe_red" : 3, "mild_yellow" : 2, "safe_green" : 1}
# dictionary for 1 person while list for multiple people(casualties)
casualties = [{"age" : "children_stars", "severity" : "severe_red"}, {"age" : "adults_square", "severity" : "safe_green"}]

# calculation priority score defining function
def priority_score(casualty):
  return age_score[casualty["age"]] * severity_score[casualty["severity"]]
for casualty in casualties:
  casualty["priority"] = priority_score(casualty)
print(casualties)

# sorting cuz different casualties have different priorities and higher priority casualty needs to be assigned to camps first.
## Return a new sorted list from the items in iterable. Has two optional arguments which must be specified as keyword arguments. key specifies a function of one argument that is used to extract a comparison key from each element in iterable (for example, key=str.lower). The default value is None (compare the elements directly). reverse is a boolean value.
## using sorted instead of .sort cuz sorted() is a function and we need original data in the future and .sort() modifies the list in place so list is lost.

casualties_sorted = sorted(casualties, key=lambda x: x["priority"], reverse=True)   # sorting acc to priority  # reverse=True we use cuz sorting gives ascending order and we want highest priority first so reverse is used.
print("\nSorted Casualties:")
for a in casualties_sorted:
    print(a)

# now assigning casualties to different camps - camps can have limited casualties and the camps need to remember who has alr been assigned
# setting up a dict for camps which will again contain another dict of capacity and if they've been assigned which is an empty list

camps = {"blue" : {"capacity" : 4, "assigned" : []}, "pink" : {"capacity" : 3, "assigned" : []}, "grey" : {"capacity" : 2, "assigned" : []}}

########### 26 jan and 27 jan ##############
import cv2 as cv
import numpy as np

img = cv.imread('/Users/DevanshiJaiswal/Desktop/1.png')

#emergency(colour) detection
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

#age(shape) detection
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
blur = cv.GaussianBlur(gray, (7,7), 1.5)   #to reduce noise- (5,5) is kernel size
edge = cv.Canny(blur, 50, 150)     #edge detection - contours are found from edges, 50 and 150 are lower and upper thresholds

contour, _ = cv.findContours(edge, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)     #to find contour, RETR_EXTERNAL only outer contours not holes, CHAIN_APPROX_SIMPLE compresses pts

for cnt in contour:
    area = cv.contourArea(cnt)
    if area < 1:                            #ignore small noise
        continue
    perimeter = cv.arcLength(cnt, True)       #approx contour
    circularity = 4 * np.pi * area / (perimeter * perimeter)    #to identify circles

    shape = "unknown"

    if circularity > 0.88:       #to ensure that every shapes which looks like a circle is identified as circle
        shape = "camp"

    else:
        epsilon = 0.03 * cv.arcLength(cnt, True)
        approx = cv.approxPolyDP(cnt, epsilon, True)
        vertices = len(approx)

        if vertices == 3:
            shape = ("Triangle")

        elif vertices == 4:
            x, y, w, h = cv.boundingRect(approx)
            aspect_ratio = float(w) / h
            if 0.95 <= aspect_ratio <= 1.05:       #to eliminate unevenness
                shape = "square"
            else:
                shape = "rectangle"

        elif 8 <= vertices <= 12:
            shape = "star"

    cv.drawContours(img, [cnt], -1, (0, 255, 0), 2)      #to outline the shape
    # Find contour center and put text
    M = cv.moments(cnt)        #moments are mathematical summary of a shape, describes things like area, center,spread
    if M["m00"] != 0:          #m00 is area of contour, safety check to ensure if area is zero its not recognized.
        cX = int(M["m10"] / M["m00"])     #entroid
        cY = int(M["m01"] / M["m00"])
        cv.putText(img, shape, (cX, cY), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)



cv.imshow('Image ', img)
cv.waitKey(0)
cv.destroyAllWindows()
