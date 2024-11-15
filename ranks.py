def goodFinder(k,d,a,kda,kp): 
    output = ""
    if (k >= 20 and d == 0):
        output += 'Incarnation'
    elif (k >= 14 and k <= 19 and d == 0):
        output +=  'Apotheosis'
    elif (k >= 8 and k <= 13 and d == 0):
        output += 'Deluxe'
    elif (k >= 5 and k <= 7 and d == 0):
        output += 'Introduction'
    elif (k == 0 and d == 0 and a >= 20):
        output += 'Ascension'
    else:
        if (k >= 10 and k <= 19 and kda >= 5):
            output += "Supreme "
        elif (k >= 20 and kda >= 5):
            output += "Ultimate "
            
        if (kda >= 5 and kda <= 9 ): 
            output +=  "Original"
        elif (kda >= 10 and kda <= 19):
            output +=  "Classic"
        elif (kda >= 20):
            output +=  "Certified Classic"
            
    return output
            
def badFinder(k,d,a,kda,kp):
    if kp == 0 and d >= 20:
        return "HOLY its a Incarnation"
    elif kp == 0 and d >= 14:
        return "An Apotheosis"
    elif kp == 0 and d >= 8:
        return "A good old Deluxe"
    elif (kp == 0 and d == 5) or (kp == 1 and d == 6):
        return "An Introduction"
    
    else:
        if d >= 20:
            if kda <= 0.2:
                return "Ultimate Certified Classic"
            elif kda <= 0.5:
                return "Ultimate Classic"
            elif kda <= 1:
                return "Ultimate Original "
            else:
                return "No official classification"

        elif d >= 14:
            if kda <= 0.2:
                return "Supreme Certified Classic"
            elif kda <= 0.5:
                return "( ͡° ͜ʖ ͡°), Supreme Classic"
            elif kda <= 1:
                return "Supreme Original"
            else:
                return "" 
        else:
            if kda <= 0.2 and kda >= 0:
                return "Certified Classic"
            elif kda <= 0.5:
                return "The one and only Classic"
            elif kda < 1:
                return "The Original"
            else:
                return "" 