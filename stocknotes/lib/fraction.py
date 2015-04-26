
def gcd(a,b):
	""" the gcd function is used by Fraction.reduce(), but it is
	significant in it's own right"""
	return gcd_iterative(a,b)

def gcd_recursive(a,b):
	if b == 0:
		return a
	else:
		return gcd(b,a%b)

def gcd_iterative(a,b):
	while 1:
		if b==0:
			return a
		(a,b) = (b,a%b)

class Fraction:
	def __init__ (self,num=0,denom=1):
		if denom<=0:
			raise ZeroDivisionError("denominator must be greater then zero")
		self.numerator = num
		self.denominator = denom
		self.reduce()

	def toString(self):
		return "%s/%s" %(self.numerator,self.denominator)

	def __str__(self):
		return self.toString()

	def toFloat(self):
		return float(self.numerator)/self.denominator

	def mixedNumber(self):
		return (self.numerator/self.denominator,(self-Fraction(self.numerator/self.denominator)))
		
	def reduce(self):
		divisor= gcd(self.numerator,self.denominator)
		if divisor> 1:
			self.numerator = self.numerator/divisor
			self.denominator= self.denominator/divisor

	def __add__(self,fract2):
		sum = Fraction()
		sum.numerator = (self.numerator*fract2.denominator)+(fract2.numerator*self.denominator)
		sum.denominator = (self.denominator*fract2.denominator)
		if sum.numerator > 0:
			sum.reduce()
		else:
			sum.numerator = -1*sum.numerator
			sum.reduce()
			sum.numerator = -1*sum.numerator
		return sum

	def __sub__(self,fract2):
		negative= Fraction(-1*fract2.numerator,fract2.denominator)
		return self + negative

	def __mul__(self,fract2):
		product = Fraction()
		product.numerator = self.numerator*fract2.numerator
		product.denominator = self.denominator*fract2.denominator
		if product.denominator < 0:
			product.denominator = -1*product.denominator
			product.reduce()
			product.numerator = -1*product.numerator
		elif product.numerator < 0:
			product.numerator = -1*product.numerator
			product.reduce()
			product.numerator = -1*product.numerator
		else:
			product.reduce()
		return product

	def __div__(self,fract2):
		recip = Fraction(fract2.denominator,fract2.numerator)
		return self * recip

	def __iadd__(self,fract2):
		return self + fract2

	def __isub__(self,fract2):
		return self - fract2

	def __imul__(self,fract2):
		return self * fract2

	def __idiv__(self,fract2):
		return self / fract2

	def __cmp__(self,other):
		if self.numerator==other.numerator and \
		   self.denominator==other.denominator:
			return 0
		return cmp(float(self.numerator)/self.denominator,
			   float(other.numerator)/other.denominator)

one = Fraction(1,1)
