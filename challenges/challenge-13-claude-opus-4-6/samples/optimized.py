# Generate Fibonacci
f=[1,1]
for _ in range(14):f+=[f[-2]+f[-1]]
# Generate primes
p=[]
for n in range(2,102):
 if all(n%d for d in range(2,n)):p+=[n]
# Build lines
L=["The Fibonacci sequence begins: "+", ".join(map(str,f))+".",
"Pi to 50 decimal places is 3.14159265358979323846264338327950288419716939937510.",
"The first 26 prime numbers are: "+", ".join(map(str,p))+".",
"In chess, the starting position has 32 pieces: 16 white and 16 black.",
"Each side begins with 1 king, 1 queen, 2 rooks, 2 bishops, 2 knights, and 8 pawns.",
"The chemical formula for glucose is C6H12O6 and for ethanol is C2H5OH.",
"Water boils at 100 degrees Celsius (212 degrees Fahrenheit) at standard atmospheric pressure.",
"The speed of light in a vacuum is approximately 299,792,458 meters per second.",
"Earth orbits the Sun at an average distance of about 149,597,870.7 kilometers.",
"A haiku has three lines with 5, 7, and 5 syllables respectively.",
'The word "typewriter" can be typed using only the top row of a QWERTY keyboard.',
"Buffalo buffalo Buffalo buffalo buffalo buffalo Buffalo buffalo."]
print("\n".join(L))
