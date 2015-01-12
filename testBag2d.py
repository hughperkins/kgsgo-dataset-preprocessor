
import Bag2d

b = Bag2d.Bag2d(5)
b.insert((2,2))
print b
b.insert((2,3))
print b
b.erase((2,2))
print b
b.erase((2,3))
print b

b.insert((2,2))
print b
b.erase((2,2))
print b
b.insert((2,3))
print b
b.erase((2,3))
print b

